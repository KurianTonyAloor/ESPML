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
    5. Overall Composite Document Reconstruction Score (0.0 - 100.0%)
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

    def run_scientific_evaluation(self, output_report_json: str = None) -> dict:
        page_metrics = self.evaluate_page_count()
        text_metrics = self.evaluate_text_content()
        spatial_metrics = self.evaluate_spatial_placement()
        image_metrics = self.evaluate_image_placement()

        # Weighted Composite Reconstruction Fidelity Index (0.0% - 100.0%)
        # Weights: Text Match (40%), Spatial IoU (25%), Image Retention (20%), Page Density (15%)
        overall_fidelity_score = (
            (text_metrics["text_sequence_similarity_pct"] * 0.40) +
            (spatial_metrics["mean_spatial_iou_pct"] * 0.25) +
            (image_metrics["image_retention_rate_pct"] * 0.20) +
            (page_metrics["page_density_score"] * 0.15)
        )

        results = {
            "evaluation_timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "original_pdf": os.path.basename(self.orig_pdf_path),
            "recreated_pdf": os.path.basename(self.rec_pdf_path),
            "composite_reconstruction_fidelity_score_pct": round(overall_fidelity_score, 2),
            "metrics": {
                "page_count_analysis": page_metrics,
                "text_content_analysis": text_metrics,
                "spatial_placement_analysis": spatial_metrics,
                "image_placement_analysis": image_metrics
            }
        }

        if output_report_json:
            os.makedirs(os.path.dirname(output_report_json), exist_ok=True)
            with open(output_report_json, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
            print(f"[Quantitative Report Saved] {output_report_json}")

        return results

    def close(self):
        self.orig_doc.close()
        self.rec_doc.close()

if __name__ == "__main__":
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    orig_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(PROJECT_ROOT, "testing_doc", "kemh102.pdf")
    rec_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(PROJECT_ROOT, "output", "pdf_files", "reconstructed_kemh102_latest.pdf")

    evaluator = QuantitativePDFEvaluator(orig_path, rec_path)
    results = evaluator.run_scientific_evaluation()

    print("\n=======================================================================")
    print("      QUANTITATIVE & SCIENTIFIC RECONSTRUCTION EVALUATION REPORT       ")
    print("=======================================================================")
    print(f"Original PDF:  {results['original_pdf']}")
    print(f"Recreated PDF: {results['recreated_pdf']}")
    print(f"Timestamp:     {results['evaluation_timestamp']}")
    print("-----------------------------------------------------------------------")
    print(f"OVERALL RECONSTRUCTION FIDELITY SCORE:  {results['composite_reconstruction_fidelity_score_pct']}%\n")

    p_m = results['metrics']['page_count_analysis']
    print(f"1. PAGE COUNT DENSITY:")
    print(f"   - Original Pages:   {p_m['original_pages']}")
    print(f"   - Recreated Pages:  {p_m['recreated_pages']}")
    print(f"   - Page Delta %:     {p_m['page_difference_percentage']}%")
    print(f"   - Page Density Score:{p_m['page_density_score']}%\n")

    t_m = results['metrics']['text_content_analysis']
    print(f"2. TEXT CONTENT ACCURACY:")
    print(f"   - Original Words:   {t_m['original_word_count']}")
    print(f"   - Recreated Words:  {t_m['recreated_word_count']}")
    print(f"   - Sequence Match:   {t_m['text_sequence_similarity_pct']}%")
    print(f"   - Word Retention:   {t_m['word_retention_rate_pct']}%\n")

    s_m = results['metrics']['spatial_placement_analysis']
    print(f"3. SPATIAL PLACEMENT (IoU):")
    print(f"   - Evaluated Blocks: {s_m['total_spatial_text_blocks_evaluated']}")
    print(f"   - Mean Spatial IoU: {s_m['mean_spatial_iou_pct']}%\n")

    i_m = results['metrics']['image_placement_analysis']
    print(f"4. IMAGE & FIGURE RETENTION:")
    print(f"   - Original Images:  {i_m['original_pdf_images_count']}")
    print(f"   - Recreated Images: {i_m['recreated_pdf_images_count']}")
    print(f"   - Image Retention:  {i_m['image_retention_rate_pct']}%\n")
    print("=======================================================================")

    evaluator.close()
