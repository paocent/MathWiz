# rag_engine.py
import os
import json
import hashlib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from config import PDF_DIR, VECTOR_DIR, CHUNK_SIZE, CHUNK_OVERLAP, EMBED_DIM, TOP_K

# Try to import PyMuPDF for real PDF extraction (optional)
try:
    import fitz
    HAS_FITZ = True
except Exception:
    HAS_FITZ = False

INDEX_FILE = os.path.join(VECTOR_DIR, "vectors.npy")
META_FILE = os.path.join(VECTOR_DIR, "metadata.json")

def local_hash_embedding(text: str, dim: int = EMBED_DIM) -> np.ndarray:
    vec = np.zeros(dim, dtype=float)
    words = text.lower().split()
    for i, w in enumerate(words):
        h = int(hashlib.md5(w.encode("utf-8")).hexdigest()[:8], 16)
        vec[i % dim] += (h % 1000) / 1000.0
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec

def extract_text_from_pdf(path: str) -> str:
    if not HAS_FITZ:
        raise RuntimeError("PyMuPDF (fitz) not installed.")
    doc = fitz.open(path)
    pages = []
    for p in range(doc.page_count):
        page = doc.load_page(p)
        pages.append(page.get_text("text"))
    doc.close()
    return "\n".join(pages)

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    text = text.replace("\r\n", "\n")
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    N = len(text)
    while start < N:
        end = min(start + chunk_size, N)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == N:
            break
        start = max(0, end - overlap)
    return chunks

def build_index_from_folder(folder_path: str = PDF_DIR):
    all_chunks = []
    metadata = []
    for fname in sorted(os.listdir(folder_path)):
        if not fname.lower().endswith(".pdf"):
            continue
        full = os.path.join(folder_path, fname)
        try:
            txt = extract_text_from_pdf(full)
        except Exception:
            txt = ""
        chunks = chunk_text(txt)
        for i, c in enumerate(chunks):
            all_chunks.append(c)
            metadata.append({
                "source": fname,
                "chunk_index": i,
                "preview": c[:400].replace("\n"," ")
            })
    if not all_chunks:
        if os.path.exists(INDEX_FILE):
            os.remove(INDEX_FILE)
        if os.path.exists(META_FILE):
            os.remove(META_FILE)
        return 0
    vectors = np.vstack([local_hash_embedding(c) for c in all_chunks]).astype("float32")
    np.save(INDEX_FILE, vectors)
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    return len(all_chunks)

def load_index():
    if not os.path.exists(INDEX_FILE) or not os.path.exists(META_FILE):
        return None, None
    vectors = np.load(INDEX_FILE)
    with open(META_FILE, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    return vectors, metadata

def retrieve(query: str, top_k: int = TOP_K):
    vectors, metadata = load_index()
    if vectors is None:
        return []
    qvec = local_hash_embedding(query).reshape(1, -1).astype("float32")
    sims = cosine_similarity(qvec, vectors)[0]
    idxs = np.argsort(-sims)[:top_k]
    results = []
    for idx in idxs:
        results.append({
            "score": float(sims[idx]),
            "text": metadata[idx].get("preview", "") + "\n\n(full chunk omitted)",
            "meta": metadata[idx]
        })
    return results
