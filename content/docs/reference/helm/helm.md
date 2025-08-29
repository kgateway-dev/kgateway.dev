# kgateway

A Helm chart for the kgateway project

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | {} | Set affinity rules for pod scheduling, such as 'nodeAffinity:'. |
| agentGateway | object | {"enabled":false} | Enable the integration with Agent Gateway, which lets you use kgateway to help manage agent connectivity across MCP servers, A2A agents, and REST APIs. |
| controller | object | {"extraEnv":{},"image":{"pullPolicy":"","registry":"","repository":"kgateway","tag":""},"logLevel":"info","replicaCount":1,"service":{"ports":{"grpc":9977,"health":9093,"metrics":9092},"type":"ClusterIP"}} | Configure the kgateway control plane deployment. |
| controller.extraEnv | object | {} | Add extra environment variables to the controller container. |
| controller.image | object | {"pullPolicy":"","registry":"","repository":"kgateway","tag":""} | Configure the controller container image. |
| controller.image.pullPolicy | string | "" | Set the image pull policy for the controller. |
| controller.image.registry | string | "" | Set the image registry for the controller. |
| controller.image.repository | string | "kgateway" | Set the image repository for the controller. |
| controller.image.tag | string | "" | Set the image tag for the controller. |
| controller.logLevel | string | "info" | Set the log level for the controller. |
| controller.replicaCount | int | 1 | Set the number of controller pod replicas. |
| controller.service | object | {"ports":{"grpc":9977,"health":9093,"metrics":9092},"type":"ClusterIP"} | Configure the controller service. |
| controller.service.ports | object | {"grpc":9977,"health":9093,"metrics":9092} | Set the service ports for gRPC and health endpoints. |
| controller.service.type | string | "ClusterIP" | Set the service type for the controller. |
| deploymentAnnotations | object | {} | Add annotations to the kgateway deployment. |
| discoveryNamespaceSelectors | list | [] | List of namespace selectors (OR'ed): each entry can use 'matchLabels' or 'matchExpressions' (AND'ed within each entry if used together). Kgateway includes the selected namespaces in config discovery. For more information, see the docs https://kgateway.dev/docs/operations/install/#namespace-discovery. |
| fullnameOverride | string | "" | Override the full name of resources created by the Helm chart, which is 'kgateway'. If you set 'fullnameOverride: "foo", the full name of the resources that the Helm release creates become 'foo', such as the deployment, service, and service account for the kgateway control plane in the kgateway-system namespace. |
| image | object | {"pullPolicy":"IfNotPresent","registry":"cr.kgateway.dev/kgateway-dev","tag":""} | Configure the default container image for the components that Helm deploys. You can override these settings for each particular component in that component's section, such as 'controller.image' for the kgateway control plane. If you use your own private registry, make sure to include the imagePullSecrets. |
| image.pullPolicy | string | "IfNotPresent" | Set the default image pull policy. |
| image.registry | string | "cr.kgateway.dev/kgateway-dev" | Set the default image registry. |
| image.tag | string | "" | Set the default image tag. |
| imagePullSecrets | list | [] | Set a list of image pull secrets for Kubernetes to use when pulling container images from your own private registry instead of the default kgateway registry. |
| inferenceExtension | object | {"autoProvision":false,"enabled":false} | Configure the integration with the Gateway API Inference Extension project, which lets you use kgateway to route to AI inference workloads like LLMs that run locally in your Kubernetes cluster. Documentation for Inference Extension can be found here: https://kgateway.dev/docs/integrations/inference-extension/ |
| inferenceExtension.autoProvision | bool | false | Enable automatic provisioning for Inference Extension. |
| inferenceExtension.enabled | bool | false | Enable Inference Extension. |
| nameOverride | string | "" | Add a name to the default Helm base release, which is 'kgateway'. If you set 'nameOverride: "foo", the name of the resources that the Helm release creates become 'kgateway-foo', such as the deployment, service, and service account for the kgateway control plane in the kgateway-system namespace. |
| nodeSelector | object | {} | Set node selector labels for pod scheduling, such as 'kubernetes.io/arch: amd64'. |
| podAnnotations | object | {"prometheus.io/scrape":"true"} | Add annotations to the kgateway pods. |
| podSecurityContext | object | {} | Set the pod-level security context. For example, 'fsGroup: 2000' sets the filesystem group to 2000. |
| policyMerge | object | {} | Policy merging settings. Currently, TrafficPolicy's extAuth, extProc, and transformation policies support deep merging. E.g., to enable deep merging of extProc policy in TrafficPolicy: policyMerge:   trafficPolicy:     extProc: DeepMerge |
| resources | object | {} | Configure resource requests and limits for the container, such as 'limits.cpu: 100m' or 'requests.memory: 128Mi'. |
| securityContext | object | {} | Set the container-level security context, such as 'runAsNonRoot: true'. |
| serviceAccount | object | {"annotations":{},"create":true,"name":""} | Configure the service account for the deployment. |
| serviceAccount.annotations | object | {} | Add annotations to the service account. |
| serviceAccount.create | bool | true | Specify whether a service account should be created. |
| serviceAccount.name | string | "" | Set the name of the service account to use. If not set and create is true, a name is generated using the fullname template. |
| tolerations | list | [] | Set tolerations for pod scheduling, such as 'key: "nvidia.com/gpu"'. |

