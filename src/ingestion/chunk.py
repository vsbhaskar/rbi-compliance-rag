import re

PARA_RE = re.compile(r"^\s*(\d{1,3})\.\s+\S")
HEADING_RE = re.compile(r"^\s*(chapter|annex|annexure|section|part)\b", re.I)
ANNEX_RE = re.compile(r"^\s*annex", re.I)


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def chunk_blocks(doc_id: str, blocks, max_chars=1200, min_chars=400):
    chunks = []
    buf, buf_len = [], 0
    start_page, section = None, None
    chunk_section, chunk_para = None, None
    last_para, last_n = None, 0

    def flush():
        nonlocal buf, buf_len, start_page, chunk_para, chunk_section
        if not buf:
            return
        content = " ".join(buf)
        chunks.append({
            "chunk_id": f"{doc_id}-{len(chunks):04d}",
            "doc_id": doc_id,
            "chunk_index": len(chunks),
            "page_start": start_page,
            "para_no": chunk_para,
            "section_title": chunk_section,
            "content": content,
            "char_count": len(content),
        })
        buf, buf_len = [], 0

    for page, raw in blocks:
        text = clean(raw)
        if not text:
            continue

        if HEADING_RE.match(text) and len(text) < 120:
            section = text
            if ANNEX_RE.match(text):
                last_n = 0  # annexures restart their numbering

        m = PARA_RE.match(text)
        if m:
            n = int(m.group(1))
            if last_n < n <= last_n + 3:   # only accept forward-moving numbers
                last_n, last_para = n, str(n)
            else:
                m = None                   # sub-item like "2." inside a definition

        too_big = buf_len > 0 and buf_len + len(text) > max_chars
        new_para = bool(m) and buf_len >= min_chars
        if too_big or new_para:
            flush()

        if not buf:
            start_page = page
            chunk_para = last_para
            chunk_section = section
        buf.append(text)
        buf_len += len(text)

    flush()
    return chunks