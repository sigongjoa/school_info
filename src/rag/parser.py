import pdfplumber
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class PDFTableParser:
    """
    Parses PDF into Markdown format, attempting to preserve table structures.
    Uses pdfplumber for table extraction.
    """
    
    def parse(self, pdf_path: str) -> str:
        """
        Parses a PDF file and returns a Markdown string.
        """
        logger.info(f"Parsing PDF: {pdf_path}")
        markdown_output = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    markdown_output.append(f"## Page {page_num + 1}")
                    
                    # 1. Extract Text (Layout-aware)
                    # We might want to separate tables from text, but pdfplumber's extract_text
                    # sometimes merges them messily.
                    # Strategy: Find tables, extract them, and try to place them? 
                    # Simpler strategy for V1: Extract tables first, then extract text ignoring table areas?
                    # Or just: Text extraction + Append found tables?
                    
                    # Let's try simple text extraction first, but converting tables to MD
                    text = page.extract_text()
                    if text:
                        markdown_output.append(text)
                    
                    # 2. Extract Tables and convert to Markdown
                    tables = page.extract_tables()
                    if tables:
                        markdown_output.append("\n### Tables\n")
                        for table in tables:
                            md_table = self._table_to_markdown(table)
                            markdown_output.append(md_table)
                            markdown_output.append("\n")
                            
        except Exception as e:
            logger.error(f"Failed to parse PDF {pdf_path}: {e}")
            return ""

        return "\n".join(markdown_output)

    def _table_to_markdown(self, table: List[List[str]]) -> str:
        """
        Converts a list of lists (table) into a Markdown table string.
        Handles None values and multiline cells.
        """
        if not table:
            return ""
            
        # Clean cells
        cleaned_table = []
        for row in table:
            cleaned_row = []
            for cell in row:
                if cell is None:
                    cleaned_row.append("")
                else:
                    # Replace newlines with space to keep markdown table structure valid
                    cleaned_row.append(cell.replace("\n", "<br>").strip())
            cleaned_table.append(cleaned_row)
            
        # Header
        header = cleaned_table[0]
        # Body
        body = cleaned_table[1:]
        
        md_lines = []
        # Header row
        md_lines.append("| " + " | ".join(header) + " |")
        # Separator row
        md_lines.append("| " + " | ".join(["---"] * len(header)) + " |")
        
        # Body rows
        for row in body:
            # Handle row length mismatch (merged cells might cause this?)
            # Pdfplumber usually fills, but if not, pad.
            if len(row) < len(header):
                row += [""] * (len(header) - len(row))
            elif len(row) > len(header):
                # Truncate or extend header? Let's just fit first N
                row = row[:len(header)]
                
            md_lines.append("| " + " | ".join(row) + " |")
            
        return "\n".join(md_lines)
