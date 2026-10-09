import pymupdf as fitz


def extract_blocks(pdf_path: str):
    """Return a list of (page_number, block_text) in reading order."""
    doc = fitz.open(pdf_path)
    blocks = []
    empty_pages = 0
    for page_no, page in enumerate(doc, start=1):
        page_blocks = page.get_text("blocks", sort=True)
        text_found = False
        for b in page_blocks:
            text = b[4].strip()
            if text:
                blocks.append((page_no, text))
                text_found = True
        if not text_found:
            empty_pages += 1
    if empty_pages > len(doc) * 0.3:
        print(f"  WARNING: {empty_pages}/{len(doc)} pages have no text (scanned PDF? needs OCR)")
    return blocks