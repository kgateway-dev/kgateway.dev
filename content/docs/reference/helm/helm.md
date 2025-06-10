# kgateway

A Helm chart for the kgateway project

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | {} | Set affinity rules for pod scheduling, such as 'nodeAffinity:'. |
| agentGateway | object | {"enabled":false} | Agent Gateway lets you use kgateway to help manage agent connectivity across MCP servers, A2A agents, and REST APIs. |
| controller | object | {"extraEnv":{},"image":{"pullPolicy":"","registry":"","repository":"kgateway","tag":""},"logLevel":"info","replicaCount":1,"service":{"ports":{"grpc":9977,"health":9093},"type":"ClusterIP"}} | Configure the kgateway control plane deployment. |
| controller.extraEnv | object | {} | Add extra environment variables to the controller container. |
| controller.image | object | {"pullPolicy":"","registry":"","repository":"kgateway","tag":""} | Configure the controller container image. |
| controller.image.pullPolicy | string | "" | Set the image pull policy for the controller. |
| controller.image.registry | string | "" | Set the image registry for the controller. |
| controller.image.repository | string | "kgateway" | Set the image repository for the controller. |
| controller.image.tag | string | "" | Set the image tag for the controller. |
| controller.logLevel | string | "info" | Set the log level for the controller. |
| controller.replicaCount | int | 1 | Set the number of controller pod replicas. |
| controller.service | object | {"ports":{"grpc":9977,"health":9093},"type":"ClusterIP"} | Configure the controller service. |
| controller.service.ports | object | {"grpc":9977,"health":9093} | Set the service ports for gRPC and health endpoints. |
| controller.service.type | string | "ClusterIP" | Set the service type for the controller. |
| deploymentAnnotations | object | {} | Add annotations to the kgateway deployment. |
| discoveryNamespaceSelectors | list | [] | version: v3 |
| fullnameOverride | string | "" | such as the deployment, service, and service account for the kgateway control plane in the kgateway-system namespace. |
| image | object | {"pullPolicy":"IfNotPresent","registry":"cr.kgateway.dev/kgateway-dev","tag":""} | If you use your own private registry, make sure to include the imagePullSecrets. |
| image.pullPolicy | string | "IfNotPresent" | Set the default image pull policy. |
| image.registry | string | "cr.kgateway.dev/kgateway-dev" | Set the default image registry.  |
| image.tag | string | "" | Set the default image tag. |
| imagePullSecrets | list | [] | Set a list of image pull secrets for Kubernetes to use when pulling container images from your own private registry instead of the default kgateway registry. |
| inferenceExtension | object | {"autoProvision":false,"enabled":false} | With Inference Extension, you can use kgateway to route to AI inference workloads like LLMs that run locally in your Kubernetes cluster. |
| inferenceExtension.autoProvision | bool | false | Enable automatic provisioning for Inference Extension. |
| inferenceExtension.enabled | bool | false | Enable Inference Extension. |
| nameOverride | string | "" | such as the deployment, service, and service account for the kgateway control plane in the kgateway-system namespace. |
| nodeSelector | object | {} | Set node selector labels for pod scheduling, such as 'kubernetes.io/arch: amd64'. |
| podAnnotations | object | {} | Add annotations to the kgateway pods. |
| podSecurityContext | object | {} | For example, 'fsGroup: 2000' sets the filesystem group to 2000. |
| resources | object | {} | Configure resource requests and limits for the container, such as 'limits.cpu: 100m' or 'requests.memory: 128Mi'. |
| securityContext | object | {} | Set the container-level security context, such as 'runAsNonRoot: true'. |
| serviceAccount | object | {"annotations":{},"create":true,"name":""} | Configure the service account for the deployment. |
| serviceAccount.annotations | object | {} | Add annotations to the service account. |
| serviceAccount.create | bool | true | Specify whether a service account should be created. |
| serviceAccount.name | string | "" | If not set and create is true, a name is generated using the fullname template. |
| tolerations | list | [] | Set tolerations for pod scheduling, such as 'key: "nvidia.com/gpu"'. |

