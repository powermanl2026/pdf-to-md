---
name: pdf-to-md
description: Convert PDF files to Markdown format with configurable options
version: 1.0.0
---
# PDF to Markdown Conversion Skill

**Name**: pdf-to-md  
**Description**: Converts PDF design documents to Markdown files, preserving basic text structure and directory hierarchy.  
**Version**: 1.0.0  
**Usage**: 
  ```bash
  python -m pdf_to_md.scripts.convert_pdf_to_md --input-dir &lt;INPUT_DIR&gt; --output-dir &lt;OUTPUT_DIR&gt; [--pages &lt;PAGE_LIST&gt;]
  ```
**Options**:
  - `--input-dir`: Root directory containing PDF files to convert (required)
  - `--output-dir`: Root directory for Markdown output (required)
  - `--pages`: Comma-separated page numbers and ranges to process (e.g., "1,3,5-10"). Processes all pages if omitted.
  - `--help`: Show this help message
**Examples**:
  ```bash
  # Convert all PDFs in ./designs to ./docs
  python -m pdf_to_md.scripts.convert_pdf_to_md --input-dir ./designs --output-dir ./docs
  
  # Convert only first 5 pages of each PDF
  python -m pdf_to_md.scripts.convert_pdf_to_md --input-dir ./designs --output-dir ./docs --pages 1-5
  
  # Convert specific pages
  python -m pdf_to_md.scripts.convert_pdf_to_md --input-dir ./designs --output-dir ./docs --pages 1,3,7,9-12
  ```
**Notes**:
  - Outputs one Markdown file per PDF file.
  - Each PDF page becomes a section headed by "## Page {page_number}".
  - Pages are separated by horizontal rules (`---`).
  - Directory structure from input is mirrored in output.
  - Encrypted or corrupted PDFs are skipped with warnings.