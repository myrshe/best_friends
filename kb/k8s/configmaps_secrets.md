---
title: "ConfigMaps и Secrets: управление конфигурацией"
tags: [kubernetes, configmaps, secrets, configuration]
level: intermediate
prerequisites: [pods, deployments]
source_file: kb/k8s/configmaps_secrets.md
created: 2026-01-15
---

# ConfigMaps и Secrets в Kubernetes

## ConfigMaps
Хранят конфигурацию отдельно от образа.

```yaml
apiVersion: v1
kind: ConfigMap
meta
  name: app-config
  database.url: "postgres://db:5432/myapp"
  log.level: "info"
```

### Способы монтирования
```yaml
envFrom:
- configMapRef: {name: app-config}
# или как volume
volumeMounts:
- {name: cfg, mountPath: /etc/config}
volumes:
- name: cfg
  configMap: {name: app-config}
```

## Secrets
Чувствительные данные (base64).
```yaml
apiVersion: v1
kind: Secret
meta
  name: db-creds
type: Opaque
stringData:
  username: admin
  password: super-secret
```
Монтируются аналогично ConfigMap, но через `secretKeyRef` или `secret` volume.

## Безопасность
| Практика | Почему важно |
|----------|-------------|
| Не хранить в Git | Используйте SealedSecrets / Vault |
| RBAC | Ограничьте `kubectl get secret` |
| Шифрование etcd | Включите `--encryption-provider-config` |
| Избегайте env vars | Видны в `ps` и логах |

## Обновление
- Volumes обновляются автоматически (~1 мин)
- Env vars требуют рестарта подов:
```bash
kubectl rollout restart deployment/my-app
```

## Связанные темы
- [[deployments]] — применение конфига
- [[rbac]] — контроль доступа
- [[external-secrets]] — интеграция с Vault