import json
import os
import sys
import time
import httpx
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.config import settings

client = httpx.Client(timeout=120.0, base_url=settings.OLLAMA_BASE_URL)


def call_llm(prompt: str) -> dict:
    payload = {
        "model": settings.LLM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "options": {"temperature": 0.0, "num_predict": 50},
        "stream": False
    }
    resp = client.post("/api/chat", json=payload)
    resp.raise_for_status()
    content = resp.json()["message"]["content"].strip()
    for token in content.replace(",", ".").split():
        try:
            return float(token)
        except ValueError:
            continue
    return 0.0


def score_faithfulness(q: str, a: str, ctx: str) -> float:
    prompt = f"""Оцени, насколько ответ основан ТОЛЬКО на контексте. Верни число от 0.0 до 1.0.
Вопрос: {q}
Контекст: {ctx}
Ответ: {a}
Число:"""
    return call_llm(prompt)


def score_relevancy(q: str, a: str) -> float:
    prompt = f"""Оцени, насколько ответ релевантен вопросу. Верни число от 0.0 до 1.0.
Вопрос: {q}
Ответ: {a}
Число:"""
    return call_llm(prompt)


def score_precision(q: str, ctx: str) -> float:
    prompt = f"""Оцени, насколько найденный контекст полезен для ответа на вопрос. Верни число от 0.0 до 1.0.
Вопрос: {q}
Контекст: {ctx}
Число:"""
    return call_llm(prompt)


def score_recall(q: str, a: str, truth: str) -> float:
    prompt = f"""Оцени, покрывает ли ответ все ключевые факты из эталона. Верни число от 0.0 до 1.0.
Эталон: {truth}
Ответ: {a}
Число:"""
    return call_llm(prompt)


def run_evals(dataset_path: str = "src/evals/dataset.json"):
    print("🔍 Запуск синхронной оценки качества...")
    if not os.path.exists(dataset_path):
        print(f"Файл не найден: {dataset_path}")
        return

    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    dataset = dataset[:7]
    print(f"Оцениваем {len(dataset)} вопросов (по одному, без параллелизма)")

    scores = {"faithfulness": [], "answer_relevancy": [], "context_precision": [], "context_recall": []}

    for i, item in enumerate(dataset, 1):
        print(f"\nВопрос {i}/7: {item['question'][:50]}...")
        ctx_text = " | ".join(item["contexts"])

        try:
            scores["faithfulness"].append(score_faithfulness(item["question"], item["answer"], ctx_text))
            time.sleep(2)  # Пауза между вызовами
            scores["answer_relevancy"].append(score_relevancy(item["question"], item["answer"]))
            time.sleep(2)
            scores["context_precision"].append(score_precision(item["question"], ctx_text))
            time.sleep(2)
            scores["context_recall"].append(score_recall(item["question"], item["answer"], item["ground_truth"]))
            print(f"Готово")
        except Exception as e:
            print(f"Ошибка на метрике: {e}")

    results = {k: round(sum(v) / len(v), 3) if v else 0.0 for k, v in scores.items()}

    print("\n📊 Итоговые метрики:")
    for k, v in results.items():
        print(f"  {k}: {v:.3f}")

    os.makedirs("reports", exist_ok=True)
    with open("reports/eval_report.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("Сохранено в reports/eval_report.json")
    return results


if __name__ == "__main__":
    run_evals()