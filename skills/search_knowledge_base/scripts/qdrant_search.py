from qdrant_client import QdrantClient
from qdrant_client.http.models import MatchAny, FieldCondition, Filter
from langchain_ollama import OllamaEmbeddings

def search(query: str, topic: str, level: str, config: dict) -> list:
    embeddings = OllamaEmbeddings(
        model=config.get("embedding_model", "nomic-embed-text"),
        base_url=config.get("ollama_url", "http://localhost:11434")
    )
    client = QdrantClient(url=config.get("qdrant_url", "http://localhost:6333"))

    query_vector = embeddings.embed_query(query)

    search_filter = None
    if topic and topic != "other":
        search_filter = Filter(
            must=[FieldCondition(key="tags", match=MatchAny(any=[topic]))]
        )

    results = client.query_points(
        collection_name=config.get("collection", "course_kb"),
        query=query_vector,
        limit=config.get("top_k", 5),
        query_filter=search_filter
    ).points

    chunks = []
    for hit in results:
        score = hit.score if hit.score is not None else 0.5
        if score > 0.3:
            chunks.append({
                "text": hit.payload.get("text", ""),
                "source": hit.payload.get("filename", "unknown.md"),
                "score": round(score, 3),
                "tags": hit.payload.get("tags", [])
            })
    return chunks[:config.get("top_k", 3)]