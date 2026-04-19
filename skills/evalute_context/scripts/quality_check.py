def evaluate(chunks: list, query: str) -> dict:

    if not chunks:
        return {"status": "insufficient", "reason": "empty", "avg_score": 0.0}

    avg_score = sum(c.get("score", 0) for c in chunks) / len(chunks)

    if len(chunks) >= 2 and avg_score >= 0.6:
        return {
            "status": "sufficient",
            "reason": f"{len(chunks)} чанков, avg_score={avg_score:.2f}",
            "avg_score": round(avg_score, 2)
        }

    return {
        "status": "insufficient",
        "reason": f"Мало чанков ({len(chunks)}) или низкая релевантность ({avg_score:.2f})",
        "avg_score": round(avg_score, 2)
    }