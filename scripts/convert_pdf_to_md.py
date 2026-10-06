#!/usr/bin/env python3
"""
Convert PDF design documents to Markdown files.
Outputs to a directory mirroring the original structure.
"""

import sys
# Add the virtual environment site-packages to sys.path to access pdfminer.six
VENV_PATH = "/Users/powermanl/powermanl-prj/yoho-check/.venv/lib/python3.9/site-packages"
if VENV_PATH not in sys.path:
    sys.path.insert(0, VENV_PATH)

import argparse
import logging
import os
from pathlib import Path

# pdfminer.six imports
from pdfminer.high_level import extract_text
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from io import StringIO

# Configuration
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


def is_encrypted(pdf_path):
    """Check if PDF is encrypted."""
    try:
        with open(pdf_path, 'rb') as f:
            parser = PDFParser(f)
            doc = PDFDocument(parser)
            # Some versions of pdfminer.six use 'is_encrypted' attribute
            if hasattr(doc, 'is_encrypted'):
                return doc.is_encrypted
            else:
                # Fallback: check if the document is encrypted via the 'encrypt' attribute?
                # For safety, assume not encrypted if we can't determine
                return False
    except Exception as e:
        logger.warning(f"Could not check encryption for {pdf_path}: {e}")
        # If we can't open the file, assume it's corrupted or unreadable
        return True  # Treat as unprocessable


def extract_text_from_pdf_page(pdf_path, page_num):
    """
    Extract text from a specific page of a PDF.
    Returns empty string if extraction fails.
    """
    try:
        # Use pdfminer's high-level extract_text with page numbers
        # Note: extract_text doesn't support single page extraction directly,
        # so we use a workaround with PDFPageInterpreter for precise control.
        output = StringIO()
        with open(pdf_path, 'rb') as f:
            parser = PDFParser(f)
            document = PDFDocument(parser)
            rsrcmgr = PDFResourceManager()
            device = TextConverter(rsrcmgr, output, laparams=LAParams())
            interpreter = PDFPageInterpreter(rsrcmgr, device)

            # Iterate through pages to find the target page
            for i, page in enumerate(PDFPage.get_pages(f), start=1):
                if i == page_num:
                    interpreter.process_page(page)
                    break
            else:
                # Page not found
                return ""

        text = output.getvalue()
        device.close()
        output.close()
        return text
    except PDFTextExtractionNotAllowed:
        logger.warning(f"Text extraction not allowed for page {page_num} in {pdf_path}")
        return ""
    except Exception as e:
        logger.warning(f"Failed to extract text from page {page_num} of {pdf_path}: {e}")
        return ""


def convert_pdf_to_markdown(pdf_path, output_path, pages=None):
    """
    Convert a single PDF file to Markdown.
    """
    try:
        # Check for encryption
        if is_encrypted(pdf_path):
            logger.warning(f"Skipping encrypted PDF: {pdf_path}")
            return False

        # Determine which pages to process
        if pages is None:
            # Get total number of pages
            with open(pdf_path, 'rb') as f:
                page_count = len(list(PDFPage.get_pages(f)))
            pages_to_process = list(range(1, page_count + 1))
        else:
            pages_to_process = pages

        # Extract text for each page
        page_sections = []
        for page_num in pages_to_process:
            text = extract_text_from_pdf_page(pdf_path, page_num)
            if text.strip():  # Only include non-empty pages
                section = f"## Page {page_num}\n\n{text.strip()}"
                page_sections.append(section)
            else:
                logger.info(f"Page {page_num} in {pdf_path} is empty or extraction failed")

        if not page_sections:
            logger.warning(f"No extractable text found in {pdf_path}")
            return False

        # Combine sections with horizontal rule separator
        full_md = "\n\n---\n\n".join(page_sections)

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write Markdown file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_md)

        logger.info(f"Converted: {pdf_path} -> {output_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to convert {pdf_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Convert PDF files to Markdown.")
    parser.add_argument(
        "--input-dir",
        type=str,
        required=True,
        help="Root directory containing PDF files to convert"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        required=True,
        help="Root directory for Markdown output"
    )
    parser.add_argument(
        "--pages",
        type=str,
        help="Comma-separated page numbers and ranges (e.g., '1,3,5-10')"
    )

    args = parser.parse_args()

    # Parse page ranges
    pages = None
    if args.pages:
        pages = set()
        for part in args.pages.split(','):
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                pages.update(range(start, end + 1))
            else:
                pages.add(int(part))
        logger.info(f"Processing pages: {sorted(pages)}")

    # Walk input directory
    input_root = Path(args.input_dir)
    output_root = Path(args.output_dir)

    if not input_root.is_dir():
        logger.error(f"Input directory does not exist: {input_root}")
        sys.exit(1)

    pdf_files = list(input_root.rglob("*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDF files found in {input_root}")
        return

    logger.info(f"Found {len(pdf_files)} PDF files to process")

    success_count = 0
    for pdf_file in pdf_files:
        # Compute relative path and output path
        rel_path = pdf_file.relative_to(input_root)
        md_rel_path = rel_path.with_suffix(".md")
        output_path = output_root / md_rel_path

        if convert_pdf_to_markdown(pdf_file, output_path, pages):
            success_count += 1

    logger.info(f"Successfully converted {success_count}/{len(pdf_files)} PDF files")


if __name__ == "__main__":
    main()