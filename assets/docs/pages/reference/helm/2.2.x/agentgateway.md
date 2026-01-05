
## Values

| Key | Type | Description | Default |
|-----|------|-------------|---------|
| affinity | object | Set affinity rules for pod scheduling, such as 'nodeAffinity:'. | `{}` |
| controller | object | Configure the agentgateway control plane deployment. | `{"extraEnv":{},"image":{"pullPolicy":"","registry":"","repository":"controller","tag":""},"logLevel":"info","replicaCount":1,"service":{"ports":{"agwGrpc":9978,"health":9093,"metrics":9092},"type":"ClusterIP"},"strategy":{},"xds":{"tls":{"enabled":false}}}` |
| controller.extraEnv | object | Add extra environment variables to the controller container. | `{}` |
| controller.image | object | Configure the controller container image. | `{"pullPolicy":"","registry":"","repository":"controller","tag":""}` |
| controller.image.pullPolicy | string | Set the image pull policy for the controller. | `""` |
| controller.image.registry | string | Set the image registry for the controller. | `""` |
| controller.image.repository | string | Set the image repository for the controller. | `"controller"` |
| controller.image.tag | string | Set the image tag for the controller. | `""` |
| controller.logLevel | string | Set the log level for the controller. | `"info"` |
| controller.replicaCount | int | Set the number of controller pod replicas. | `1` |
| controller.service | object | Configure the controller service. | `{"ports":{"agwGrpc":9978,"health":9093,"metrics":9092},"type":"ClusterIP"}` |
| controller.service.ports | object | Set the service ports for gRPC and health endpoints. | `{"agwGrpc":9978,"health":9093,"metrics":9092}` |
| controller.service.type | string | Set the service type for the controller. | `"ClusterIP"` |
| controller.strategy | object | Change the rollout strategy from the Kubernetes default of a RollingUpdate with 25% maxUnavailable, 25% maxSurge. E.g., to recreate pods, minimizing resources for the rollout but causing downtime: strategy:   type: Recreate E.g., to roll out as a RollingUpdate but with non-default parameters: strategy:   type: RollingUpdate   rollingUpdate:     maxSurge: 100% | `{}` |
| controller.xds | object | Configure TLS settings for the xDS gRPC servers. | `{"tls":{"enabled":false}}` |
| controller.xds.tls.enabled | bool | Enable TLS encryption for xDS communication. When enabled, the agent gateway xDS server (port 9978) will use TLS. When TLS is enabled, you must create a Secret named 'agentgateway-xds-cert' in the agentgateway installation namespace. The Secret must be of type 'kubernetes.io/tls' with 'tls.crt', 'tls.key', and 'ca.crt' data fields present. | `false` |
| deploymentAnnotations | object | Add annotations to the agentgateway deployment. | `{}` |
| discoveryNamespaceSelectors | list | List of namespace selectors (OR'ed): each entry can use 'matchLabels' or 'matchExpressions' (AND'ed within each entry if used together). Agentgateway includes the selected namespaces in config discovery. For more information, see the docs https://kgateway.dev/docs/latest/install/advanced/#namespace-discovery. | `[]` |
| fullnameOverride | string | Override the full name of resources created by the Helm chart, which is 'agentgateway'. If you set 'fullnameOverride: "foo", the full name of the resources that the Helm release creates become 'foo', such as the deployment, service, and service account for the agentgateway control plane in the agentgateway-system namespace. | `""` |
| gatewayClassParametersRefs | object | Map of GatewayClass names to GatewayParameters references that will be set on    the default GatewayClasses managed by kgateway. Each entry must define both the    name and namespace of the GatewayParameters resource.    The default GatewayClasses managed by kgateway are:    - agentgateway    Example:    gatewayClassParametersRefs:      agentgateway:        name: shared-gwp        namespace: kgateway-system | `{}` |
| image | object | Configure the default container image for the components that Helm deploys. You can override these settings for each particular component in that component's section, such as 'controller.image' for the agentgateway control plane. If you use your own private registry, make sure to include the imagePullSecrets. | `{"pullPolicy":"IfNotPresent","registry":"cr.agentgateway.dev","tag":""}` |
| image.pullPolicy | string | Set the default image pull policy. | `"IfNotPresent"` |
| image.registry | string | Set the default image registry. | `"cr.agentgateway.dev"` |
| image.tag | string | Set the default image tag. | `""` |
| imagePullSecrets | list | Set a list of image pull secrets for Kubernetes to use when pulling container images from your own private registry instead of the default agentgateway registry. | `[]` |
| inferenceExtension | object | Configure the integration with the Gateway API Inference Extension project, which lets you use agentgateway to route to AI inference workloads like LLMs that run locally in your Kubernetes cluster. Documentation for Inference Extension can be found here: https://kgateway.dev/docs/latest/agentgateway/inference/ | `{"enabled":false}` |
| inferenceExtension.enabled | bool | Enable Inference Extension support in the agentgateway controller. | `false` |
| nameOverride | string | Add a name to the default Helm base release, which is 'agentgateway'. If you set 'nameOverride: "foo", the name of the resources that the Helm release creates become 'agentgateway-foo', such as the deployment, service, and service account for the agentgateway control plane in the agentgateway-system namespace. | `""` |
| nodeSelector | object | Set node selector labels for pod scheduling, such as 'kubernetes.io/arch: amd64'. | `{}` |
| podAnnotations | object | Add annotations to the agentgateway pods. | `{"prometheus.io/scrape":"true"}` |
| podSecurityContext | object | Set the pod-level security context. For example, 'fsGroup: 2000' sets the filesystem group to 2000. | `{}` |
| resources | object | Configure resource requests and limits for the container, such as 'limits.cpu: 100m' or 'requests.memory: 128Mi'. | `{}` |
| securityContext | object | Set the container-level security context, such as 'runAsNonRoot: true'. | `{}` |
| serviceAccount | object | Configure the service account for the deployment. | `{"annotations":{},"create":true,"name":""}` |
| serviceAccount.annotations | object | Add annotations to the service account. | `{}` |
| serviceAccount.create | bool | Specify whether a service account should be created. | `true` |
| serviceAccount.name | string | Set the name of the service account to use. If not set and create is true, a name is generated using the fullname template. | `""` |
| tolerations | list | Set tolerations for pod scheduling, such as 'key: "nvidia.com/gpu"'. | `[]` |
