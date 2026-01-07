
import os
import json
import subprocess
import logging
import re
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class TypstGenerator:
    """
    Typst Wrapper for PDF Generation (Standalone)
    """
    
    def __init__(self):
        self.font_paths = self._discover_fonts()
        self.font_arg = ["--font-path", str(self.font_paths[0])] if self.font_paths else []
        if self.font_paths:
            logger.info(f"TypstGenerator using font path: {self.font_paths[0]}")
        else:
            logger.warning("TypstGenerator: No Nanum/Korean fonts found. PDF text might be broken.")

    def _discover_fonts(self):
        """Find common font directories for Korean fonts"""
        candidates = [
            "/usr/share/fonts/truetype/nanum",
            "/usr/share/fonts/nanum",
            "/root/.local/share/fonts"
        ]
        found = [p for p in candidates if os.path.exists(p)]
        return found

    def compile(self, template_path: str, data: Dict[str, Any], output_path: str):
        """
        Compiles a Typst template with the given data.
        """
        try:
            data_file = Path(output_path).with_suffix('.json')
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            data_abs_path = str(data_file.absolute())
            # Root / allows absolute paths
            cmd = ["typst", "compile", "--root", "/", template_path, output_path] + self.font_arg
            cmd += ["--input", f"data_file={data_abs_path}"]
            
            logger.info(f"Compiling: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Typst compiled successfully: {output_path}")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Typst compilation failed: {e.stderr}")
            raise RuntimeError(f"Typst Error: {e.stderr}")
