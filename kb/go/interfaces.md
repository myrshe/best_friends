---
title: "Интерфейсы в Go: полиморфизм и абстракция"
tags: [go, interfaces, polymorphism, design]
level: intermediate
prerequisites: [structs, methods]
source_file: kb/go/interfaces.md
created: 2026-01-15
---

# Интерфейсы в Go

## Что такое интерфейс?
Интерфейс в Go — набор сигнатур методов. Тип реализует интерфейс автоматически (утиная типизация), если определяет все методы.

Пример:
```go
type Speaker interface {
    Speak() string
}

type Dog struct{}
func (d Dog) Speak() string { return "Гав!" }

func MakeItSpeak(s Speaker) {
    fmt.Println(s.Speak())
}
```

## Ключевые принципы
| Принцип | Описание | Пример |
|---------|----------|--------|
| Утиная типизация | Не нужно явно объявлять `implements` | `Dog` автоматически `Speaker` |
| Маленькие интерфейсы | 1-2 метода легче переиспользовать | `io.Reader`, `io.Writer` |
| Определяет потребитель | Интерфейс создаёт тот, кто использует | Инверсия зависимостей |

## Встроенные интерфейсы stdlib
```go
type Reader interface { Read(p []byte) (n int, err error) }
type Closer interface { Close() error }

type ReadCloser interface { Reader; Closer }
```

## Type assertions и switches
```go
// Проверка типа
if wc, ok := w.(io.WriteCloser); ok {
    defer wc.Close()
}

// Переключение типов
func process(r io.Reader) {
    switch v := r.(type) {
    case *os.File:
        fmt.Println("Файл:", v.Name())
    default:
        fmt.Println("Другой Reader")
    }
}
```

## Частые ошибки
❌ Интерфейс с nil-значением не равен nil-интерфейсу:
```go
var f *os.File = nil
var r io.Reader = f
fmt.Println(r == nil) // false! r содержит (*os.File, nil)
```

✅ Best Practices:
- Возвращайте конкретные типы, принимайте интерфейсы
- Не создавайте интерфейсы "на будущее"
- Используйте `any` только при реальной необходимости

## Связанные темы
- [[structs-methods]] — основы ООП в Go
- [[error-handling]] — интерфейс error