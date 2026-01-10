import sys
import os
import logging
from pathlib import Path

# Add paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath("/mnt/d/progress/mathesis/mathesis-common"))

from mathesis_core.export.typst_wrapper import TypstGenerator

logging.basicConfig(level=logging.INFO)

def generate_source_pdf():
    """
    Generates a 'Source' PDF that simulates a downloaded school teaching plan.
    This PDF will be readable by pdfplumber (text-based).
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "downloads", "source_materials")
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Create a simpler raw template if needed, or reuse teaching_plan.typ with raw data
    template_path = os.path.join(base_dir, "templates", "teaching_plan.typ")
    
    # Raw Data mimicking a real document
    data = {
        "school_name": "테스트중학교",
        "filename": "2025_Source_Plan.pdf",
        "year": "2025",
        "curriculum_content": [
             {"area": "수학교과", "detail": "함수와 그래프 집중 탐구"},
             {"area": "평가방침", "detail": "지필 50%, 수행 50% (서술형 30%, 포트폴리오 20%)"}
        ],
        # Empty fields for the sections we are supposed to generate via RAG
        "rag_analysis": "원본 문서입니다. (분석 전)"
        # Note: Do not include "chart_image_path" key to avoid Typst trying to load empty path
    }
    
    output_pdf = os.path.join(output_dir, "2025_Source_Plan.pdf")
    
    gen = TypstGenerator()
    gen.compile(template_path, data, output_pdf)
    
    return output_pdf

if __name__ == "__main__":
    pdf = generate_source_pdf()
    print(f"Generated Source PDF: {pdf}")
