---
title: "Pods: базовая единица развертывания в Kubernetes"
tags: [kubernetes, pods, containers, basics]
level: beginner
prerequisites: [docker-basics]
source_file: kb/k8s/pods.md
created: 2026-01-15
---

# Pods в Kubernetes

## Что такое Pod?
Наименьшая единица развертывания. Может содержать 1+ контейнеров, которые:
- Делят сетевой стек (один IP, localhost)
- Делят тома (volumes)
- Запускаются на одной ноде

```yaml
apiVersion: v1
kind: Pod
meta
  name: my-app-pod
spec:
  containers:
  - name: app
    image: nginx:1.25
    ports:
    - containerPort: 80
```

## Жизненный цикл
```
Pending → Running → Succeeded/Failed → Terminated
```
| Фаза | Описание |
|------|----------|
| Pending | Планирование, pull образа |
| Running | Контейнеры работают |
| Failed | Завершение с ошибкой |
| Unknown | Потеря связи с нодой |

## Multi-container Pods
Паттерн sidecar для логирования:
```yaml
spec:
  containers:
  - name: app
    volumeMounts: [{name: logs, mountPath: /var/log}]
  - name: log-shipper
    image: fluent-bit
    volumeMounts: [{name: logs, mountPath: /var/log}]
  volumes:
  - name: logs
    emptyDir: {}
```

## Probes: проверка здоровья
```yaml
livenessProbe:   # Перезапуск при падении
  httpGet: {path: /health, port: 8080}
readinessProbe:  # Исключение из балансировки
  exec: {command: [cat, /tmp/ready]}
```

## Команды
```bash
kubectl get pods
kubectl describe pod <name>
kubectl logs <pod> -c <container>
```

## Связанные темы
- [[deployments]] — управление репликами
- [[services]] — сетевой доступ
- [[volumes]] — хранение данных