import os
import sys
import json
import difflib
import datetime
import numpy as np
import pymupdf as fitz

class QuantitativePDFEvaluator:
    """
    Scientific quantitative evaluation engine comparing Original Input PDF vs. Recreated Output PDF.
    Measures 5 core scientific metrics:
    1. Page Density & Count Ratio (%)
    2. Text Content Match & Retention Rate (%)
    3. Spatial Bounding Box Intersection-Over-Union / Placement Accuracy (IoU %)
    4. Image & Figure Placement Retention Rate (%)
    5. Granular Paragraph & Picture Displacement Metrics (Delta Page, Delta X pt, Delta Y pt, Delta Width pt, Delta Height pt)
    """

    def __init__(self, orig_pdf_path: str, rec_pdf_path: str):
        self.orig_pdf_path = orig_pdf_path
        self.rec_pdf_path = rec_pdf_path
        
        self.orig_doc = fitz.open(orig_pdf_path)
        self.rec_doc = fitz.open(rec_pdf_path)

    def evaluate_page_count(self) -> dict:
        orig_pages = len(self.orig_doc)
        rec_pages = len(self.rec_doc)
        page_diff = abs(rec_pages - orig_pages)
        page_diff_pct = (page_diff / float(orig_pages)) * 100.0
        page_match_score = max(0.0, 100.0 - page_diff_pct)

        return {
            "original_pages": orig_pages,
            "recreated_pages": rec_pages,
            "page_difference": page_diff,
            "page_difference_percentage": round(page_diff_pct, 2),
            "page_density_score": round(page_match_score, 2)
        }

    def evaluate_text_content(self) -> dict:
        orig_text = ""
        for p in self.orig_doc:
            orig_text += p.get_text("text") + "\n"

        rec_text = ""
        for p in self.rec_doc:
            rec_text += p.get_text("text") + "\n"

        orig_words = len(orig_text.split())
        rec_words = len(rec_text.split())

        seq = difflib.SequenceMatcher(None, orig_text, rec_text)
        similarity_ratio = seq.ratio() * 100.0

        word_retention_rate = (min(rec_words, orig_words) / float(max(1, orig_words))) * 100.0

        return {
            "original_word_count": orig_words,
            "recreated_word_count": rec_words,
            "word_count_difference": abs(rec_words - orig_words),
            "text_sequence_similarity_pct": round(similarity_ratio, 2),
            "word_retention_rate_pct": round(word_retention_rate, 2)
        }

    def _compute_iou(self, boxA: list, boxB: list) -> float:
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        interArea = max(0.0, xB - xA) * max(0.0, yB - yA)
        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

        unionArea = boxAArea + boxBArea - interArea
        if unionArea <= 0:
            return 0.0
        return interArea / float(unionArea)

    def evaluate_spatial_placement(self) -> dict:
        iou_scores = []
        min_pages = min(len(self.orig_doc), len(self.rec_doc))

        for p_idx in range(min_pages):
            orig_page = self.orig_doc[p_idx]
            rec_page = self.rec_doc[p_idx]

            orig_blocks = [b["bbox"] for b in orig_page.get_text("dict")["blocks"] if b.get("type") == 0]
            rec_blocks = [b["bbox"] for b in rec_page.get_text("dict")["blocks"] if b.get("type") == 0]

            for ob in orig_blocks:
                best_iou = 0.0
                for rb in rec_blocks:
                    iou = self._compute_iou(ob, rb)
                    if iou > best_iou:
                        best_iou = iou
                iou_scores.append(best_iou)

        mean_spatial_iou = float(np.mean(iou_scores)) * 100.0 if iou_scores else 0.0

        return {
            "evaluated_page_pairs": min_pages,
            "total_spatial_text_blocks_evaluated": len(iou_scores),
            "mean_spatial_iou_pct": round(mean_spatial_iou, 2)
        }

    def evaluate_image_placement(self) -> dict:
        orig_img_count = 0
        for p in self.orig_doc:
            orig_img_count += len(p.get_image_info())

        rec_img_count = 0
        for p in self.rec_doc:
            rec_img_count += len(p.get_image_info())

        img_retention_rate = (min(rec_img_count, orig_img_count) / float(max(1, orig_img_count))) * 100.0

        return {
            "original_pdf_images_count": orig_img_count,
            "recreated_pdf_images_count": rec_img_count,
            "image_count_difference": abs(rec_img_count - orig_img_count),
            "image_retention_rate_pct": round(img_retention_rate, 2)
        }

    def evaluate_page_by_page(self) -> list:
        page_analysis = []
        max_pages = max(len(self.orig_doc), len(self.rec_doc))

        for p_num in range(max_pages):
            orig_has_page = p_num < len(self.orig_doc)
            rec_has_page = p_num < len(self.rec_doc)

            orig_words = 0
            rec_words = 0
            orig_imgs = 0
            rec_imgs = 0
            page_match_ratio = 0.0
            page_iou = 0.0

            if orig_has_page:
                orig_page = self.orig_doc[p_num]
                orig_text = orig_page.get_text("text")
                orig_words = len(orig_text.split())
                orig_imgs = len(orig_page.get_image_info())

            if rec_has_page:
                rec_page = self.rec_doc[p_num]
                rec_text = rec_page.get_text("text")
                rec_words = len(rec_text.split())
                rec_imgs = len(rec_page.get_image_info())

            if orig_has_page and rec_has_page:
                seq = difflib.SequenceMatcher(None, orig_text, rec_text)
                page_match_ratio = seq.ratio() * 100.0

                orig_blocks = [b["bbox"] for b in orig_page.get_text("dict")["blocks"] if b.get("type") == 0]
                rec_blocks = [b["bbox"] for b in rec_page.get_text("dict")["blocks"] if b.get("type") == 0]

                iou_list = []
                for ob in orig_blocks:
                    best_iou = 0.0
                    for rb in rec_blocks:
                        iou = self._compute_iou(ob, rb)
                        if iou > best_iou:
                            best_iou = iou
                    iou_list.append(best_iou)
                page_iou = float(np.mean(iou_list)) * 100.0 if iou_list else 0.0

                if page_match_ratio > 85.0 and abs(orig_words - rec_words) < 15:
                    status = "EXCELLENT_MATCH"
                elif page_match_ratio > 50.0:
                    status = "MODERATE_ALIGNMENT"
                else:
                    status = "LAYOUT_SHIFTED"

            elif orig_has_page and not rec_has_page:
                status = "ORIGINAL_PAGE_OMITTED"
            else:
                status = "EXTRA_RECREATED_PAGE"

            page_analysis.append({
                "page_number": p_num + 1,
                "orig_words": orig_words,
                "rec_words": rec_words,
                "word_delta": abs(rec_words - orig_words),
                "text_match_pct": round(page_match_ratio, 2),
                "orig_images": orig_imgs,
                "rec_images": rec_imgs,
                "image_delta": abs(rec_imgs - orig_imgs),
                "page_spatial_iou_pct": round(page_iou, 2),
                "alignment_status": status
            })

        return page_analysis

    def evaluate_paragraph_displacements(self) -> list:
        """
        Calculates exact paragraph displacement metrics (Delta Page, Delta X pt, Delta Y pt).
        """
        displacements = []
        rec_paragraphs = []

        # Index all paragraphs in recreated document
        for p_idx in range(len(self.rec_doc)):
            page = self.rec_doc[p_idx]
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:
                if b.get("type") == 0:
                    t = "".join(span["text"] for line in b["lines"] for span in line["spans"]).strip()
                    if len(t) > 15:
                        rec_paragraphs.append({
                            "page": p_idx + 1,
                            "bbox": b["bbox"],
                            "x0": round(b["bbox"][0], 1),
                            "y0": round(b["bbox"][1], 1),
                            "text": t
                        })

        # Compare against original paragraphs
        for p_idx in range(len(self.orig_doc)):
            page = self.orig_doc[p_idx]
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:
                if b.get("type") == 0:
                    orig_t = "".join(span["text"] for line in b["lines"] for span in line["spans"]).strip()
                    if len(orig_t) > 15:
                        orig_x0 = round(b["bbox"][0], 1)
                        orig_y0 = round(b["bbox"][1], 1)
                        orig_p = p_idx + 1

                        # Find best text match in recreated document
                        best_match = None
                        best_sim = 0.0
                        for rp in rec_paragraphs:
                            sim = difflib.SequenceMatcher(None, orig_t[:60], rp["text"][:60]).ratio()
                            if sim > best_sim:
                                best_sim = sim
                                best_match = rp

                        if best_match and best_sim > 0.60:
                            rec_p = best_match["page"]
                            rec_x0 = best_match["x0"]
                            rec_y0 = best_match["y0"]

                            delta_page = rec_p - orig_p
                            delta_x = round(rec_x0 - orig_x0, 1)
                            delta_y = round(rec_y0 - orig_y0, 1)

                            displacements.append({
                                "orig_page": orig_p,
                                "rec_page": rec_p,
                                "delta_page": delta_page,
                                "orig_x0": orig_x0,
                                "rec_x0": rec_x0,
                                "delta_x_pt": delta_x,
                                "orig_y0": orig_y0,
                                "rec_y0": rec_y0,
                                "delta_y_pt": delta_y,
                                "match_similarity": round(best_sim * 100.0, 1),
                                "snippet": orig_t[:55].replace('\n', ' ') + "..."
                            })

        return displacements

    def evaluate_picture_displacements(self) -> list:
        """
        Calculates exact picture/image displacement metrics (Delta Page, Delta Y pt, Delta Width pt, Delta Height pt).
        """
        pic_displacements = []
        rec_images = []

        # Index all images in recreated document
        for p_idx in range(len(self.rec_doc)):
            page = self.rec_doc[p_idx]
            info = page.get_image_info()
            for idx, img in enumerate(info):
                bbox = [round(v, 1) for v in img["bbox"]]
                w = round(bbox[2] - bbox[0], 1)
                h = round(bbox[3] - bbox[1], 1)
                if w > 15 and h > 15:
                    rec_images.append({
                        "page": p_idx + 1,
                        "bbox": bbox,
                        "x0": bbox[0],
                        "y0": bbox[1],
                        "width": w,
                        "height": h
                    })

        # Compare against original document images
        for p_idx in range(len(self.orig_doc)):
            page = self.orig_doc[p_idx]
            info = page.get_image_info()
            for idx, img in enumerate(info):
                bbox = [round(v, 1) for v in img["bbox"]]
                w = round(bbox[2] - bbox[0], 1)
                h = round(bbox[3] - bbox[1], 1)
                
                # Filter out small watermark dots
                if w > 20 and h > 20 and (w * h) / (page.rect.width * page.rect.height) <= 0.35:
                    orig_p = p_idx + 1
                    orig_x0 = bbox[0]
                    orig_y0 = bbox[1]

                    # Find closest image in recreated PDF
                    best_match = None
                    best_dist = 9999.0
                    for ri in rec_images:
                        dist = abs(ri["width"] - w) + abs(ri["height"] - h)
                        if dist < best_dist:
                            best_dist = dist
                            best_match = ri

                    if best_match and best_dist < 80.0:
                        rec_p = best_match["page"]
                        rec_x0 = best_match["x0"]
                        rec_y0 = best_match["y0"]
                        rec_w = best_match["width"]
                        rec_h = best_match["height"]

                        delta_page = rec_p - orig_p
                        delta_x = round(rec_x0 - orig_x0, 1)
                        delta_y = round(rec_y0 - orig_y0, 1)
                        delta_w = round(rec_w - w, 1)
                        delta_h = round(rec_h - h, 1)

                        pic_displacements.append({
                            "orig_page": orig_p,
                            "rec_page": rec_p,
                            "delta_page": delta_page,
                            "orig_bbox": [orig_x0, orig_y0, round(orig_x0 + w, 1), round(orig_y0 + h, 1)],
                            "rec_bbox": [rec_x0, rec_y0, round(rec_x0 + rec_w, 1), round(rec_y0 + rec_h, 1)],
                            "delta_x_pt": delta_x,
                            "delta_y_pt": delta_y,
                            "orig_width_pt": w,
                            "rec_width_pt": rec_w,
                            "delta_width_pt": delta_w,
                            "orig_height_pt": h,
                            "rec_height_pt": rec_h,
                            "delta_height_pt": delta_h
                        })

        return pic_displacements

    def export_versioned_txt_report(self, output_txt_path: str) -> str:
        page_metrics = self.evaluate_page_count()
        text_metrics = self.evaluate_text_content()
        spatial_metrics = self.evaluate_spatial_placement()
        image_metrics = self.evaluate_image_placement()
        page_by_page = self.evaluate_page_by_page()
        para_displacements = self.evaluate_paragraph_displacements()
        pic_displacements = self.evaluate_picture_displacements()

        overall_fidelity = (
            (text_metrics["text_sequence_similarity_pct"] * 0.40) +
            (spatial_metrics["mean_spatial_iou_pct"] * 0.25) +
            (image_metrics["image_retention_rate_pct"] * 0.20) +
            (page_metrics["page_density_score"] * 0.15)
        )

        lines = [
            "=======================================================================\n",
            "   QUANTITATIVE & SCIENTIFIC PAGE-BY-PAGE & ELEMENT DISPLACEMENT REPORT  \n",
            "=======================================================================\n",
            f"Original Document:  {os.path.basename(self.orig_pdf_path)}\n",
            f"Recreated Document: {os.path.basename(self.rec_pdf_path)}\n",
            f"Evaluation Date:   {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "-----------------------------------------------------------------------\n",
            f"COMPOSITE RECONSTRUCTION FIDELITY INDEX: {round(overall_fidelity, 2)}%\n\n",
            "=== 1. EXECUTIVE METRIC SUMMARY ===\n",
            f"  - Total Pages (Orig / Rec):  {page_metrics['original_pages']} / {page_metrics['recreated_pages']} (Delta: {page_metrics['page_difference_percentage']}%)\n",
            f"  - Total Words (Orig / Rec):  {text_metrics['original_word_count']} / {text_metrics['recreated_word_count']} (Retention: {text_metrics['word_retention_rate_pct']}%)\n",
            f"  - Text Sequence Match %:     {text_metrics['text_sequence_similarity_pct']}%\n",
            f"  - Mean Spatial IoU %:        {spatial_metrics['mean_spatial_iou_pct']}%\n",
            f"  - Total Images (Orig / Rec): {image_metrics['original_pdf_images_count']} / {image_metrics['recreated_pdf_images_count']} (Retention: {image_metrics['image_retention_rate_pct']}%)\n\n",
            "=== 2. PAGE-BY-PAGE GRANULAR BREAKDOWN ===\n",
            f"{'Page':<6} | {'Words (O/R)':<12} | {'Text Match %':<12} | {'Images (O/R)':<12} | {'Page IoU %':<10} | {'Status':<20}\n",
            "-" * 82 + "\n"
        ]

        for p in page_by_page:
            words_str = f"{p['orig_words']} / {p['rec_words']}"
            imgs_str = f"{p['orig_images']} / {p['rec_images']}"
            lines.append(f"{p['page_number']:<6} | {words_str:<12} | {p['text_match_pct']:<12.2f}% | {imgs_str:<12} | {p['page_spatial_iou_pct']:<10.2f}% | {p['alignment_status']:<20}\n")

        lines.append("\n=== 3. GRANULAR PARAGRAPH DISPLACEMENT METRICS LOG ===\n")
        lines.append(f"{'Orig Pg':<8} | {'Rec Pg':<8} | {'ΔPage':<6} | {'Orig y0':<8} | {'Rec y0':<8} | {'Δy (pt)':<10} | {'Content Snippet':<45}\n")
        lines.append("-" * 100 + "\n")
        
        for pd in para_displacements[:30]:  # Log top 30 paragraph shifts
            lines.append(f"{pd['orig_page']:<8} | {pd['rec_page']:<8} | {pd['delta_page']:<+6} | {pd['orig_y0']:<8.1f} | {pd['rec_y0']:<8.1f} | {pd['delta_y_pt']:<+10.1f} | {pd['snippet']:<45}\n")

        lines.append("\n=== 4. GRANULAR PICTURE / IMAGE PLACEMENT DISPLACEMENT LOG ===\n")
        lines.append(f"{'Orig Pg':<8} | {'Rec Pg':<8} | {'ΔPage':<6} | {'Δy (pt)':<10} | {'Orig WxH (pt)':<16} | {'Rec WxH (pt)':<16} | {'ΔWidth (pt)':<12}\n")
        lines.append("-" * 88 + "\n")

        for pic in pic_displacements[:20]:  # Log picture shifts
            orig_dim = f"{pic['orig_width_pt']}x{pic['orig_height_pt']}"
            rec_dim = f"{pic['rec_width_pt']}x{pic['rec_height_pt']}"
            lines.append(f"{pic['orig_page']:<8} | {pic['rec_page']:<8} | {pic['delta_page']:<+6} | {pic['delta_y_pt']:<+10.1f} | {orig_dim:<16} | {rec_dim:<16} | {pic['delta_width_pt']:<+12.1f}\n")

        lines.append("=======================================================================\n")

        os.makedirs(os.path.dirname(output_txt_path), exist_ok=True)
        with open(output_txt_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        print(f"[Versioned TXT Evaluation Report Saved] {output_txt_path}")
        return output_txt_path

    def close(self):
        self.orig_doc.close()
        self.rec_doc.close()

if __name__ == "__main__":
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    orig_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(PROJECT_ROOT, "testing_doc", "kemh102.pdf")
    rec_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(PROJECT_ROOT, "output", "pdf_files", "reconstructed_kemh102_latest.pdf")

    evaluator = QuantitativePDFEvaluator(orig_path, rec_path)
    
    eval_dir = os.path.join(PROJECT_ROOT, "output", "evaluations")
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    doc_stem = os.path.splitext(os.path.basename(orig_path))[0]
    
    out_txt = os.path.join(eval_dir, f"eval_report_{doc_stem}_{timestamp_str}.txt")
    latest_txt = os.path.join(eval_dir, f"eval_report_{doc_stem}_latest.txt")
    
    evaluator.export_versioned_txt_report(out_txt)
    evaluator.export_versioned_txt_report(latest_txt)
    evaluator.close()
