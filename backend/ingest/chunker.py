from typing import List, Dict
import re

def _estimate_tokens(s: str) -> int:
    # Grobe Schätzung: 1 Token ~ 0.8 Wort
    return max(1, int(len(s.split()) / 0.8))

def split_into_chunks(text: str, target_tokens: int = 800, overlap: int = 100) -> List[str]:
    """
    Einfacher Chunker:
    - Split nach Absätzen
    - Bei sehr langen Absätzen: Split nach Sätzen
    - Sliding-Window mit Wort-Overlap
    """
    paras = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    chunks, buf, buf_len = [], [], 0

    for para in paras:
        sentences = re.split(r"(?<=[.!?])\s+", para) if _estimate_tokens(para) > target_tokens else [para]
        for s in sentences:
            s_tok = _estimate_tokens(s)
            if buf_len + s_tok > target_tokens and buf:
                chunks.append(" ".join(buf))
                if overlap > 0:
                    ov_words = " ".join(" ".join(buf).split()[-int(overlap*0.8):])
                    buf, buf_len = ([ov_words], _estimate_tokens(ov_words))
                else:
                    buf, buf_len = [], 0
            buf.append(s); buf_len += s_tok

    if buf:
        chunks.append(" ".join(buf))
    return chunks

def to_records(doc_id: str, chunks: List[str], base_meta: Dict) -> List[Dict]:
    return [
        {"doc_id": doc_id, "chunk_id": i, "content": c, "metadata": base_meta}
        for i, c in enumerate(chunks)
    ]
