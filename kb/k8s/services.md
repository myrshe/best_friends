---
title: "Services: сетевой доступ к приложениям в Kubernetes"
tags: [kubernetes, services, networking, load-balancing]
level: intermediate
prerequisites: [pods, deployments, labels-selectors]
source_file: kb/k8s/services.md
created: 2026-01-15
---

# Services в Kubernetes

## Зачем нужны Services?
Pods эфемерны. Service даёт:
- Стабильный ClusterIP и DNS
- Балансировку нагрузки
- Service discovery

```yaml
apiVersion: v1
kind: Service
meta
  name: web-service
spec:
  selector: {app: web-app}
  ports:
  - {protocol: TCP, port: 80, targetPort: 8080}
  type: ClusterIP
```

## Типы Services
| Тип | Доступ | Использование |
|-----|--------|--------------|
| ClusterIP | Внутри кластера | Внутренние микросервисы |
| NodePort | `<NodeIP>:<Port>` | Dev/тестирование |
| LoadBalancer | Внешний IP (облако) | Продакшен |
| ExternalName | DNS CNAME | Проксирование наружу |

## Service Discovery
```bash
# DNS внутри кластера
curl http://web-service.namespace.svc.cluster.local
# Короткое имя в том же namespace
curl http://web-service
```

## Headless Services
```yaml
spec:
  clusterIP: None
  selector: {app: database}
  ports: [{port: 5432}]
```
→ Возвращает IP всех подов напрямую. Нужно для StatefulSet и репликации БД.

## Частые ошибки
❌ Пустой `endpoints`:
```bash
kubectl get endpoints web-service
# Если пусто → проблема в selector или pods не в Ready
```

## Инспекция
```bash
kubectl get endpoints web-service
kubectl run tmp-shell --rm -i --tty --image curlimages/curl -- sh
kubectl describe service web-service
```

## Связанные темы
- [[deployments]] — управление подами
- [[ingress]] — HTTP маршрутизация
- [[network-policies]] — ограничение трафика