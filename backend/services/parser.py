"""
PDF & Text Parsing Service
"""

import io
import re
from typing import Union


def extract_text_from_pdf(content: bytes) -> str:
    """
    Extract text from PDF using pdfplumber.
    Preserves layout as much as possible.
    """
    try:
        import pdfplumber
    except ImportError:
        # Fallback without pdfplumber
        return _simple_pdf_extract(content)
    
    text_parts = []
    
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    
    full_text = '\n\n'.join(text_parts)
    return _normalize_text(full_text)


def extract_text_from_txt(content: bytes) -> str:
    """Extract and normalize text from TXT file."""
    # Try different encodings
    for encoding in ['utf-8', 'latin-1', 'cp1252']:
        try:
            text = content.decode(encoding)
            return _normalize_text(text)
        except UnicodeDecodeError:
            continue
    
    # Last resort
    return _normalize_text(content.decode('utf-8', errors='ignore'))


def _normalize_text(text: str) -> str:
    """
    Normalize resume text:
    - Fix spacing
    - Normalize bullets
    - Clean special characters
    """
    # Replace various bullet characters with standard dash
    text = re.sub(r'[•●○◦▪▫►▻◆◇★☆✓✔✕✖✗✘→]', '-', text)
    
    # Normalize whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Fix multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove page numbers
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
    
    # Clean up lines
    lines = []
    for line in text.split('\n'):
        line = line.strip()
        if line:
            lines.append(line)
    
    return '\n'.join(lines)


def _simple_pdf_extract(content: bytes) -> str:
    """Fallback PDF extraction without pdfplumber."""
    # Very basic extraction - look for text patterns
    text = content.decode('latin-1', errors='ignore')
    
    # Remove binary noise
    printable = ''.join(c if c.isprintable() or c in '\n\r\t' else ' ' for c in text)
    
    return _normalize_text(printable)
