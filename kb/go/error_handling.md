---
title: "Обработка ошибок в Go: идиомы и паттерны"
tags: [go, errors, error-handling, idioms]
level: beginner
prerequisites: [functions, interfaces]
source_file: kb/go/error_handling.md
created: 2026-01-15
---

# Обработка ошибок в Go

## Философия
Ошибки в Go — это значения. Функции возвращают `error` как последний параметр.

```go
func ReadConfig(path string) (*Config, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, fmt.Errorf("read config: %w", err)
    }
    return parse(data)
}
```

## Базовые паттерны
✅ Проверка сразу:
```go
f, err := os.Open("config.json")
if err != nil {
    return err
}
defer f.Close()
```

✅ Контекст через обёртку (Go 1.13+):
```go
if err != nil {
    return fmt.Errorf("process user %d: %w", userID, err)
}
```

✅ Сравнение конкретных ошибок:
```go
if errors.Is(err, os.ErrNotExist) {
    return defaultConfig()
}
```

## Sentinel errors vs типы ошибок
| Подход | Когда использовать | Пример |
|--------|-------------------|--------|
| Sentinel (`var ErrX = errors.New(...)`) | Ошибка часть бизнес-логики | `sql.ErrNoRows` |
| Тип ошибки (структура) | Нужны доп. поля или логика | `*os.PathError` |
| Обёртка (`%w`) | Добавление контекста | `fmt.Errorf("db: %w", err)` |

## Panic и recover
Используйте `panic` только для неустранимых ошибок программирования:
```go
func MustParse(s string) *Config {
    cfg, err := Parse(s)
    if err != nil { panic(err) }
    return cfg
}
```
`recover` только в граничных горутинах с `defer`.

## Частые ошибки
❌ Игнорирование: `_ = file.Close()`
✅ Всегда проверяйте или явно логируйте: `if err := f.Close(); err != nil { log.Println(err) }`

## Связанные темы
- [[interfaces]] — интерфейс error
- [[logging]] — логирование