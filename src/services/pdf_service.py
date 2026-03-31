"""
PDF service — loads and extracts text from all PDFs in data/fund2_docs/.

Text is extracted once at first use and cached for the server session.
Drop any PDF into data/fund2_docs/ and restart the server to pick it up.
"""

from pathlib import Path
from typing import Optional

import pdfplumber

from src.utils.logger import get_logger

logger = get_logger(__name__)

DOCS_DIR = Path(__file__).parent.parent.parent / "data" / "fund2_docs"


class PDFService:
    def __init__(self):
        self._cached_text: Optional[str] = None

    def get_document_context(self) -> Optional[str]:
        """
        Return concatenated text from all PDFs in data/fund2_docs/.
        Result is cached for the server session — restart to reload.
        """
        if self._cached_text is not None:
            return self._cached_text

        if not DOCS_DIR.exists():
            logger.warning("fund2_docs directory not found", path=str(DOCS_DIR))
            return None

        pdf_files = sorted(DOCS_DIR.glob("*.pdf"))
        if not pdf_files:
            logger.warning("No PDF files found in fund2_docs", path=str(DOCS_DIR))
            return None

        texts = []
        for pdf_path in pdf_files:
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    page_texts = [
                        page.extract_text()
                        for page in pdf.pages
                        if page.extract_text()
                    ]
                if page_texts:
                    texts.append(f"=== {pdf_path.name} ===\n" + "\n".join(page_texts))
                    logger.info("Loaded PDF", file=pdf_path.name, pages=len(page_texts))
            except Exception as e:
                logger.error("Failed to load PDF", file=pdf_path.name, error=str(e))

        if not texts:
            return None

        self._cached_text = "\n\n".join(texts)
        logger.info("PDF context ready", files=len(texts), chars=len(self._cached_text))
        return self._cached_text


pdf_service = PDFService()
