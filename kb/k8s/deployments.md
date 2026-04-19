---
title: "Deployments: декларативное управление приложениями"
tags: [kubernetes, deployments, rolling-update, scaling]
level: beginner
prerequisites: [pods, labels-selectors]
source_file: kb/k8s/deployments.md
created: 2026-01-15
---

# Deployments в Kubernetes

## Что такое Deployment?
Ресурс для управления состоянием Pods и ReplicaSets. Обеспечивает:
- Rolling updates без простоя
- Rollback к предыдущим версиям
- Горизонтальное масштабирование
- Самовосстановление

```yaml
apiVersion: apps/v1
kind: Deployment
meta
  name: web-app
spec:
  replicas: 3
  selector: {matchLabels: {app: web-app}}
  template:
    meta
      labels: {app: web-app}
    spec:
      containers:
      - {name: nginx, image: nginx:1.25}
```

## Стратегии обновления
| Стратегия | Поведение | Когда использовать |
|-----------|-----------|-------------------|
| RollingUpdate | Постепенная замена подов | Продакшен, zero-downtime |
| Recreate | Удалить все старые → создать новые | Не поддерживают параллельные версии |

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0
```

## Основные операции
```bash
kubectl apply -f deploy.yaml
kubectl rollout status deployment/web-app
kubectl set image deployment/web-app nginx=nginx:1.26
kubectl rollout undo deployment/web-app
kubectl scale deployment/web-app --replicas=5
```

## Частые ошибки
❌ Неправильный selector:
```yaml
selector: {matchLabels: {app: wrong}}
template: {meta
```
✅ `selector.matchLabels` обязан совпадать с `template.metadata.labels`

## Связанные темы
- [[pods]] — базовая единица
- [[services]] — доступ к подам
- [[configmaps-secrets]] — конфигурация