# kgateway

A Helm chart for the kgateway project

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object |  |  |
| controller.extraEnv | object |  |  |
| controller.image.pullPolicy | string |  |  |
| controller.image.registry | string |  |  |
| controller.image.repository | string |  |  |
| controller.image.tag | string |  |  |
| controller.logLevel | string |  |  |
| controller.replicaCount | int |  |  |
| controller.service.ports.grpc | int |  |  |
| controller.service.ports.health | int |  |  |
| controller.service.type | string |  |  |
| fullnameOverride | string |  |  |
| image.pullPolicy | string |  |  |
| image.registry | string |  |  |
| image.tag | string |  |  |
| imagePullSecrets | list |  |  |
| inferenceExtension.autoProvision | bool |  |  |
| inferenceExtension.enabled | bool |  |  |
| nameOverride | string |  |  |
| nodeSelector | object |  |  |
| podAnnotations | object |  |  |
| podSecurityContext | object |  |  |
| resources | object |  |  |
| securityContext | object |  |  |
| serviceAccount.annotations | object |  |  |
| serviceAccount.create | bool |  |  |
| serviceAccount.name | string |  |  |
| tolerations | list |  |  |

