import re
import json
from pathlib import Path

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

POLICY_DIR = Path(__file__).parent.parent / "data"
POLICY_FILE = POLICY_DIR / "school_policy.txt"
INDEX_FILE = POLICY_DIR / "policy_index.json"

MODEL_NAME = "all-MiniLM-L6-v2"
_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def load_policy():
    if not POLICY_FILE.exists():
        raise FileNotFoundError(f"Policy file not found: {POLICY_FILE}")

    text = POLICY_FILE.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError("The school policy file is empty.")

    return text


def split_into_chunks(text):
    pieces = re.split(r"(?m)^(?=\d+\.\s)", text)
    return [p.strip() for p in pieces if p.strip()]


def build_index():
    chunks = split_into_chunks(load_policy())

    print("Loading embedding model...")
    embeddings = get_model().encode(chunks, normalize_embeddings=True)

    index = {"chunks": chunks, "embeddings": embeddings.tolist()}
    INDEX_FILE.write_text(
        json.dumps(index, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("Policy index created successfully.")
    print(f"Policy sections indexed: {len(chunks)}")


def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def rank_of(scores):
    order = np.argsort(scores)[::-1]
    return {int(i): position + 1 for position, i in enumerate(order)}


def search_policy(question, top_k=2, mode="hybrid"):
    if not INDEX_FILE.exists():
        build_index()

    index = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    chunks = index["chunks"]

    # 1. Meaning search
    question_embedding = get_model().encode(
        [question], normalize_embeddings=True
    )[0]
    meaning_scores = np.array(index["embeddings"]) @ question_embedding

    # 2. Keyword search
    bm25 = BM25Okapi([tokenize(c) for c in chunks])
    keyword_scores = bm25.get_scores(tokenize(question))
    has_keyword_match = keyword_scores.max() > 0

    # 3. Nothing relevant at all
    if meaning_scores.max() < 0.25 and not has_keyword_match:
        return []
    if mode == "keyword" and not has_keyword_match:
        return []

    # 4. Give points to each section
    meaning_rank = rank_of(meaning_scores)
    keyword_rank = rank_of(keyword_scores)

    combined = {}
    for i in range(len(chunks)):
        points = 0
        if mode in ("hybrid", "meaning"):
            points += 1 / (60 + meaning_rank[i])
        if mode in ("hybrid", "keyword") and has_keyword_match:
            points += 1 / (60 + keyword_rank[i])
        combined[i] = points

    # 5. Pick the best, drop weak runners-up
    best = sorted(combined, key=combined.get, reverse=True)[:top_k]

    if mode != "keyword":
        top_meaning = meaning_scores[best[0]]
        best = [i for i in best if meaning_scores[i] >= top_meaning * 0.7]

    return [{"text": chunks[i], "score": combined[i]} for i in best]


if __name__ == "__main__":
    build_index()

    print("\nPolicy search test (type 'exit' to stop)")
    while True:
        question = input("\nAsk about school policies: ").strip()
        if question.lower() in ("exit", "quit", ""):
            break

        results = search_policy(question)
        if not results:
            print("No relevant policy found.")
        for result in results:
            print(f"\nRelevance: {result['score']:.3f}")
            print(result["text"])