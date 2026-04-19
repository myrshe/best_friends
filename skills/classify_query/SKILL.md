---
name: "classify_query"
description: "Классифицирует пользовательский запрос: определяет тему курса (go, k8s, python), уровень сложности (beginner/intermediate/advanced) и язык (ru/en)."
triggers:
  - "классифицировать"
  - "определить тему"
  - "маршрутизация"
  - "интент"
inputs:
  query: "string - текст вопроса пользователя"
  history: "string - опционально, последние сообщения диалога"
outputs:
  topic: "string - go | k8s | python | docker | other"
  level: "string - beginner | intermediate | advanced"
  language: "string - ru | en"
  confidence: "float - уверенность классификации 0.0-1.0"
---

# Навык: Классификация запроса

## Когда использовать
- Поступил новый вопрос от пользователя
- Нужно определить, к какой теме курса относится вопрос
- Требуется адаптировать сложность ответа под уровень пользователя

## Алгоритм выполнения
1. Проанализировать ключевые слова в `query`:
   - `defer`, `goroutine`, `channel` → topic: "go"
   - `pod`, `deployment`, `service` → topic: "k8s"
   - `list comprehension`, `decorator` → topic: "python"
2. Оценить уровень по терминологии:
   - "что такое", "как работает" → beginner
   - "оптимизация", "под капотом", "реализация" → advanced
3. Определить язык по алфавиту и грамматике
4. Вернуть JSON с классификацией

## Промпт для LLM (см. scripts/router_prompt.md)

Ты — классификатор учебных запросов. Верни СТРОГО JSON:
{"topic": "...", "level": "...", "language": "...", "confidence": 0.0-1.0}

Доступные значения:
- topic: go, k8s, python, docker, other
- level: beginner, intermediate, advanced
- language: ru, en

Если вопрос неясен — используй "other" и "beginner".

Вопрос: {query}

## Обработка ошибок
- Если уверенность < 0.6 → вернуть topic: "other", level: "beginner"
- Если JSON не распарсился → использовать regex-фолбэк по ключевым словам