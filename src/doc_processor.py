
import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    Handles extraction of text from various document formats (PDF, HWP, etc.)
    Independent Version for Node 5.
    """
    
    def extract_text(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return self._extract_pdf(file_path)
        elif ext in [".hwp", ".hwpx"]:
            return self._extract_hwp(file_path)
        else:
            return f"[Unsupported Format: {ext}]"

    def _extract_pdf(self, path: str) -> str:
        try:
            # Try pypdf
            import pypdf
            reader = pypdf.PdfReader(path)
            text = []
            for page in reader.pages:
                text.append(page.extract_text() or "")
            return "\n".join(text)
        except ImportError:
            return "[Error: pypdf library missing]"
        except Exception as e:
            return f"[Error processing PDF: {e}]"

    def _extract_hwp(self, path: str) -> str:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                return content
        except Exception as e:
            return f"[Error processing HWP: {e}]"
