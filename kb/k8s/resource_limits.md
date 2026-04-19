---
title: "Resource Requests и Limits: управление ресурсами в Kubernetes"
tags: [kubernetes, resources, limits, scheduling, qos]
level: intermediate
prerequisites: [pods, deployments, scheduler]
source_file: kb/k8s/resource_limits.md
created: 2026-01-15
---

# Resource Requests и Limits

## Зачем ограничивать?
- **Requests**: гарантированные ресурсы для планирования
- **Limits**: жёсткий потолок потребления

```yaml
resources:
  requests: {memory: "256Mi", cpu: "250m"}
  limits:   {memory: "512Mi", cpu: "500m"}
```

## Единицы измерения
| Ресурс | Формат | Примеры |
|--------|--------|---------|
| CPU | millicores (m) | `100m` = 0.1 ядра, `1` = 1 ядро |
| Memory | байты с суффиксами | `128Mi`, `1Gi` |
| Storage | аналогично memory | `2Gi` для ephemeral |

## QoS классы
| Класс | Условия | При нехватке ресурсов |
|-------|---------|----------------------|
| Guaranteed | requests == limits | Последний кандидат на eviction |
| Burstable | requests < limits | Эвистируется после Guaranteed |
| BestEffort | нет requests/limits | Первый кандидат на eviction |

## Превышение лимитов
| Ресурс | Реакция K8s |
|--------|-------------|
| CPU | Троттлинг (замедление) |
| Memory | OOMKill (код выхода 137) |
| Storage | Pod Evicted |

## Частые ошибки
❌ Только limits → QoS BestEffort, непредсказуемое планирование
✅ Всегда указывайте и requests, и limits

## Quotas и LimitRanges
```yaml
# LimitRange: дефолты для namespace
apiVersion: v1
kind: LimitRange
spec:
  limits:
  - type: Container
    default: {memory: 512Mi, cpu: 500m}
    defaultRequest: {memory: 256Mi, cpu: 250m}
```

## Связанные темы
- [[scheduler]] — планирование
- [[monitoring]] — Prometheus метрики
- [[hpa]] — автоскейлинг