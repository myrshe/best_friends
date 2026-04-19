import os
import hashlib
from typing import List, Dict, Optional
import frontmatter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


QDRANT_URL = "http://localhost:6333"
OLLAMA_URL = "http://localhost:11434"
COLLECTION_NAME = "course_kb"
EMBEDDING_MODEL = "nomic-embed-text"


def get_embedding_model():
    return OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_URL)


def ensure_collection(client: QdrantClient, vector_size: int):
    collections = client.get_collections().collections
    if not any(c.name == COLLECTION_NAME for c in collections):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )
        print(f"Коллекция '{COLLECTION_NAME}' создана")


def load_md_files(kb_dir: str) -> List[Dict]:
    documents = []
    for root, _, files in os.walk(kb_dir):
        for file in files:
            if file.endswith(".md"):
                path = os.path.join(root, file)
                post = frontmatter.load(path)
                content = post.content
                metadata = post.metadata
                metadata["source"] = path
                metadata["filename"] = file

                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=500,
                    chunk_overlap=50,
                    separators=["\n## ", "\n### ", "\n\n", "\n", " "]
                )
                chunks = splitter.split_text(content)

                for i, chunk in enumerate(chunks):
                    chunk_id = hashlib.md5(f"{path}:{i}".encode()).hexdigest()
                    documents.append({
                        "id": chunk_id,
                        "text": chunk,
                        "metadata": {**metadata, "chunk_idx": i}
                    })
    return documents


def ingest_kb(kb_dir: str = "kb"):
    print(f"Запуск индексации из {kb_dir}...")

    embeddings = get_embedding_model()
    qdrant = QdrantClient(url=QDRANT_URL)

    test_vec = embeddings.embed_query("test")
    ensure_collection(qdrant, vector_size=len(test_vec))

    docs = load_md_files(kb_dir)
    if not docs:
        print("Файлы не найдены!")
        return

    print(f"Найдено {len(docs)} чанков. Векторизуем...")

    points = []
    for doc in docs:
        vector = embeddings.embed_query(doc["text"])
        points.append(
            PointStruct(
                id=doc["id"],
                vector=vector,
                payload={
                    "text": doc["text"],
                    **doc["metadata"]
                }
            )
        )

    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Готово! Загружено {len(points)} чанков в Qdrant.")


if __name__ == "__main__":
    ingest_kb()