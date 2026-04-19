---
title: "Оператор defer в Go"
tags: [go, defer, cleanup, resources]
level: beginner
prerequisites: [functions, error-handling]
source_file: kb/go/defer.md
created: 2026-01-15
---

# Оператор defer в Go

## Что такое defer?
`defer` — это ключевое слово, которое откладывает выполнение функции до момента возврата из текущей функции.

Пример:
```go
func readFile(path string) error {
    f, err := os.Open(path)
    if err != nil {
        return err
    }
    defer f.Close() // Выполнится после возврата из readFile
    
    // ... работа с файлом
    return nil
}
```

## Порядок выполнения (LIFO)
Несколько `defer` выполняются в обратном порядке:

```go
func example() {
    defer fmt.Println("Первый")
    defer fmt.Println("Второй") 
    defer fmt.Println("Третий")
}
// Вывод: Третий → Второй → Первый
```

## Практические сценарии

| Сценарий | Пример |
|----------|--------|
| Закрытие файла | `defer file.Close()` |
| Разблокировка мьютекса | `defer mu.Unlock()` |
| Закрытие HTTP-ответа | `defer resp.Body.Close()` |

## Частые ошибки

❌ Неверно — аргументы вычисляются сразу:
```go
defer fmt.Println("Значение:", getValue())
```

✅ Верно — отложенное вычисление через анонимную функцию:
```go
defer func() {
    fmt.Println("Значение:", getValue())
}()
```

## Связанные темы
- [[error-handling]] — обработка ошибок
- [[goroutines]] — конкурентность в Go