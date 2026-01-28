
## Values

| Key | Type | Description | Default |
|-----|------|-------------|---------|
| affinity | object | Set affinity rules for pod scheduling, such as 'nodeAffinity:'. | `{}` |
| commonLabels | object | Additional labels to add to all resources created by the Helm chart. | `{}` |
| controller | object | Configure the kgateway control plane deployment. | `{"extraEnv":{},"horizontalPodAutoscaler":{},"image":{"pullPolicy":"","registry":"","repository":"kgateway","tag":""},"logLevel":"info","podDisruptionBudget":{},"priorityClassName":"","replicaCount":1,"service":{"allocateLoadBalancerNodePorts":null,"annotations":{},"clusterIP":"","clusterIPs":[],"enabled":true,"externalIPs":[],"externalName":"","externalTrafficPolicy":"","extraLabels":{},"healthCheckNodePort":null,"internalTrafficPolicy":"","ipFamilies":[],"ipFamilyPolicy":"","loadBalancerClass":"","loadBalancerIP":"","loadBalancerSourceRanges":[],"ports":{"grpc":9977,"health":9093,"metrics":9092},"publishNotReadyAddresses":false,"sessionAffinity":"","sessionAffinityConfig":{},"trafficDistribution":"","type":"ClusterIP"},"strategy":{},"verticalPodAutoscaler":{},"xds":{"tls":{"enabled":false}}}` |
| controller.extraEnv | object | Add extra environment variables to the controller container. | `{}` |
| controller.horizontalPodAutoscaler | object | Set horizontal pod autoscaler for the controller. Note that this does not    affect the data plane. The scaleTargetRef is automatically configured to    target the controller deployment. E.g.:  horizontalPodAutoscaler:   minReplicas: 1   maxReplicas: 5   metrics:     - type: Resource       resource:         name: cpu         target:           type: Utilization           averageUtilization: 80 | `{}` |
| controller.image | object | Configure the controller container image. | `{"pullPolicy":"","registry":"","repository":"kgateway","tag":""}` |
| controller.image.pullPolicy | string | Set the image pull policy for the controller. | `""` |
| controller.image.registry | string | Set the image registry for the controller. | `""` |
| controller.image.repository | string | Set the image repository for the controller. | `"kgateway"` |
| controller.image.tag | string | Set the image tag for the controller. | `""` |
| controller.logLevel | string | Set the log level for the controller. | `"info"` |
| controller.podDisruptionBudget | object | Set pod disruption budget for the controller. Note that this does not    affect the data plane. E.g.:  podDisruptionBudget:   minAvailable: 100% | `{}` |
| controller.priorityClassName | string | Set the priority class name for the controller pod. | `""` |
| controller.replicaCount | int | Set the number of controller pod replicas. | `1` |
| controller.service | object | Controller service configuration. | `{"allocateLoadBalancerNodePorts":null,"annotations":{},"clusterIP":"","clusterIPs":[],"enabled":true,"externalIPs":[],"externalName":"","externalTrafficPolicy":"","extraLabels":{},"healthCheckNodePort":null,"internalTrafficPolicy":"","ipFamilies":[],"ipFamilyPolicy":"","loadBalancerClass":"","loadBalancerIP":"","loadBalancerSourceRanges":[],"ports":{"grpc":9977,"health":9093,"metrics":9092},"publishNotReadyAddresses":false,"sessionAffinity":"","sessionAffinityConfig":{},"trafficDistribution":"","type":"ClusterIP"}` |
| controller.service.allocateLoadBalancerNodePorts | string | Allocate load balancer node ports. | `nil` |
| controller.service.annotations | object | Service annotations. | `{}` |
| controller.service.clusterIP | string | Cluster IP address. | `""` |
| controller.service.clusterIPs | list | Cluster IPs for dual-stack. | `[]` |
| controller.service.enabled | bool | Create the controller Service. | `true` |
| controller.service.externalIPs | list | External IP addresses. | `[]` |
| controller.service.externalName | string | External name for ExternalName services. | `""` |
| controller.service.externalTrafficPolicy | string | External traffic policy. | `""` |
| controller.service.extraLabels | object | Extra labels for the Service. | `{}` |
| controller.service.healthCheckNodePort | string | Health check node port. | `nil` |
| controller.service.internalTrafficPolicy | string | Internal traffic policy. | `""` |
| controller.service.ipFamilies | list | IP families. | `[]` |
| controller.service.ipFamilyPolicy | string | IP family policy. | `""` |
| controller.service.loadBalancerClass | string | Load balancer class. | `""` |
| controller.service.loadBalancerIP | string | Load balancer IP address. | `""` |
| controller.service.loadBalancerSourceRanges | list | Allowed source ranges for load balancer. | `[]` |
| controller.service.ports | object | Service ports. | `{"grpc":9977,"health":9093,"metrics":9092}` |
| controller.service.publishNotReadyAddresses | bool | Publish not ready addresses. | `false` |
| controller.service.sessionAffinity | string | Session affinity. | `""` |
| controller.service.sessionAffinityConfig | object | Session affinity configuration. | `{}` |
| controller.service.trafficDistribution | string | Traffic distribution. | `""` |
| controller.service.type | string | Service type. | `"ClusterIP"` |
| controller.strategy | object | Change the rollout strategy from the Kubernetes default of a RollingUpdate with 25% maxUnavailable, 25% maxSurge. E.g., to recreate pods, minimizing resources for the rollout but causing downtime: strategy:   type: Recreate E.g., to roll out as a RollingUpdate but with non-default parameters: strategy:   type: RollingUpdate   rollingUpdate:     maxSurge: 100% | `{}` |
| controller.verticalPodAutoscaler | object | Set vertical pod autoscaler for the controller. Note that this does not    affect the data plane. The targetRef is automatically configured to    target the controller deployment. E.g.:  verticalPodAutoscaler:   updatePolicy:     updateMode: Auto   resourcePolicy:     containerPolicies:       - containerName: "*"         minAllowed:           cpu: 100m           memory: 128Mi | `{}` |
| controller.xds | object | Configure TLS settings for the xDS gRPC servers. | `{"tls":{"enabled":false}}` |
| controller.xds.tls.enabled | bool | Enable TLS encryption for xDS communication. When enabled, both the main xDS server (port 9977) and agent gateway xDS server (port 9978) will use TLS. When TLS is enabled, you must create a Secret named 'kgateway-xds-cert' in the kgateway installation namespace. The Secret must be of type 'kubernetes.io/tls' with 'tls.crt', 'tls.key', and 'ca.crt' data fields present. | `false` |
| deploymentAnnotations | object | Add annotations to the kgateway deployment. | `{}` |
| discoveryNamespaceSelectors | list | List of namespace selectors (OR'ed): each entry can use 'matchLabels' or 'matchExpressions' (AND'ed within each entry if used together). Kgateway includes the selected namespaces in config discovery. For more information, see the docs https://kgateway.dev/docs/latest/install/advanced/#namespace-discovery. | `[]` |
| fullnameOverride | string | Override the full name of resources created by the Helm chart, which is 'kgateway'. If you set 'fullnameOverride: "foo", the full name of the resources that the Helm release creates become 'foo', such as the deployment, service, and service account for the kgateway control plane in the kgateway-system namespace. | `""` |
| gatewayClassParametersRefs | object | Map of GatewayClass names to GatewayParameters references that will be set on    the default GatewayClasses managed by kgateway. Each entry must define both the    name and namespace of the GatewayParameters resource.    The default GatewayClasses managed by kgateway are:    - kgateway    - kgateway-waypoint    Example:    gatewayClassParametersRefs:      kgateway:        name: shared-gwp        namespace: kgateway-system | `{}` |
| image | object | Configure the default container image for the components that Helm deploys. You can override these settings for each particular component in that component's section, such as 'controller.image' for the kgateway control plane. If you use your own private registry, make sure to include the imagePullSecrets. | `{"pullPolicy":"IfNotPresent","registry":"cr.kgateway.dev/kgateway-dev","tag":""}` |
| image.pullPolicy | string | Set the default image pull policy. | `"IfNotPresent"` |
| image.registry | string | Set the default image registry. | `"cr.kgateway.dev/kgateway-dev"` |
| image.tag | string | Set the default image tag. | `""` |
| imagePullSecrets | list | Set a list of image pull secrets for Kubernetes to use when pulling container images from your own private registry instead of the default kgateway registry. | `[]` |
| inferenceExtension | object | Configure the integration with the Gateway API Inference Extension project, which lets you use kgateway to route to AI inference workloads like LLMs that run locally in your Kubernetes cluster. Documentation for Inference Extension can be found here: https://kgateway.dev/docs/latest/agentgateway/inference/ | `{"enabled":false}` |
| inferenceExtension.enabled | bool | Enable Inference Extension. If enabled, agentgateway.enabled should also be set to true. Enabling inference extension without agentgateway is deprecated in v2.1 and will not be supported in v2.2. | `false` |
| nameOverride | string | Add a name to the default Helm base release, which is 'kgateway'. If you set 'nameOverride: "foo", the name of the resources that the Helm release creates become 'kgateway-foo', such as the deployment, service, and service account for the kgateway control plane in the kgateway-system namespace. | `""` |
| nodeSelector | object | Set node selector labels for pod scheduling, such as 'kubernetes.io/arch: amd64'. | `{}` |
| podAnnotations | object | Add annotations to the kgateway pods. | `{"prometheus.io/scrape":"true"}` |
| podSecurityContext | object | Set the pod-level security context. For example, 'fsGroup: 2000' sets the filesystem group to 2000. | `{}` |
| policyMerge | object | Policy merging settings. Currently, TrafficPolicy's extAuth, extProc, and transformation policies support deep merging. E.g., to enable deep merging of extProc policy in TrafficPolicy: policyMerge:   trafficPolicy:     extProc: DeepMerge | `{}` |
| resources | object | Configure resource requests and limits for the container, such as 'limits.cpu: 100m' or 'requests.memory: 128Mi'. | `{}` |
| securityContext | object | Set the container-level security context, such as 'runAsNonRoot: true'. | `{}` |
| serviceAccount | object | Configure the service account for the deployment. | `{"annotations":{},"create":true,"name":""}` |
| serviceAccount.annotations | object | Add annotations to the service account. | `{}` |
| serviceAccount.create | bool | Specify whether a service account should be created. | `true` |
| serviceAccount.name | string | Set the name of the service account to use. If not set and create is true, a name is generated using the fullname template. | `""` |
| tolerations | list | Set tolerations for pod scheduling, such as 'key: "nvidia.com/gpu"'. | `[]` |
| validation | object | Configure validation behavior for route and policy safety checks in the control plane.    This setting determines how invalid configuration is handled to prevent security bypasses    and to maintain multi-tenant isolation. | `{"level":"standard"}` |
| validation.level | string | Validation level. Accepted values: "standard" or "strict" (case-insensitive).    Standard replaces invalid routes with a direct 500 response and continues applying valid configuration.    Strict adds xDS preflight validation and blocks snapshots that would NACK in Envoy.    Default is "standard". | `"standard"` |
| waypoint | object | Enable the waypoint integration. This enables kgateway to translate istio waypoints and use kgateway as a waypoint in an Istio Ambient service mesh setup. | `{"enabled":false}` |
