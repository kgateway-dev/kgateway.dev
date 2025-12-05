
## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | {} |  |
| controller.extraEnv | object | {} |  |
| controller.image.pullPolicy | string | "" |  |
| controller.image.registry | string | "" |  |
| controller.image.repository | string | "kgateway" |  |
| controller.image.tag | string | "" |  |
| controller.logLevel | string | "info" |  |
| controller.replicaCount | int | 1 |  |
| controller.service.ports.grpc | int | 9977 |  |
| controller.service.ports.health | int | 9093 |  |
| controller.service.type | string | "ClusterIP" |  |
| fullnameOverride | string | "" |  |
| image.pullPolicy | string | "IfNotPresent" |  |
| image.registry | string | "cr.kgateway.dev/kgateway-dev" |  |
| image.tag | string | "" |  |
| imagePullSecrets | list | [] |  |
| inferenceExtension.autoProvision | bool | false |  |
| inferenceExtension.enabled | bool | false |  |
| nameOverride | string | "" |  |
| nodeSelector | object | {} |  |
| podAnnotations | object | {} |  |
| podSecurityContext | object | {} |  |
| resources | object | {} |  |
| securityContext | object | {} |  |
| serviceAccount.annotations | object | {} |  |
| serviceAccount.create | bool | true |  |
| serviceAccount.name | string | "" |  |
| tolerations | list | [] |  |

