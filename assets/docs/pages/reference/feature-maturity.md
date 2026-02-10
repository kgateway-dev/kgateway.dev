Review the feature maturity of the {{< reuse "docs/snippets/kgateway.md" >}} project.

To receive feedback and improve functionality for real use cases, {{< reuse "docs/snippets/kgateway.md" >}} features are often released according to a feature maturity model. As the features are improved and stabilized, they are gradually moved through the stages of alpha, beta, and general availability (GA) support. 

## Maturity stages {#stages}

Review the following table for the comparison points between each stage of maturity.

| Comparison point | Alpha | Beta | GA |
|------------------|-------|------|----|
| API | Can and will likely change | Unlikely to change | No change |
| Implementation | Can and will likely change | Can change, but user experience is maintained | No changes that affect user experience |
| Upgrade paths | Not guaranteed | Not guaranteed | Provided and tested |
| Requests for enhancement (RFEs) and bug fixes | RFEs and bug fixes prioritized | RFEs and bug fixes prioritized | Fully supported |
| Documentation | Not guaranteed and supplied with warnings | Supplied with warnings | Fully supplied |
| Automated testing | Internal testing, but little testing with real use cases | Internal testing and some testing with real use cases | Fully tested and validated with real use cases |
| Suggested usage | Exploration and feedback | Testing setups, demos, and POCs | Production setups |

## Feature maturity {#feature-maturity}

Review the following table for the maturity of features in the {{< reuse "docs/snippets/kgateway.md" >}} project.

| Feature | Maturity |
|---------|----------|
| Core functionality, such as controller and data plane proxy | GA |
| Support for Gateway API | GA`*` |
| GatewayParameters | GA |
| Self-managed proxies | Alpha |
| Backend and BackendConfigPolicy | GA |
| Traffic- and Listener-level policies, including inheritance | GA |
| Access logging | GA |
| Rate limiting GatewayExtension | GA |
| External auth GatewayExtension | GA |
| External processing (ExtProc) GatewayExtension | GA |
| JWT GatewayExtension | GA |
| OAuth2 provider GatewayExtension | GA |
| OpenTelemetry integration | GA |
| AWS NLB/ALB integration | GA |
| AWS Lambda integration | GA |
| Istio ambient and sidecar integration | GA |
| Istio waypoint integration | Alpha |
| AI Gateway integration | N/A (see agentgateway) |
| Inference Extension integration | N/A (see agentgateway) |

`*` For more details about Gateway API support, see the [Kubernetes Gateway API docs](https://gateway-api.sigs.k8s.io/implementations/#kgateway).

## Experimental features in Gateway API {#experimental-features}

{{< reuse "docs/snippets/k8sgwapi-exp.md" >}}
