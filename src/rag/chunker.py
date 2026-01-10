import re
from typing import List, Dict, Any

class SectionChunker:
    """
    Splits Markdown content into semantic sections based on headers.
    """
    
    def chunk(self, text: str) -> List[Dict[str, Any]]:
        """
        Splits text by headers and returns chunks with metadata.
        """
        lines = text.split('\n')
        chunks = []
        current_header = "Intro"
        current_content = []
        
        header_pattern = re.compile(r'^(#{1,3})\s+(.*)')
        
        for line in lines:
            match = header_pattern.match(line)
            if match:
                # Save previous chunk if it has content
                if current_content:
                    full_text = "\n".join(current_content).strip()
                    if full_text:
                        chunks.append({
                            "text": full_text,
                            "metadata": {
                                "header": current_header
                            }
                        })
                
                # Start new chunk
                current_header = match.group(2).strip()
                current_content = [line] # Include header in content? Yes, useful context.
            else:
                current_content.append(line)
        
        # Last chunk
        if current_content:
             full_text = "\n".join(current_content).strip()
             if full_text:
                chunks.append({
                    "text": full_text,
                    "metadata": {
                        "header": current_header
                    }
                })
                
        return chunks
