import os
import sys
import logging
import json

# Add Node 6 and Common to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) # node6 root
sys.path.append(os.path.abspath("/mnt/d/progress/mathesis/mathesis-common")) # common root

# Configure logging
logging.basicConfig(level=logging.INFO)

from src.rag.engine import RAGEngine

def create_dummy_pdf(path):
    # Since we can't easily create a real PDF programmatically without reportlab,
    # we will rely on a mock/test-only behavior or just manually place a file.
    # OR better: The user might have files.
    # If not, let's create a dummy text file and pretend the parser handles it? 
    # No, parser uses pdfplumber.
    
    # Check if we have sample files in downloads/B100000662/2025/teaching_plans?
    # The crawler creates some dummy files but they are just text files renamed as .pdf in the simulation crawler!
    # Ah! The simulation crawler writes "Mock PDF (Typst missing)" to .pdf files.
    # pdfplumber will fail on that.
    
    # We need a REAL PDF or a mock parser for testing.
    # Let's mock the parser here to avoid needing a real PDF for this quick test.
    pass

class MockParser:
    def parse(self, path):
        return """
# 2025학년도 동도중학교 수학과 평가계획

## 1. 평가 목적
학생들의 수학적 사고력을 기른다.

## 2. 평가 비율
| 평가 종류 | 비율 | 내용 |
| --- | --- | --- |
| 지필평가 | 60% | 중간(30%), 기말(30%) |
| 수행평가 | 40% | 서술형(20%), 포트폴리오(20%) |
"""

if __name__ == "__main__":
    print("Initializing RAGEngine...")
    engine = RAGEngine(collection_name="test_school_v1")
    

    # Mock parser for testing
    engine.parser = MockParser()

    # Mock Ollama correctly by monkeypatching the EXISTING instance
    # This ensures the Reference held by ChromaHybridStore is also affected
    
    def mock_embed(text, model="nomic-embed-text:latest"):
        return [0.1] * 768
        
    def mock_generate(prompt, **kwargs):
        return json.dumps({
            "answer": "수행평가 비율은 40%입니다. (Mock AI Answer)",
            "references": ["Section 2"],
            "details": {"performance_ratio": "40%"}
        })
        
    engine.ollama.embed = mock_embed
    engine.ollama.generate = mock_generate

    print("Ingesting mock file...")

    # Path doesn't matter for mock parser
    engine.ingest_file("dummy.pdf", metadata={"school": "Demo School"})
    
    print("Querying: '수학 수행평가 비율은?'...")
    result = engine.query("수학 수행평가 비율은?")
    
    print("\n--- Result JSON ---")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if "40%" in str(result) or "수행평가" in str(result):
        print("\n✅ Verification SUCCESS: Found relevant info.")
    else:
        print("\n❌ Verification FAILED: Could not find info.")
