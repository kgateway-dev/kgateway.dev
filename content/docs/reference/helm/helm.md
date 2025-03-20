# kgateway

A Helm chart for the kgateway project.

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` |  |
| autoscaling.enabled | bool | `false` |  |
| autoscaling.maxReplicas | int | `100` |  |
| autoscaling.minReplicas | int | `1` |  |
| autoscaling.targetCPUUtilizationPercentage | int | `80` |  |
| controller.image.pullPolicy | string | `"IfNotPresent"` |  |
| controller.image.registry | string | `""` |  |
| controller.image.repository | string | `"kgateway"` |  |
| controller.image.tag | string | `""` |  |
| controller.logLevel | string | `"info"` |  |
| controller.replicaCount | int | `1` |  |
| controller.service.ports.grpc | int | `9977` |  |
| controller.service.type | string | `"ClusterIP"` |  |
| fullnameOverride | string | `""` |  |
| gateway.aiExtension.enabled | bool | `false` |  |
| gateway.aiExtension.image.repository | string | `"kgateway-ai-extension"` |  |
| gateway.envoyContainer.image.pullPolicy | string | `"IfNotPresent"` |  |
| gateway.envoyContainer.image.registry | string | `""` |  |
| gateway.envoyContainer.image.repository | string | `"envoy-wrapper"` |  |
| gateway.envoyContainer.image.tag | string | `""` |  |
| gateway.envoyContainer.securityContext.allowPrivilegeEscalation | bool | `false` |  |
| gateway.envoyContainer.securityContext.capabilities.add[0] | string | `"NET_BIND_SERVICE"` |  |
| gateway.envoyContainer.securityContext.capabilities.drop[0] | string | `"ALL"` |  |
| gateway.envoyContainer.securityContext.readOnlyRootFilesystem | bool | `true` |  |
| gateway.envoyContainer.securityContext.runAsNonRoot | bool | `true` |  |
| gateway.envoyContainer.securityContext.runAsUser | int | `10101` |  |
| gateway.istio.istioProxyContainer.image.registry | string | `"docker.io/istio"` |  |
| gateway.istio.istioProxyContainer.image.repository | string | `"proxyv2"` |  |
| gateway.istio.istioProxyContainer.image.tag | string | `"1.22.0"` |  |
| gateway.istio.istioProxyContainer.istioDiscoveryAddress | string | `"istiod.istio-system.svc:15012"` |  |
| gateway.istio.istioProxyContainer.istioMetaClusterId | string | `"Kubernetes"` |  |
| gateway.istio.istioProxyContainer.istioMetaMeshId | string | `"cluster.local"` |  |
| gateway.istio.istioProxyContainer.logLevel | string | `"warning"` |  |
| gateway.proxyDeployment.replicas | int | `1` |  |
| gateway.sdsContainer.image.pullPolicy | string | `"IfNotPresent"` |  |
| gateway.sdsContainer.image.registry | string | `""` |  |
| gateway.sdsContainer.image.repository | string | `"sds"` |  |
| gateway.sdsContainer.logLevel | string | `"info"` |  |
| gateway.stats.enableStatsRoute | bool | `true` |  |
| gateway.stats.enabled | bool | `true` |  |
| gateway.stats.routePrefixRewrite | string | `"/stats/prometheus"` |  |
| gateway.stats.statsRoutePrefixRewrite | string | `"/stats"` |  |
| gatewayClass.annotations | object | `{}` |  |
| gatewayClass.controllerName | string | `"kgateway.dev/kgateway"` |  |
| gatewayClass.description | string | `"kgateway controller"` |  |
| gatewayClass.enabled | bool | `true` |  |
| gatewayClass.labels | object | `{}` |  |
| gatewayClass.name | string | `"kgateway"` |  |
| gatewayClass.parametersRef.enabled | bool | `true` |  |
| gatewayClass.parametersRef.group | string | `"gateway.kgateway.dev"` |  |
| gatewayClass.parametersRef.kind | string | `"GatewayParameters"` |  |
| gatewayClass.parametersRef.name | string | `"kgateway"` |  |
| gatewayClass.parametersRef.podTemplate.extraAnnotations | object | `{}` |  |
| gatewayClass.parametersRef.podTemplate.extraLabels | object | `{}` |  |
| gatewayClass.service.type | string | `"LoadBalancer"` |  |
| image.pullPolicy | string | `"IfNotPresent"` |  |
| image.registry | string | `"cr.kgateway.dev/kgateway-dev"` |  |
| image.tag | string | `""` |  |
| imagePullSecrets | list | `[]` |  |
| inferenceExtension.enabled | bool | `false` |  |
| nameOverride | string | `""` |  |
| nodeSelector | object | `{}` |  |
| podAnnotations | object | `{}` |  |
| podSecurityContext | object | `{}` |  |
| resources | object | `{}` |  |
| securityContext | object | `{}` |  |
| serviceAccount.annotations | object | `{}` |  |
| serviceAccount.create | bool | `true` |  |
| serviceAccount.name | string | `""` |  |
| tolerations | list | `[]` |  |
| waypointClass.annotations."ambient.istio.io/waypoint-inbound-binding" | string | `"PROXY/15088"` |  |
| waypointClass.controllerName | string | `"kgateway.dev/kgateway"` |  |
| waypointClass.description | string | `"kgateway waypoint controller"` |  |
| waypointClass.enabled | bool | `true` |  |
| waypointClass.labels | object | `{}` |  |
| waypointClass.name | string | `"kgateway-waypoint"` |  |
| waypointClass.parametersRef.enabled | bool | `true` |  |
| waypointClass.parametersRef.group | string | `"gateway.kgateway.dev"` |  |
| waypointClass.parametersRef.kind | string | `"GatewayParameters"` |  |
| waypointClass.parametersRef.name | string | `"kgateway-waypoint"` |  |
| waypointClass.parametersRef.podTemplate.extraAnnotations | object | `{}` |  |
| waypointClass.parametersRef.podTemplate.extraLabels."istio.io/dataplane-mode" | string | `"ambient"` |  |
| waypointClass.service.type | string | `"ClusterIP"` |  |
