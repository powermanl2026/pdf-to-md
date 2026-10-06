# Usage Examples and Tips

## Basic Conversion
Convert all PDFs in a directory tree:
```bash
python -m pdf_to_md.scripts.convert_pdf_to_md \
  --input-dir /path/to/pdfs \
  --output-dir /path/to/markdown
```

## Page Selection
Convert only specific pages:
```bash
# Pages 1 through 3 and page 5
python -m pdf_to_md.scripts.convert_pdf_to_md \
  --input-dir ./specs \
  --output-dir ./output \
  --pages 1-3,5
```

## Integration with Other Skills
Use the output as input for other text processing skills or document generators.