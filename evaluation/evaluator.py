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
    Performs Page-by-Page granular breakdown and exports versioned evaluation .txt reports.
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
        """
        Performs a granular Page-by-Page comparison analysis.
        """
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

    def export_versioned_txt_report(self, output_txt_path: str) -> str:
        page_metrics = self.evaluate_page_count()
        text_metrics = self.evaluate_text_content()
        spatial_metrics = self.evaluate_spatial_placement()
        image_metrics = self.evaluate_image_placement()
        page_by_page = self.evaluate_page_by_page()

        overall_fidelity = (
            (text_metrics["text_sequence_similarity_pct"] * 0.40) +
            (spatial_metrics["mean_spatial_iou_pct"] * 0.25) +
            (image_metrics["image_retention_rate_pct"] * 0.20) +
            (page_metrics["page_density_score"] * 0.15)
        )

        lines = [
            "=======================================================================\n",
            "      QUANTITATIVE & SCIENTIFIC PAGE-BY-PAGE RECONSTRUCTION REPORT     \n",
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
