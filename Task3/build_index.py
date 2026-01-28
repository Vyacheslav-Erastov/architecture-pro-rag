from datetime import datetime
from pathlib import Path
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
import faiss
from sentence_transformers import SentenceTransformer

KNOWLEDGE_BASE_DIR = Path("Task2/knowledge_base_final")

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

INDEX_DIR = Path("Task3/index")
INDEX_PATH = INDEX_DIR / "faiss.index"
META_PATH = INDEX_DIR / "metadata.json"

MODEL_NAME = "BAAI/bge-base-en"
EMBEDDING_DIM = 768


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def load_documents():
    for file_path in KNOWLEDGE_BASE_DIR.rglob("*"):
        if file_path.suffix.lower() not in {".md", ".txt"}:
            continue

        text = file_path.read_text(encoding="utf-8")
        yield file_path, text


def chunk_document(file_path: Path, text: str):
    chunks = text_splitter.split_text(text)

    result = []
    for idx, chunk in enumerate(chunks):
        result.append(
            {
                "id": f"{file_path.stem}_{idx}",
                "text": chunk,
                "metadata": {
                    "source": str(file_path),
                    "chunk_index": idx,
                    "total_chunks": len(chunks),
                },
            }
        )
    return result


def main():
    total_chunks = []

    for file_path, text in load_documents():
        chunks = chunk_document(file_path, text)
        total_chunks.extend(chunks)

    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    texts = [f"passage: {c['text']}" for c in total_chunks]

    model = SentenceTransformer(MODEL_NAME)

    print(f"Total chunks: {len(total_chunks)}")

    print("Start embeddings generation")
    start_gen = datetime.now()
    embeddings = model.encode(
        texts, show_progress_bar=True, convert_to_numpy=True, normalize_embeddings=True
    )
    finish_gen = datetime.now()
    print("Finish embeddings generation")

    print(f"Generation time: {(finish_gen - start_gen).seconds}")

    index = faiss.IndexFlatIP(EMBEDDING_DIM)
    index.add(embeddings)

    faiss.write_index(index, str(INDEX_PATH))

    metadata = [
        {
            "id": c["id"],
            "source": c["metadata"]["source"],
            "chunk_index": c["metadata"]["chunk_index"],
            "total_chunks": c["metadata"]["total_chunks"],
            "text": c["text"],
        }
        for c in total_chunks
    ]

    with META_PATH.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"Total chunks: {len(total_chunks)}")


if __name__ == "__main__":
    main()
