# ingest/chunker.py
from typing import List, Dict
import re

# grobe Token-Schätzung: 1 Token ~ 4 Zeichen (konservativ)
def approx_tokens_by_chars(s: str) -> int:
    return max(1, int(len(s) / 4))  # konservativ -> produziert eher kleinere Chunks

MAX_TOKENS = 500          # Hard-Cap für Embedding-Modelle mit Limit 512
TARGET_TOKENS = 350       # Zielgröße
OVERLAP_TOKENS = 60       # Kontext-Overlap

def _split_sentences(text: str) -> List[str]:
    # einfache Satztrennung
    return re.split(r"(?<=[.!?])\s+", text)

def _split_hard(s: str, max_tokens: int) -> List[str]:
    # Falls ein einzelner Satz/Block zu lang ist: nach Zeichen hart splitten
    max_chars = max_tokens * 4
    out, i, n = [], 0, len(s)
    while i < n:
        out.append(s[i:i+max_chars])
        i += max_chars
    return out

def split_into_chunks(text: str, target_tokens: int = TARGET_TOKENS, overlap_tokens: int = OVERLAP_TOKENS) -> List[str]:
    # große Blöcke zuerst nach Absätzen, dann nach Sätzen, dann hart
    paras = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    chunks: List[str] = []
    buf: List[str] = []
    buf_tokens = 0

    for para in paras:
        blocks = [para]
        if approx_tokens_by_chars(para) > target_tokens:
            # in Sätze splitten
            blocks = _split_sentences(para)

        for block in blocks:
            # falls Block selbst über dem Hardcap liegt -> hart schneiden
            if approx_tokens_by_chars(block) > MAX_TOKENS:
                for piece in _split_hard(block, MAX_TOKENS - 10):
                    # Stücke einzeln einspeisen
                    if approx_tokens_by_chars(piece) > target_tokens:
                        # falls immer noch groß: direkt als Chunk wegschreiben
                        chunks.append(piece)
                        continue
                    # sonst normal in den Buffer
                    tok = approx_tokens_by_chars(piece)
                    if buf_tokens + tok > target_tokens and buf:
                        chunks.append(" ".join(buf))
                        # Overlap
                        if overlap_tokens > 0:
                            words = " ".join(buf).split()
                            ov_words = " ".join(words[-overlap_tokens:]) if len(words) > overlap_tokens else " ".join(words)
                            buf = [ov_words] if ov_words else []
                            buf_tokens = approx_tokens_by_chars(" ".join(buf)) if buf else 0
                        else:
                            buf, buf_tokens = [], 0
                    buf.append(piece)
                    buf_tokens += tok
                continue

            tok = approx_tokens_by_chars(block)
            if buf_tokens + tok > target_tokens and buf:
                chunks.append(" ".join(buf))
                # Overlap
                if overlap_tokens > 0:
                    words = " ".join(buf).split()
                    ov_words = " ".join(words[-overlap_tokens:]) if len(words) > overlap_tokens else " ".join(words)
                    buf = [ov_words] if ov_words else []
                    buf_tokens = approx_tokens_by_chars(" ".join(buf)) if buf else 0
                else:
                    buf, buf_tokens = [], 0
            buf.append(block)
            buf_tokens += tok

    if buf:
        chunks.append(" ".join(buf))

    # Endkontrolle: kein Chunk über MAX_TOKENS
    fixed: List[str] = []
    for c in chunks:
        if approx_tokens_by_chars(c) <= MAX_TOKENS:
            fixed.append(c)
        else:
            fixed.extend(_split_hard(c, MAX_TOKENS - 10))
    return fixed

def to_records(doc_id: str, chunks: List[str], base_meta: Dict) -> List[Dict]:
    return [
        {"doc_id": doc_id, "chunk_id": i + 1, "content": c, "metadata": base_meta}
        for i, c in enumerate(chunks)
    ]
