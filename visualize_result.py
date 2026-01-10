import sys
import os
import json

# Add module paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath("/mnt/d/progress/mathesis/mathesis-common"))

from mathesis_core.export.visualizers import ChartBuilder

def main():
    # 1. Simulate RAG Output (JSON)
    # Ideally this comes from RAGEngine.query()
    rag_result = {
      "answer": "수행평가 비율은 40%입니다.",
      "details": {
        "지필평가": 60.0,
        "수행평가": 40.0
      }
    }
    
    print("RAG Result:", json.dumps(rag_result, ensure_ascii=False))
    
    # 2. Visualize
    builder = ChartBuilder(output_dir="./visual_outputs")
    
    if "details" in rag_result:
        chart_path = builder.create_assessment_pie_chart(
            title="Math Assessment Ratio (2025)",
            data=rag_result["details"]
        )
        if chart_path:
            print(f"Chart generated successfully: {chart_path}")
        else:
            print("Failed to generate chart.")

if __name__ == "__main__":
    main()
