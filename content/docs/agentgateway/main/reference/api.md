---
title: API reference
weight: 10
---

{{< reuse "/docs/snippets/api-ref-docs-intro.md" >}}

## Packages
- [agentgateway.dev/v1alpha1](#agentgatewaydevv1alpha1)

## agentgateway.dev/v1alpha1


### Resource Types
- [AgentgatewayBackend](#agentgatewaybackend)
- [AgentgatewayParameters](#agentgatewayparameters)
- [AgentgatewayPolicy](#agentgatewaypolicy)



#### AIBackend



AIBackend specifies the AI backend configuration



_Appears in:_
- [AgentgatewayBackendSpec](#agentgatewaybackendspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `provider` _[LLMProvider](#llmprovider)_ | provider specifies configuration for how to reach the configured LLM provider. |  |  |
| `groups` _[PriorityGroup](#prioritygroup) array_ | groups specifies a list of groups in priority order where each group defines<br />a set of LLM providers. The priority determines the priority of the backend endpoints chosen.<br />Note: provider names must be unique across all providers in all priority groups. Backend policies<br />may target a specific provider by name using targetRefs[].sectionName.<br /><br />Example configuration with two priority groups:<br />```yaml<br />groups:<br />- providers:<br />  - azureopenai:<br />      deploymentName: gpt-4o-mini<br />      apiVersion: 2024-02-15-preview<br />      endpoint: ai-gateway.openai.azure.com<br />- providers:<br />  - azureopenai:<br />      deploymentName: gpt-4o-mini-2<br />      apiVersion: 2024-02-15-preview<br />      endpoint: ai-gateway-2.openai.azure.com<br />     policies:<br />       auth:<br />         secretRef:<br />           name: azure-secret<br />```<br />TODO: enable this rule when we don't need to support older k8s versions where this rule breaks // +kubebuilder:validation:XValidation:message="provider names must be unique across groups",rule="self.map(pg, pg.providers.map(pp, pp.name)).map(p, self.map(pg, pg.providers.map(pp, pp.name)).filter(cp, cp != p).exists(cp, p.exists(pn, pn in cp))).exists(p, !p)" |  | MaxItems: 32 <br />MinItems: 1 <br /> |


#### AIPromptEnrichment



AIPromptEnrichment defines the config to enrich requests sent to the LLM provider by appending and prepending system prompts.


Prompt enrichment allows you to add additional context to the prompt before sending it to the model.
Unlike RAG or other dynamic context methods, prompt enrichment is static and is applied to every request.


**Note**: Some providers, including Anthropic, do not support SYSTEM role messages, and instead have a dedicated
system field in the input JSON. In this case, use the [`defaults` setting](#fielddefault) to set the system field.


The following example prepends a system prompt of `Answer all questions in French.`
and appends `Describe the painting as if you were a famous art critic from the 17th century.`
to each request that is sent to the `openai` HTTPRoute.
```yaml


	name: openai-opt
	namespace: kgateway-system


spec:


	targetRefs:
	- group: gateway.networking.k8s.io
	  kind: HTTPRoute
	  name: openai
	ai:
	    promptEnrichment:
	      prepend:
	      - role: SYSTEM
	        content: "Answer all questions in French."
	      append:
	      - role: USER
	        content: "Describe the painting as if you were a famous art critic from the 17th century."


```



_Appears in:_
- [BackendAI](#backendai)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `prepend` _[Message](#message) array_ | A list of messages to be prepended to the prompt sent by the client. |  |  |
| `append` _[Message](#message) array_ | A list of messages to be appended to the prompt sent by the client. |  |  |


#### AIPromptGuard



AIPromptGuard configures a prompt guards to block unwanted requests to the LLM provider and mask sensitive data.
Prompt guards can be used to reject requests based on the content of the prompt, as well as
mask responses based on the content of the response.


This example rejects any request prompts that contain
the string "credit card", and masks any credit card numbers in the response.
```yaml
promptGuard:


	request:
	- response:
	    message: "Rejected due to inappropriate content"
	  regex:
	    action: REJECT
	    matches:
	    - pattern: "credit card"
	      name: "CC"
	response:
	- regex:
	    builtins:
	    - CREDIT_CARD
	    action: MASK


```



_Appears in:_
- [BackendAI](#backendai)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `request` _[PromptguardRequest](#promptguardrequest) array_ | Prompt guards to apply to requests sent by the client. |  | MaxItems: 8 <br />MinItems: 1 <br /> |
| `response` _[PromptguardResponse](#promptguardresponse) array_ | Prompt guards to apply to responses returned by the LLM provider. |  | MaxItems: 8 <br />MinItems: 1 <br /> |


#### APIKeyAuthentication







_Appears in:_
- [Traffic](#traffic)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `mode` _[APIKeyAuthenticationMode](#apikeyauthenticationmode)_ | Validation mode for api key authentication. | Strict | Enum: [Strict Optional] <br /> |
| `secretRef` _[LocalObjectReference](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#localobjectreference-v1-core)_ | secretRef references a Kubernetes secret storing a set of API Keys. If there are many keys, 'secretSelector' can be<br />used instead.<br /><br />Each entry in the Secret represents one API Key. The key is an arbitrary identifier. The value can either be:<br />* A string, representing the API Key.<br />* A JSON object, with two fields, `key` and `metadata`. `key` contains the API Key. `metadata` contains arbitrary JSON<br />  metadata associated with the key, which may be used by other policies. For example, you may write an authorization<br />  policy allow `apiKey.group == 'sales'`.<br /><br />Example:<br /><br />apiVersion: v1<br />kind: Secret<br />metadata:<br />  name: api-key<br />stringData:<br />  client1: \|<br />    \{<br />      "key": "k-123",<br />      "metadata": \{<br />        "group": "sales",<br />        "created_at": "2024-10-01T12:00:00Z",<br />      \}<br />    \}<br />  client2: "k-456" |  |  |
| `secretSelector` _[SecretSelector](#secretselector)_ | secretSelector selects multiple secrets containing API Keys. If the same key is defined in multiple secrets, the<br />behavior is undefined.<br /><br />Each entry in the Secret represents one API Key. The key is an arbitrary identifier. The value can either be:<br />* A string, representing the API Key.<br />* A JSON object, with two fields, `key` and `metadata`. `key` contains the API Key. `metadata` contains arbitrary JSON<br />  metadata associated with the key, which may be used by other policies. For example, you may write an authorization<br />  policy allow `apiKey.group == 'sales'`.<br /><br />Example:<br /><br />apiVersion: v1<br />kind: Secret<br />metadata:<br />  name: api-key<br />stringData:<br />  client1: \|<br />    \{<br />      "key": "k-123",<br />      "metadata": \{<br />        "group": "sales",<br />        "created_at": "2024-10-01T12:00:00Z",<br />      \}<br />    \}<br />  client2: "k-456" |  |  |


#### APIKeyAuthenticationMode

_Underlying type:_ _string_



_Validation:_
- Enum: [Strict Optional]

_Appears in:_
- [APIKeyAuthentication](#apikeyauthentication)

| Field | Description |
| --- | --- |
| `Strict` | A valid API Key must be present.<br />This is the default option.<br /> |
| `Optional` | If an API Key exists, validate it.<br />Warning: this allows requests without an API Key!<br /> |


#### AWSGuardrailConfig







_Appears in:_
- [BedrockConfig](#bedrockconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `identifier` _string_ | GuardrailIdentifier is the identifier of the Guardrail policy to use for the backend. |  |  |
| `version` _string_ | GuardrailVersion is the version of the Guardrail policy to use for the backend. |  |  |


#### AccessLog



accessLogs specifies how per-request access logs are emitted.



_Appears in:_
- [Frontend](#frontend)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `filter` _[CELExpression](#celexpression)_ | filter specifies a CEL expression that is used to filter logs. A log will only be emitted if the expression evaluates<br />to 'true'. |  |  |
| `attributes` _[LogTracingAttributes](#logtracingattributes)_ | attributes specifies customizations to the key-value pairs that are logged |  |  |


#### Action

_Underlying type:_ _string_

Action to take if a regex pattern is matched in a request or response.
This setting applies only to request matches. PromptguardResponse matches are always masked by default.



_Appears in:_
- [Regex](#regex)

| Field | Description |
| --- | --- |
| `MASK` | Mask the matched data in the request.<br /> |
| `REJECT` | Reject the request if the regex matches content in the request.<br /> |


#### AgentgatewayBackend









| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `agentgateway.dev/v1alpha1` | | |
| `kind` _string_ | `AgentgatewayBackend` | | |
| `kind` _string_ | Kind is a string value representing the REST resource this object represents.<br />Servers may infer this from the endpoint the client submits requests to.<br />Cannot be updated.<br />In CamelCase.<br />More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds |  |  |
| `apiVersion` _string_ | APIVersion defines the versioned schema of this representation of an object.<br />Servers should convert recognized schemas to the latest internal value, and<br />may reject unrecognized values.<br />More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources |  |  |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[AgentgatewayBackendSpec](#agentgatewaybackendspec)_ | spec defines the desired state of AgentgatewayBackend. |  |  |
| `status` _[AgentgatewayBackendStatus](#agentgatewaybackendstatus)_ | status defines the current state of AgentgatewayBackend. |  |  |


#### AgentgatewayBackendSpec







_Appears in:_
- [AgentgatewayBackend](#agentgatewaybackend)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `static` _[StaticBackend](#staticbackend)_ | static represents a static hostname. |  |  |
| `ai` _[AIBackend](#aibackend)_ | ai represents a LLM backend. |  |  |
| `mcp` _[MCPBackend](#mcpbackend)_ | mcp represents an MCP backend |  |  |
| `dynamicForwardProxy` _[DynamicForwardProxyBackend](#dynamicforwardproxybackend)_ | dynamicForwardProxy configures the proxy to dynamically send requests to the destination based on the incoming<br />request HTTP host header, or TLS SNI for TLS traffic.<br /><br />Note: this Backend type enables users to send trigger the proxy to send requests to arbitrary destinations. Proper<br />access controls must be put in place when using this backend type. |  |  |
| `policies` _[BackendFull](#backendfull)_ | policies controls policies for communicating with this backend. Policies may also be set in AgentgatewayPolicy;<br />policies are merged on a field-level basis, with policies on the Backend (this field) taking precedence. |  |  |


#### AgentgatewayBackendStatus



AgentgatewayBackend defines the observed state of AgentgatewayBackend.



_Appears in:_
- [AgentgatewayBackend](#agentgatewaybackend)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `conditions` _[Condition](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#condition-v1-meta) array_ | Conditions is the list of conditions for the backend. |  | MaxItems: 8 <br /> |


#### AgentgatewayParameters









| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `agentgateway.dev/v1alpha1` | | |
| `kind` _string_ | `AgentgatewayParameters` | | |
| `kind` _string_ | Kind is a string value representing the REST resource this object represents.<br />Servers may infer this from the endpoint the client submits requests to.<br />Cannot be updated.<br />In CamelCase.<br />More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds |  |  |
| `apiVersion` _string_ | APIVersion defines the versioned schema of this representation of an object.<br />Servers should convert recognized schemas to the latest internal value, and<br />may reject unrecognized values.<br />More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources |  |  |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[AgentgatewayParametersSpec](#agentgatewayparametersspec)_ | spec defines the desired state of AgentgatewayParameters. |  |  |
| `status` _[AgentgatewayParametersStatus](#agentgatewayparametersstatus)_ | status defines the current state of AgentgatewayParameters. |  |  |


#### AgentgatewayParametersConfigs







_Appears in:_
- [AgentgatewayParametersSpec](#agentgatewayparametersspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `logging` _[AgentgatewayParametersLogging](#agentgatewayparameterslogging)_ | logging configuration for Agentgateway. By default, all logs are set to "info" level. |  |  |
| `rawConfig` _[JSON](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#json-v1-apiextensions-k8s-io)_ | rawConfig provides an opaque mechanism to configure the agentgateway<br />config file (the agentgateway binary has a '-f' option to specify a<br />config file, and this is that file).  This will be merged with<br />configuration derived from typed fields like<br />AgentgatewayParametersLogging.Format, and those typed fields will take<br />precedence.<br /><br />Example:<br />  rawConfig:<br />    binds:<br />    - port: 3000<br />      listeners:<br />      - routes:<br />        - policies:<br />            cors:<br />              allowOrigins:<br />                - "*"<br />              allowHeaders:<br />                - mcp-protocol-version<br />                - content-type<br />                - cache-control<br />          backends:<br />          - mcp:<br />              targets:<br />              - name: everything<br />                stdio:<br />                  cmd: npx<br />                  args: ["@modelcontextprotocol/server-everything"] |  | Type: object <br /> |
| `image` _[Image](#image)_ | The agentgateway container image. See<br />https://kubernetes.io/docs/concepts/containers/images<br />for details.<br /><br />Default values, which may be overridden individually:<br /><br />	registry: ghcr.io/agentgateway<br />	repository: agentgateway<br />	tag: <agentgateway version><br />	pullPolicy: <omitted, relying on Kubernetes defaults which depend on the tag> |  |  |
| `env` _[EnvVar](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#envvar-v1-core) array_ | The container environment variables. These override any existing<br />values. If you want to delete an environment variable entirely, use<br />`$patch: delete` with AgentgatewayParametersOverlays instead. Note that<br />[variable<br />expansion](https://kubernetes.io/docs/tasks/inject-data-application/define-interdependent-environment-variables/)<br />does apply, but is highly discouraged -- to set dependent environment<br />variables, you can use $(VAR_NAME), but it's highly<br />discouraged. `$$(VAR_NAME)` avoids expansion and results in a literal<br />`$(VAR_NAME)`. |  |  |
| `resources` _[ResourceRequirements](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#resourcerequirements-v1-core)_ | The compute resources required by this container. See<br />https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/<br />for details. |  |  |
| `shutdown` _[ShutdownSpec](#shutdownspec)_ | Shutdown delay configuration.  How graceful planned or unplanned data<br />plane changes happen is in tension with how quickly rollouts of the data<br />plane complete. How long a data plane pod must wait for shutdown to be<br />perfectly graceful depends on how you have configured your Gateways. |  |  |


#### AgentgatewayParametersLogging







_Appears in:_
- [AgentgatewayParametersConfigs](#agentgatewayparametersconfigs)
- [AgentgatewayParametersSpec](#agentgatewayparametersspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `level` _string_ | Logging level in standard RUST_LOG syntax, e.g. 'info', the default, or<br />by module, comma-separated. E.g.,<br />"rmcp=warn,hickory_server::server::server_future=off,typespec_client_core::http::policies::logging=warn" |  |  |
| `format` _[AgentgatewayParametersLoggingFormat](#agentgatewayparametersloggingformat)_ |  |  | Enum: [json text] <br /> |


#### AgentgatewayParametersLoggingFormat

_Underlying type:_ _string_

The default logging format is text.

_Validation:_
- Enum: [json text]

_Appears in:_
- [AgentgatewayParametersLogging](#agentgatewayparameterslogging)

| Field | Description |
| --- | --- |
| `json` |  |
| `text` |  |


#### AgentgatewayParametersObjectMetadata







_Appears in:_
- [KubernetesResourceOverlay](#kubernetesresourceoverlay)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `labels` _object (keys:string, values:string)_ | Map of string keys and values that can be used to organize and categorize<br />(scope and select) objects. May match selectors of replication controllers<br />and services.<br />More info: https://kubernetes.io/docs/concepts/overview/working-with-objects/labels |  |  |
| `annotations` _object (keys:string, values:string)_ | Annotations is an unstructured key value map stored with a resource that may be<br />set by external tools to store and retrieve arbitrary metadata. They are not<br />queryable and should be preserved when modifying objects.<br />More info: https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations |  |  |


#### AgentgatewayParametersOverlays







_Appears in:_
- [AgentgatewayParametersSpec](#agentgatewayparametersspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `deployment` _[KubernetesResourceOverlay](#kubernetesresourceoverlay)_ | deployment allows specifying overrides for the generated Deployment resource. |  |  |
| `service` _[KubernetesResourceOverlay](#kubernetesresourceoverlay)_ | service allows specifying overrides for the generated Service resource. |  |  |
| `serviceAccount` _[KubernetesResourceOverlay](#kubernetesresourceoverlay)_ | serviceAccount allows specifying overrides for the generated ServiceAccount resource. |  |  |


#### AgentgatewayParametersSpec







_Appears in:_
- [AgentgatewayParameters](#agentgatewayparameters)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `logging` _[AgentgatewayParametersLogging](#agentgatewayparameterslogging)_ | logging configuration for Agentgateway. By default, all logs are set to "info" level. |  |  |
| `rawConfig` _[JSON](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#json-v1-apiextensions-k8s-io)_ | rawConfig provides an opaque mechanism to configure the agentgateway<br />config file (the agentgateway binary has a '-f' option to specify a<br />config file, and this is that file).  This will be merged with<br />configuration derived from typed fields like<br />AgentgatewayParametersLogging.Format, and those typed fields will take<br />precedence.<br /><br />Example:<br />  rawConfig:<br />    binds:<br />    - port: 3000<br />      listeners:<br />      - routes:<br />        - policies:<br />            cors:<br />              allowOrigins:<br />                - "*"<br />              allowHeaders:<br />                - mcp-protocol-version<br />                - content-type<br />                - cache-control<br />          backends:<br />          - mcp:<br />              targets:<br />              - name: everything<br />                stdio:<br />                  cmd: npx<br />                  args: ["@modelcontextprotocol/server-everything"] |  | Type: object <br /> |
| `image` _[Image](#image)_ | The agentgateway container image. See<br />https://kubernetes.io/docs/concepts/containers/images<br />for details.<br /><br />Default values, which may be overridden individually:<br /><br />	registry: ghcr.io/agentgateway<br />	repository: agentgateway<br />	tag: <agentgateway version><br />	pullPolicy: <omitted, relying on Kubernetes defaults which depend on the tag> |  |  |
| `env` _[EnvVar](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#envvar-v1-core) array_ | The container environment variables. These override any existing<br />values. If you want to delete an environment variable entirely, use<br />`$patch: delete` with AgentgatewayParametersOverlays instead. Note that<br />[variable<br />expansion](https://kubernetes.io/docs/tasks/inject-data-application/define-interdependent-environment-variables/)<br />does apply, but is highly discouraged -- to set dependent environment<br />variables, you can use $(VAR_NAME), but it's highly<br />discouraged. `$$(VAR_NAME)` avoids expansion and results in a literal<br />`$(VAR_NAME)`. |  |  |
| `resources` _[ResourceRequirements](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#resourcerequirements-v1-core)_ | The compute resources required by this container. See<br />https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/<br />for details. |  |  |
| `shutdown` _[ShutdownSpec](#shutdownspec)_ | Shutdown delay configuration.  How graceful planned or unplanned data<br />plane changes happen is in tension with how quickly rollouts of the data<br />plane complete. How long a data plane pod must wait for shutdown to be<br />perfectly graceful depends on how you have configured your Gateways. |  |  |
| `deployment` _[KubernetesResourceOverlay](#kubernetesresourceoverlay)_ | deployment allows specifying overrides for the generated Deployment resource. |  |  |
| `service` _[KubernetesResourceOverlay](#kubernetesresourceoverlay)_ | service allows specifying overrides for the generated Service resource. |  |  |
| `serviceAccount` _[KubernetesResourceOverlay](#kubernetesresourceoverlay)_ | serviceAccount allows specifying overrides for the generated ServiceAccount resource. |  |  |


#### AgentgatewayParametersStatus



The current conditions of the AgentgatewayParameters. This is not currently implemented.



_Appears in:_
- [AgentgatewayParameters](#agentgatewayparameters)



#### AgentgatewayPolicy









| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `agentgateway.dev/v1alpha1` | | |
| `kind` _string_ | `AgentgatewayPolicy` | | |
| `kind` _string_ | Kind is a string value representing the REST resource this object represents.<br />Servers may infer this from the endpoint the client submits requests to.<br />Cannot be updated.<br />In CamelCase.<br />More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds |  |  |
| `apiVersion` _string_ | APIVersion defines the versioned schema of this representation of an object.<br />Servers should convert recognized schemas to the latest internal value, and<br />may reject unrecognized values.<br />More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources |  |  |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[AgentgatewayPolicySpec](#agentgatewaypolicyspec)_ | spec defines the desired state of AgentgatewayPolicy. |  |  |
| `status` _[PolicyStatus](#policystatus)_ | status defines the current state of AgentgatewayPolicy. |  |  |


#### AgentgatewayPolicySpec







_Appears in:_
- [AgentgatewayPolicy](#agentgatewaypolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `targetRefs` _LocalPolicyTargetReferenceWithSectionName array_ | targetRefs specifies the target resources by reference to attach the policy to. |  | MaxItems: 16 <br />MinItems: 1 <br /> |
| `targetSelectors` _LocalPolicyTargetSelectorWithSectionName array_ | targetSelectors specifies the target selectors to select resources to attach the policy to. |  | MaxItems: 16 <br />MinItems: 1 <br /> |
| `frontend` _[Frontend](#frontend)_ | frontend defines settings for how to handle incoming traffic.<br /><br />A frontend policy can only target a Gateway. Listener and ListenerSet are not valid targets.<br /><br />When multiple policies are selected for a given request, they are merged on a field-level basis, but not a deep<br />merge. For example, policy A sets 'tcp' and 'tls', and policy B sets 'tls', the effective policy would be 'tcp' from<br />policy A, and 'tls' from policy B. |  |  |
| `traffic` _[Traffic](#traffic)_ | traffic defines settings for how process traffic.<br /><br />A traffic policy can target a Gateway (optionally, with a sectionName indicating the listener), ListenerSet, Route<br />(optionally, with a sectionName indicating the route rule).<br /><br />When multiple policies are selected for a given request, they are merged on a field-level basis, but not a deep<br />merge. Precedence is given to more precise policies: Gateway < Listener < Route < Route Rule. For example, policy A<br />sets 'timeouts' and 'retries', and policy B sets 'retries', the effective policy would be 'timeouts' from policy A,<br />and 'retries' from policy B. |  |  |
| `backend` _[BackendFull](#backendfull)_ | backend defines settings for how to connect to destination backends.<br /><br />A backend policy can target a Gateway (optionally, with a sectionName indicating the listener), ListenerSet, Route<br />(optionally, with a sectionName indicating the route rule), or a Service/Backend (optionally, with a sectionName<br />indicating the port (for Service) or sub-backend (for Backend).<br /><br />Note that a backend policy applies when connecting to a specific destination backend. Targeting a higher level<br />resource, like Gateway, is just a way to easily apply a policy to a group of backends.<br /><br />When multiple policies are selected for a given request, they are merged on a field-level basis, but not a deep<br />merge. Precedence is given to more precise policies: Gateway < Listener < Route < Route Rule < Backend/Service. For<br />example, if a Gateway policy sets 'tcp' and 'tls', and a Backend policy sets 'tls', the effective policy would be<br />'tcp' from the Gateway, and 'tls' from the Backend. |  |  |


#### AnthropicConfig



AnthropicConfig settings for the [Anthropic](https://docs.anthropic.com/en/release-notes/api) LLM provider.



_Appears in:_
- [LLMProvider](#llmprovider)
- [NamedLLMProvider](#namedllmprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `model` _string_ | Optional: Override the model name, such as `gpt-4o-mini`.<br />If unset, the model name is taken from the request. |  |  |


#### AttributeAdd







_Appears in:_
- [LogTracingAttributes](#logtracingattributes)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ |  |  |  |
| `expression` _[CELExpression](#celexpression)_ |  |  |  |


#### AzureOpenAIConfig



AzureOpenAIConfig settings for the [Azure OpenAI](https://learn.microsoft.com/en-us/azure/ai-services/openai/) LLM provider.



_Appears in:_
- [LLMProvider](#llmprovider)
- [NamedLLMProvider](#namedllmprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `endpoint` _string_ | The endpoint for the Azure OpenAI API to use, such as `my-endpoint.openai.azure.com`.<br />If the scheme is included, it is stripped. |  | MinLength: 1 <br /> |
| `deploymentName` _string_ | The name of the Azure OpenAI model deployment to use.<br />For more information, see the [Azure OpenAI model docs](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models).<br />This is required if ApiVersion is not 'v1'. For v1, the model can be set in the request. |  | MinLength: 1 <br /> |
| `apiVersion` _string_ | The version of the Azure OpenAI API to use.<br />For more information, see the [Azure OpenAI API version reference](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#api-specs).<br />If unset, defaults to "v1" |  |  |






#### BackendAI


_Appears in:_
- [Various types](#various-types)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `prompt` _[AIPromptEnrichment](#aipromptenrichment)_ | Enrich requests sent to the LLM provider by appending and prepending system prompts. This can be configured only for LLM providers that use the `CHAT` or `CHAT_STREAMING` API route type. |  | Optional |
| `promptGuard` _[AIPromptGuard](#aipromptguard)_ | promptGuard enables adding guardrails to LLM requests and responses. |  | Optional |
| `defaults` _[FieldDefault](#fielddefault)_ array | Provide defaults to merge with user input fields. If the field is already set, the field in the request is used. |  | Optional <br />MinItems: 1 <br />MaxItems: 64 |
| `overrides` _[FieldDefault](#fielddefault)_ array | Provide overrides to merge with user input fields. If the field is already set, the field will be overwritten. |  | Optional <br />MinItems: 1 <br />MaxItems: 64 |
| `modelAliases` object (keys:string, values:_[string](#string)_) | ModelAliases maps friendly model names to actual provider model names. Example: {"fast": "gpt-3.5-turbo", "smart": "gpt-4-turbo"} Note: This field is only applicable when using the agentgateway data plane. |  | Optional <br />MinItems: 1 <br />MaxItems: 64 |
| `promptCaching` _[PromptCachingConfig](#promptcachingconfig)_ | promptCaching enables automatic prompt caching for supported providers (AWS Bedrock). Reduces API costs by caching static content like system prompts and tool definitions. Only applicable for Bedrock Claude 3+ and Nova models. |  | Optional |
| `routes` object (keys:string, values:_[RouteType](#routetype)_) | routes defines how to identify the type of traffic to handle. The keys are URL path suffixes matched using ends-with comparison (e.g., "/v1/chat/completions"). The special "*" wildcard matches any path. If not specified, all traffic defaults to "completions" type. |  | Optional |

#### BackendAuth


_Appears in:_
- [Various types](#various-types)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `key` _[string](#string)_ | key provides an inline key to use as the value of the Authorization header. This option is the least secure; usage of a Secret is preferred. |  | Optional <br />MaxLength: 2048 |
| `secretRef` _[LocalObjectReference](#localobjectreference)_ | secretRef references a Kubernetes secret storing the key to use the authorization value. This must be stored in the 'Authorization' key. |  | Optional <br />MaxLength: 2048 |
| `passthrough` _[BackendAuthPassthrough](#backendauthpassthrough)_ | passthrough passes through an existing token that has been sent by the client and validated. Other policies, like JWT and API Key authentication, will strip the original client credentials. Passthrough backend authentication causes the original token to be added back into the request. If there are no client authentication policies on the request, the original token would be unchanged, so this would have no effect. |  | Optional |

#### BackendAuthPassthrough







_Appears in:_
- [BackendAuth](#backendauth)



#### BackendFull







_Appears in:_
- [AgentgatewayBackendSpec](#agentgatewaybackendspec)
- [AgentgatewayPolicySpec](#agentgatewaypolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `ai` _[BackendAI](#backendai)_ | ai specifies settings for AI workloads. This is only applicable when connecting to a Backend of type 'ai'. |  |  |
| `mcp` _[BackendMCP](#backendmcp)_ | mcp specifies settings for MCP workloads. This is only applicable when connecting to a Backend of type 'mcp'. |  |  |






#### BackendHTTP


_Appears in:_
- [Various types](#various-types)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `version` _[HTTPVersion](#httpversion)_ | version specifies the HTTP protocol version to use when connecting to the backend. If not specified, the version is automatically determined: * Service types can specify it with 'appProtocol' on the Service port. * If traffic is identified as gRPC, HTTP2 is used. * If the incoming traffic was plaintext HTTP, the original protocol will be used. * If the incoming traffic was HTTPS, HTTP1 will be used. This is because most clients will transparently upgrade HTTPS traffic to HTTP2, even if the backend doesn't support it |  | Optional <br />Enum: [HTTP1;HTTP2
	// +optional
] |

#### BackendMCP


_Appears in:_
- [Various types](#various-types)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `authorization` _[Authorization](#authorization)_ | authorization defines MCPBackend level authorization. Unlike authorization at the HTTP level, which will reject unauthorized requests with a 403 error, this policy works at the MCPBackend level.  List operations, such as list_tools, will have each item evaluated. Items that do not meet the rule will be filtered.  Get or call operations, such as call_tool, will evaluate the specific item and reject requests that do not meet the rule. |  | Optional |
| `authentication` _[MCPAuthentication](#mcpauthentication)_ | authentication defines MCPBackend specific authentication rules. |  | Optional |

#### BackendSimple


_Appears in:_
- [BackendFull](#backendfull)
- [BackendWithAI](#backendwithai)
- [BackendWithMCP](#backendwithmcp)
- [OpenAIModeration](#openaimoderation)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `tcp` _[BackendTCP](#backendtcp)_ | tcp defines settings for managing TCP connections to the backend. |  | Optional |
| `tls` _[BackendTLS](#backendtls)_ | tls defines settings for managing TLS connections to the backend.  If this field is set, TLS will be initiated to the backend; the system trusted CA certificates will be used to validate the server, and the SNI will automatically be set based on the destination. |  | Optional |
| `http` _[BackendHTTP](#backendhttp)_ | http defines settings for managing HTTP requests to the backend. |  | Optional |
| `auth` _[BackendAuth](#backendauth)_ | auth defines settings for managing authentication to the backend |  | Optional |
#### BackendTCP


_Appears in:_
- [Various types](#various-types)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `keepalive` _[Keepalive](#keepalive)_ | keepAlive defines settings for enabling TCP keepalives on the connection. |  | Optional |
| `connectTimeout` _[Duration](#duration)_ | connectTimeout defines the deadline for establishing a connection to the destination. |  | Optional <br />XValidation |

#### BackendTLS


_Appears in:_
- [Various types](#various-types)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `mtlsCertificateRef` _[LocalObjectReference](#localobjectreference)_ array | mtlsCertificateRef enables mutual TLS to the backend, using the specified key (tls.key) and cert (tls.crt) from the refenced Secret.  An optional 'ca.cert' field, if present, will be used to verify the server certificate if present. If caCertificateRefs is also specified, the caCertificateRefs field takes priority.  If unspecified, no client certificate will be used.  |  | Optional <br />MaxItems: 1 |
| `caCertificateRefs` _[LocalObjectReference](#localobjectreference)_ array | caCertificateRefs defines the CA certificate ConfigMap to use to verify the server certificate. If unset, the system's trusted certificates are used.  |  | Optional <br />MaxItems: 1 |
| `insecureSkipVerify` _[InsecureTLSMode](#insecuretlsmode)_ | insecureSkipVerify originates TLS but skips verification of the backend's certificate. WARNING: This is an insecure option that should only be used if the risks are understood.  There are two modes: * All disables all TLS verification * Hostname verifies the CA certificate is trusted, but ignores any mismatch of hostname/SANs. Note that this method is still insecure; prefer setting verifySubjectAltNames to customize the valid hostnames if possible.  |  | Optional <br />Enum: [All;Hostname
	// +optional
] |
| `sni` _[SNI](#sni)_ | sni specifies the Server Name Indicator (SNI) to be used in the TLS handshake. If unset, the SNI is automatically set based on the destination hostname. |  | Optional <br />Enum: [All;Hostname
	// +optional
	InsecureSkipVerify *InsecureTLSMode `json:"insecureSkipVerify,omitempty"`

	// sni specifies the Server Name Indicator (SNI) to be used in the TLS handshake. If unset, the SNI is automatically
	// set based on the destination hostname.
	// +optional
] |
| `verifySubjectAltNames` _[ShortString](#shortstring)_ array | verifySubjectAltNames specifies the Subject Alternative Names (SAN) to verify in the server certificate. If not present, the destination hostname is automatically used.  |  | Optional <br />MinItems: 1 <br />MaxItems: 16 |
| `alpnProtocols` _[[]TinyString](#[]tinystring)_ | alpnProtocols sets the Application Level Protocol Negotiation (ALPN) value to use in the TLS handshake.  If not present, defaults to ["h2", "http/1.1"].  |  | Optional <br />MinItems: 1 <br />MaxItems: 16 |

#### BackendWithAI







_Appears in:_
- [NamedLLMProvider](#namedllmprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `ai` _[BackendAI](#backendai)_ | ai specifies settings for AI workloads. This is only applicable when connecting to a Backend of type 'ai'. |  |  |


#### BackendWithMCP







_Appears in:_
- [McpTarget](#mcptarget)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `mcp` _[BackendMCP](#backendmcp)_ | mcp specifies settings for MCP workloads. This is only applicable when connecting to a Backend of type 'mcp'. |  |  |


#### BasicAuthentication







_Appears in:_
- [Traffic](#traffic)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `mode` _[BasicAuthenticationMode](#basicauthenticationmode)_ | validation mode for basic auth authentication. | Strict | Enum: [Strict Optional] <br /> |
| `realm` _string_ | realm specifies the 'realm' to return in the WWW-Authenticate header for failed authentication requests.<br />If unset, "Restricted" will be used. |  |  |
| `users` _string array_ | users provides an inline list of username/password pairs that will be accepted.<br />Each entry represents one line of the htpasswd format: https://httpd.apache.org/docs/2.4/programs/htpasswd.html.<br /><br />Note: passwords should be the hash of the password, not the raw password. Use the `htpasswd` or similar commands<br />to generate a hash. MD5, bcrypt, crypt, and SHA-1 are supported.<br /><br />Example:<br />users:<br />- "user1:$apr1$ivPt0D4C$DmRhnewfHRSrb3DQC.WHC."<br />- "user2:$2y$05$r3J4d3VepzFkedkd/q1vI.pBYIpSqjfN0qOARV3ScUHysatnS0cL2" |  | MaxItems: 256 <br />MinItems: 1 <br /> |
| `secretRef` _[LocalObjectReference](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#localobjectreference-v1-core)_ | secretRef references a Kubernetes secret storing the .htaccess file. The Secret must have a key named '.htaccess',<br />and should contain the complete .htaccess file.<br /><br />Note: passwords should be the hash of the password, not the raw password. Use the `htpasswd` or similar commands<br />to generate a hash. MD5, bcrypt, crypt, and SHA-1 are supported.<br /><br />Example:<br /><br />apiVersion: v1<br />kind: Secret<br />metadata:<br />  name: basic-auth<br />stringData:<br />  .htaccess: \|<br />    alice:$apr1$3zSE0Abt$IuETi4l5yO87MuOrbSE4V.<br />    bob:$apr1$Ukb5LgRD$EPY2lIfY.A54jzLELNIId/ |  |  |


#### BasicAuthenticationMode

_Underlying type:_ _string_



_Validation:_
- Enum: [Strict Optional]

_Appears in:_
- [BasicAuthentication](#basicauthentication)

| Field | Description |
| --- | --- |
| `Strict` | A valid username and password must be present.<br />This is the default option.<br /> |
| `Optional` | If a username and password exists, validate it.<br />Warning: this allows requests without a username!<br /> |


#### BedrockConfig







_Appears in:_
- [LLMProvider](#llmprovider)
- [NamedLLMProvider](#namedllmprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `region` _string_ | Region is the AWS region to use for the backend.<br />Defaults to us-east-1 if not specified. | us-east-1 | MaxLength: 63 <br />MinLength: 1 <br />Pattern: `^[a-z0-9-]+$` <br /> |
| `model` _string_ | Optional: Override the model name, such as `gpt-4o-mini`.<br />If unset, the model name is taken from the request. |  |  |
| `guardrail` _[AWSGuardrailConfig](#awsguardrailconfig)_ | Guardrail configures the Guardrail policy to use for the backend. See <https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html><br />If not specified, the AWS Guardrail policy will not be used. |  |  |


#### BuiltIn

_Underlying type:_ _string_

BuiltIn regex patterns for specific types of strings in prompts.
For example, if you specify `CreditCard`, any credit card numbers
in the request or response are matched.

_Validation:_
- Enum: [Ssn CreditCard PhoneNumber Email]

_Appears in:_
- [Regex](#regex)

| Field | Description |
| --- | --- |
| `Ssn` | Default regex matching for Social Security numbers.<br /> |
| `CreditCard` | Default regex matching for credit card numbers.<br /> |
| `PhoneNumber` | Default regex matching for phone numbers.<br /> |
| `Email` | Default regex matching for email addresses.<br /> |


#### CORS







_Appears in:_
- [Traffic](#traffic)



#### CSRF







_Appears in:_
- [Traffic](#traffic)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `additionalOrigins` _string array_ | additionalOrigin specifies additional source origins that will be allowed in addition to the destination origin. The<br />`Origin` consists of a scheme and a host, with an optional port, and takes the form `<scheme>://<host>(:<port>)`. |  | MaxItems: 16 <br />MinItems: 1 <br /> |


#### CustomResponse



CustomResponse configures a response to return to the client if request content
is matched against a regex pattern and the action is `REJECT`.



_Appears in:_
- [PromptguardRequest](#promptguardrequest)
- [PromptguardResponse](#promptguardresponse)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `message` _string_ | A custom response message to return to the client. If not specified, defaults to<br />"The request was rejected due to inappropriate content". | The request was rejected due to inappropriate content |  |
| `statusCode` _integer_ | The status code to return to the client. Defaults to 403. | 403 | Maximum: 599 <br />Minimum: 200 <br /> |


#### DirectResponse



DirectResponse defines the policy to send a direct response to the client.



_Appears in:_
- [Traffic](#traffic)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `status` _integer_ | StatusCode defines the HTTP status code to return for this route. |  | Maximum: 599 <br />Minimum: 200 <br /> |
| `body` _string_ | Body defines the content to be returned in the HTTP response body.<br />The maximum length of the body is restricted to prevent excessively large responses.<br />If this field is omitted, no body is included in the response. |  | MaxLength: 4096 <br />MinLength: 1 <br /> |


#### DynamicForwardProxyBackend







_Appears in:_
- [AgentgatewayBackendSpec](#agentgatewaybackendspec)



#### ExtAuth







_Appears in:_
- [Traffic](#traffic)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `backendRef` _[BackendObjectReference](https://gateway-api.sigs.k8s.io/reference/spec/#backendobjectreference)_ | backendRef references the External Authorization server to reach.<br /><br />Supported types: Service and Backend. |  |  |
| `forwardBody` _[ExtAuthBody](#extauthbody)_ | forwardBody configures whether to include the HTTP body in the request. If enabled, the request body will be<br />buffered. |  |  |
| `contextExtensions` _object (keys:string, values:string)_ | contextExtensions specifies additional arbitrary key-value pairs to send to the authorization server. |  | MaxProperties: 64 <br /> |


#### ExtAuthBody







_Appears in:_
- [ExtAuth](#extauth)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `maxSize` _integer_ | maxSize specifies how large in bytes the largest body that will be buffered and sent to the authorization server. If<br />the body size is larger than maxSize, then the request will be rejected with a response. |  | Minimum: 1 <br /> |


#### ExtProc







_Appears in:_
- [Traffic](#traffic)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `backendRef` _[BackendObjectReference](https://gateway-api.sigs.k8s.io/reference/spec/#backendobjectreference)_ | backendRef references the External Processor server to reach.<br />Supported types: Service and Backend. |  |  |


#### FieldDefault



FieldDefault provides default values for specific fields in the JSON request body sent to the LLM provider.
These defaults are merged with the user-provided request to ensure missing fields are populated.


User input fields here refer to the fields in the JSON request body that a client sends when making a request to the LLM provider.
Defaults set here do _not_ override those user-provided values unless you explicitly set `override` to `true`.


Example: Setting a default system field for Anthropic, which does not support system role messages:
```yaml
defaults:
  - field: "system"
    value: "answer all questions in French"


```


Example: Setting a default temperature and overriding `max_tokens`:
```yaml
defaults:
  - field: "temperature"
    value: "0.5"
  - field: "max_tokens"
    value: "100"
    override: true


```


Example: Setting custom lists fields:
```yaml
defaults:
  - field: "custom_integer_list"
    value: [1,2,3]


overrides:
  - field: "custom_string_list"
    value: ["one","two","three"]


```


Note: The `field` values correspond to keys in the JSON request body, not fields in this CRD.



_Appears in:_
- [BackendAI](#backendai)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `field` _string_ | The name of the field. |  | MinLength: 1 <br /> |
| `value` _[JSON](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#json-v1-apiextensions-k8s-io)_ | The field default value, which can be any JSON Data Type. |  |  |


#### Frontend







_Appears in:_
- [AgentgatewayPolicySpec](#agentgatewaypolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `tcp` _[FrontendTCP](#frontendtcp)_ | tcp defines settings on managing incoming TCP connections. |  |  |
| `tls` _[FrontendTLS](#frontendtls)_ | tls defines settings on managing incoming TLS connections. |  |  |
| `http` _[FrontendHTTP](#frontendhttp)_ | http defines settings on managing incoming HTTP requests. |  |  |
| `accessLog` _[AccessLog](#accesslog)_ | AccessLoggingConfig contains access logging configuration |  |  |
| `tracing` _[Tracing](#tracing)_ | Tracing contains various settings for OpenTelemetry tracer.<br />TODO: not currently implemented |  |  |


#### FrontendHTTP







_Appears in:_
- [Frontend](#frontend)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `maxBufferSize` _integer_ | maxBufferSize defines the maximum size HTTP body that will be buffered into memory.<br />Bodies will only be buffered for policies which require buffering.<br />If unset, this defaults to 2mb. |  | Minimum: 1 <br /> |
| `http1MaxHeaders` _integer_ | http1MaxHeaders defines the maximum number of headers that are allowed in HTTP/1.1 requests.<br />If unset, this defaults to 100. |  | Maximum: 4096 <br />Minimum: 1 <br /> |
| `http1IdleTimeout` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | http1IdleTimeout defines the timeout before an unused connection is closed.<br />If unset, this defaults to 10 minutes. |  |  |
| `http2WindowSize` _integer_ | http2WindowSize indicates the initial window size for stream-level flow control for received data. |  | Minimum: 1 <br /> |
| `http2ConnectionWindowSize` _integer_ | http2ConnectionWindowSize indicates the initial window size for connection-level flow control for received data. |  | Minimum: 1 <br /> |
| `http2FrameSize` _integer_ | http2FrameSize sets the maximum frame size to use.<br />If unset, this defaults to 16kb |  | Maximum: 1.677215e+06 <br />Minimum: 16384 <br /> |
| `http2KeepaliveInterval` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ |  |  |  |
| `http2KeepaliveTimeout` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ |  |  |  |


#### FrontendTCP







_Appears in:_
- [Frontend](#frontend)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `keepalive` _[Keepalive](#keepalive)_ | keepalive defines settings for enabling TCP keepalives on the connection. |  |  |


#### FrontendTLS







_Appears in:_
- [Frontend](#frontend)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `handshakeTimeout` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | handshakeTimeout specifies the deadline for a TLS handshake to complete.<br />If unset, this defaults to 15s. |  |  |
| `alpnProtocols` _string_ | alpnProtocols sets the Application Level Protocol Negotiation (ALPN) value to use in the TLS handshake.<br /><br />If not present, defaults to ["h2", "http/1.1"]. |  | MaxItems: 16 <br />MinItems: 1 <br /> |


#### GeminiConfig



GeminiConfig settings for the [Gemini](https://ai.google.dev/gemini-api/docs) LLM provider.



_Appears in:_
- [LLMProvider](#llmprovider)
- [NamedLLMProvider](#namedllmprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `model` _string_ | Optional: Override the model name, such as `gemini-2.5-pro`.<br />If unset, the model name is taken from the request. |  |  |


#### GlobalRateLimit







_Appears in:_
- [RateLimits](#ratelimits)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `backendRef` _[BackendObjectReference](https://gateway-api.sigs.k8s.io/reference/spec/#backendobjectreference)_ | backendRef references the Rate Limit server to reach.<br />Supported types: Service and Backend. |  |  |
| `domain` _string_ | domain specifies the domain under which this limit should apply.<br />This is an arbitrary string that enables a rate limit server to distinguish between different applications. |  |  |
| `descriptors` _[RateLimitDescriptor](#ratelimitdescriptor) array_ | Descriptors define the dimensions for rate limiting. These values are passed to the rate limit service which applies<br />configured limits based on them. Each descriptor represents a single rate limit rule with one or more entries. |  | MaxItems: 16 <br />MinItems: 1 <br /> |


#### HTTPVersion

_Underlying type:_ _string_





_Appears in:_
- [BackendHTTP](#backendhttp)

| Field | Description |
| --- | --- |
| `HTTP1` |  |
| `HTTP2` |  |


#### HeaderName

_Underlying type:_ _string_

An HTTP Header Name.

_Validation:_
- MaxLength: 256
- MinLength: 1
- Pattern: `^:?[A-Za-z0-9!#$%&'*+\-.^_\x60|~]+$`

_Appears in:_
- [HeaderTransformation](#headertransformation)
- [Transform](#transform)



#### HeaderTransformation







_Appears in:_
- [Transform](#transform)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _[HeaderName](#headername)_ | the name of the header to add. |  | MaxLength: 256 <br />MinLength: 1 <br />Pattern: `^:?[A-Za-z0-9!#$%&'*+\-.^_\x60\|~]+$` <br /> |
| `value` _[CELExpression](#celexpression)_ | value is the CEL expression to apply to generate the output value for the header. |  |  |


#### HostnameRewrite







_Appears in:_
- [Traffic](#traffic)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `mode` _[HostnameRewriteMode](#hostnamerewritemode)_ | mode sets the hostname rewrite mode.<br /><br />The following may be specified:<br />* Auto: automatically set the Host header based on the destination.<br />* None: do not rewrite the Host header. The original Host header will be passed through.<br /><br />This setting defaults to Auto when connecting to hostname-based Backend types, and None otherwise (for Service or<br />IP-based Backends). |  |  |


#### HostnameRewriteMode

_Underlying type:_ _string_





_Appears in:_
- [HostnameRewrite](#hostnamerewrite)

| Field | Description |
| --- | --- |
| `Auto` |  |
| `None` |  |


#### Image



A container image. See https://kubernetes.io/docs/concepts/containers/images
for details.



_Appears in:_
- [AgentgatewayParametersConfigs](#agentgatewayparametersconfigs)
- [AgentgatewayParametersSpec](#agentgatewayparametersspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `registry` _string_ | The image registry. |  |  |
| `repository` _string_ | The image repository (name). |  |  |
| `tag` _string_ | The image tag. |  |  |
| `digest` _string_ | The hash digest of the image, e.g. `sha256:12345...` |  |  |
| `pullPolicy` _[PullPolicy](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#pullpolicy-v1-core)_ | The image pull policy for the container. See<br />https://kubernetes.io/docs/concepts/containers/images/#image-pull-policy<br />for details. |  |  |


#### InsecureTLSMode

_Underlying type:_ _string_





_Appears in:_
- [BackendTLS](#backendtls)

| Field | Description |
| --- | --- |
| `All` | InsecureTLSModeInsecure disables all TLS verification<br /> |
| `Hostname` | InsecureTLSModeHostname enables verifying the CA certificate, but disables verification of the hostname/SAN.<br />Note this is still, generally, very "insecure" as the name suggests.<br /> |


#### JWKS







_Appears in:_
- [JWTProvider](#jwtprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `remote` _[RemoteJWKS](#remotejwks)_ | remote specifies how to reach the JSON Web Key Set from a remote address. |  |  |
| `inline` _string_ | inline specifies an inline JSON Web Key Set used validate the signature of the JWT. |  | MaxLength: 65536 <br />MinLength: 2 <br /> |


#### JWTAuthentication







_Appears in:_
- [Traffic](#traffic)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `mode` _[JWTAuthenticationMode](#jwtauthenticationmode)_ | validation mode for JWT authentication. | Strict | Enum: [Strict Optional Permissive] <br /> |
| `providers` _[JWTProvider](#jwtprovider) array_ |  |  | MaxItems: 64 <br />MinItems: 1 <br /> |


#### JWTAuthenticationMode

_Underlying type:_ _string_



_Validation:_
- Enum: [Strict Optional Permissive]

_Appears in:_
- [JWTAuthentication](#jwtauthentication)

| Field | Description |
| --- | --- |
| `Strict` | A valid token, issued by a configured issuer, must be present.<br />This is the default option.<br /> |
| `Optional` | If a token exists, validate it.<br />Warning: this allows requests without a JWT token!<br /> |
| `Permissive` | Requests are never rejected. This is useful for usage of claims in later steps (authorization, logging, etc).<br />Warning: this allows requests without a JWT token!<br /> |


#### JWTProvider







_Appears in:_
- [JWTAuthentication](#jwtauthentication)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `issuer` _string_ | issuer identifies the IdP that issued the JWT. This corresponds to the 'iss' claim (https://tools.ietf.org/html/rfc7519#section-4.1.1). |  |  |
| `audiences` _string array_ | audiences specifies the list of allowed audiences that are allowed access. This corresponds to the 'aud' claim (https://datatracker.ietf.org/doc/html/rfc7519#section-4.1.3).<br />If unset, any audience is allowed. |  | MaxItems: 64 <br />MinItems: 1 <br /> |
| `jwks` _[JWKS](#jwks)_ | jwks defines the JSON Web Key Set used to validate the signature of the JWT. |  |  |


#### Keepalive



TCP Keepalive settings



_Appears in:_
- [BackendTCP](#backendtcp)
- [FrontendTCP](#frontendtcp)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `retries` _integer_ | retries specifies the maximum number of keep-alive probes to send before dropping the connection.<br />If unset, this defaults to 9. |  | Maximum: 64 <br />Minimum: 1 <br /> |
| `time` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | time specifies the number of seconds a connection needs to be idle before keep-alive probes start being sent.<br />If unset, this defaults to 180s. |  |  |
| `interval` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | interval specifies the number of seconds between keep-alive probes.<br />If unset, this defaults to 180s. |  |  |


#### KubernetesResourceOverlay



KubernetesResourceOverlay provides a mechanism to customize generated
Kubernetes resources using [Strategic Merge
Patch](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-api-machinery/strategic-merge-patch.md)
semantics.



_Appears in:_
- [AgentgatewayParametersOverlays](#agentgatewayparametersoverlays)
- [AgentgatewayParametersSpec](#agentgatewayparametersspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `metadata` _[AgentgatewayParametersObjectMetadata](#agentgatewayparametersobjectmetadata)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[JSON](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#json-v1-apiextensions-k8s-io)_ | Spec provides an opaque mechanism to configure the resource Spec.<br />This field accepts a complete or partial Kubernetes resource spec (e.g., PodSpec, ServiceSpec)<br />and will be merged with the generated configuration using **Strategic Merge Patch** semantics.<br />The patch is applied after all other fields are applied.<br />If you merge-patch the same resource from AgentgatewayParameters on the<br />GatewayClass and also from AgentgatewayParameters on the Gateway, then<br />the GatewayClass merge-patch happens first.<br /><br /># Strategic Merge Patch & Deletion Guide<br /><br />This merge strategy allows you to override individual fields, merge lists, or delete items<br />without needing to provide the entire resource definition.<br /><br />**1. Replacing Values (Scalars):**<br />Simple fields (strings, integers, booleans) in your config will overwrite the generated defaults.<br /><br />**2. Merging Lists (Append/Merge):**<br />Lists with "merge keys" (like `containers` which merges on `name`, or `tolerations` which merges on `key`)<br />will append your items to the generated list, or update existing items if keys match.<br /><br />**3. Deleting List Items ($patch: delete):**<br />To remove an item from a generated list (e.g., removing a default sidecar), you must use<br />the special `$patch: delete` directive.<br /><br />  spec:<br />    containers:<br />      - name: agent-gateway<br />        # Delete the securityContext using $patch: delete<br />        securityContext:<br />          $patch: delete<br /><br />**4. Deleting/Clearing Map Fields (null):**<br />To remove a map field or a scalar entirely, set its value to `null`.<br /><br />  spec:<br />    template:<br />      spec:<br />        nodeSelector: null  # Removes default nodeSelector<br /><br />**5. Replacing Lists Entirely ($patch: replace):**<br />If you want to strictly define a list and ignore all generated defaults, use `$patch: replace`.<br /><br />  service:<br />    spec:<br />      ports:<br />        - $patch: replace<br />        - name: http<br />          port: 80<br />          targetPort: 8080<br />          protocol: TCP<br />        - name: https<br />          port: 443<br />          targetPort: 8443<br />          protocol: TCP |  | Type: object <br /> |


#### LLMProvider



LLMProvider specifies the target large language model provider that the backend should route requests to.



_Appears in:_
- [AIBackend](#aibackend)
- [NamedLLMProvider](#namedllmprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `openai` _[OpenAIConfig](#openaiconfig)_ | OpenAI provider |  |  |
| `azureopenai` _[AzureOpenAIConfig](#azureopenaiconfig)_ | Azure OpenAI provider |  |  |
| `anthropic` _[AnthropicConfig](#anthropicconfig)_ | Anthropic provider |  |  |
| `gemini` _[GeminiConfig](#geminiconfig)_ | Gemini provider |  |  |
| `vertexai` _[VertexAIConfig](#vertexaiconfig)_ | Vertex AI provider |  |  |
| `bedrock` _[BedrockConfig](#bedrockconfig)_ | Bedrock provider |  |  |
| `host` _string_ | Host specifies the hostname to send the requests to.<br />If not specified, the default hostname for the provider is used. |  |  |
| `port` _integer_ | Port specifies the port to send the requests to. |  | Maximum: 65535 <br />Minimum: 1 <br /> |
| `path` _string_ | Path specifies the URL path to use for the LLM provider API requests.<br />This is useful when you need to route requests to a different API endpoint while maintaining<br />compatibility with the original provider's API structure.<br />If not specified, the default path for the provider is used. |  |  |


#### LocalRateLimit



Policy for local rate limiting. Local rate limits are handled locally on a per-proxy basis, without co-ordination
between instances of the proxy.



_Appears in:_
- [RateLimits](#ratelimits)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `requests` _integer_ | requests specifies the number of HTTP requests per unit of time that are allowed. Requests exceeding this limit will fail with<br />a 429 error. |  | Minimum: 1 <br /> |
| `tokens` _integer_ | tokens specifies the number of LLM tokens per unit of time that are allowed. Requests exceeding this limit will fail<br />with a 429 error.<br /><br />Both input and output tokens are counted. However, token counts are not known until the request completes. As a<br />result, token-based rate limits will apply to future requests only. |  | Minimum: 1 <br /> |
| `unit` _[LocalRateLimitUnit](#localratelimitunit)_ | unit specifies the unit of time that requests are limited based on. |  | Enum: [Seconds Minutes Hours] <br /> |
| `burst` _integer_ | burst specifies an allowance of requests above the request-per-unit that should be allowed within a short period of time. |  |  |


#### LocalRateLimitUnit

_Underlying type:_ _string_





_Appears in:_
- [LocalRateLimit](#localratelimit)

| Field | Description |
| --- | --- |
| `Seconds` |  |
| `Minutes` |  |
| `Hours` |  |


#### LogTracingAttributes







_Appears in:_
- [AccessLog](#accesslog)
- [Tracing](#tracing)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `remove` _string array_ | remove lists the default fields that should be removed. For example, "http.method". |  | MaxItems: 32 <br />MinItems: 1 <br /> |
| `add` _[AttributeAdd](#attributeadd) array_ | add specifies additional key-value pairs to be added to each entry.<br />The value is a CEL expression. If the CEL expression fails to evaluate, the pair will be excluded. |  | MinItems: 1 <br /> |


#### MCPAuthentication







_Appears in:_
- [BackendMCP](#backendmcp)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `resourceMetadata` _object (keys:string, values:[JSON](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#json-v1-apiextensions-k8s-io))_ | ResourceMetadata defines the metadata to use for MCP resources. |  |  |
| `provider` _[McpIDP](#mcpidp)_ | McpIDP specifies the identity provider to use for authentication |  | Enum: [Auth0 Keycloak] <br /> |
| `issuer` _string_ | Issuer identifies the IdP that issued the JWT. This corresponds to the 'iss' claim (https://tools.ietf.org/html/rfc7519#section-4.1.1). |  |  |
| `audiences` _string array_ | audiences specify the list of allowed audiences that are allowed access. This corresponds to the 'aud' claim (https://datatracker.ietf.org/doc/html/rfc7519#section-4.1.3).<br />If unset, any audience is allowed. |  | MaxItems: 64 <br />MinItems: 1 <br /> |
| `jwks` _[RemoteJWKS](#remotejwks)_ | jwks defines the remote JSON Web Key used to validate the signature of the JWT. |  |  |


#### MCPBackend



MCPBackend configures mcp backends



_Appears in:_
- [AgentgatewayBackendSpec](#agentgatewaybackendspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `targets` _[McpTargetSelector](#mcptargetselector) array_ | Targets is a list of MCPBackend targets to use for this backend.<br />Policies targeting MCPBackend targets must use targetRefs[].sectionName<br />to select the target by name. |  | MaxItems: 32 <br />MinItems: 1 <br /> |


#### MCPProtocol

_Underlying type:_ _string_

MCPProtocol defines the protocol to use for the MCPBackend target

_Validation:_
- Enum: [StreamableHTTP SSE]

_Appears in:_
- [McpTarget](#mcptarget)

| Field | Description |
| --- | --- |
| `StreamableHTTP` | MCPProtocolStreamableHTTP specifies Streamable HTTP must be used as the protocol<br /> |
| `SSE` | MCPProtocolSSE specifies Server-Sent Events (SSE) must be used as the protocol<br /> |


#### McpIDP

_Underlying type:_ _string_





_Appears in:_
- [MCPAuthentication](#mcpauthentication)

| Field | Description |
| --- | --- |
| `Auth0` |  |
| `Keycloak` |  |


#### McpSelector







_Appears in:_
- [McpTargetSelector](#mcptargetselector)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `namespaces` _[LabelSelector](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#labelselector-v1-meta)_ | namespace is the label selector in which namespaces Services should be selected from.<br />If unset, only the namespace of the AgentgatewayBackend is searched. |  |  |
| `services` _[LabelSelector](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#labelselector-v1-meta)_ | services is the label selector for which Services should be selected. |  |  |


#### McpTarget



McpTarget defines a single MCPBackend target configuration.



_Appears in:_
- [McpTargetSelector](#mcptargetselector)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `host` _string_ | Host is the hostname or IP address of the MCPBackend target. |  |  |
| `port` _integer_ | Port is the port number of the MCPBackend target. |  | Maximum: 65535 <br />Minimum: 1 <br /> |
| `path` _string_ | Path is the URL path of the MCPBackend target endpoint.<br />Defaults to "/sse" for SSE protocol or "/mcp" for StreamableHTTP protocol if not specified. |  |  |
| `protocol` _[MCPProtocol](#mcpprotocol)_ | Protocol is the protocol to use for the connection to the MCPBackend target. |  | Enum: [StreamableHTTP SSE] <br /> |
| `policies` _[BackendWithMCP](#backendwithmcp)_ | policies controls policies for communicating with this backend. Policies may also be set in AgentgatewayPolicy, or<br />in the top level AgentgatewayBackend. Policies are merged on a field-level basis, with order: AgentgatewayPolicy <<br />AgentgatewayBackend < AgentgatewayBackend MCP (this field). |  |  |


#### McpTargetSelector



McpTargetSelector defines the MCPBackend target to use for this backend.



_Appears in:_
- [MCPBackend](#mcpbackend)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _[SectionName](#sectionname)_ | Name of the MCPBackend target. |  |  |
| `selector` _[McpSelector](#mcpselector)_ | selector is a label selector is the selector to use to select Services.<br />If policies are needed on a per-service basis, AgentgatewayPolicy can target the desired Service. |  |  |
| `static` _[McpTarget](#mcptarget)_ | static configures a static MCP destination. When connecting to in-cluster Services, it is recommended to use<br />'selector' instead. |  |  |


#### Message



An entry for a message to prepend or append to each prompt.



_Appears in:_
- [AIPromptEnrichment](#aipromptenrichment)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `role` _string_ | Role of the message. The available roles depend on the backend<br />LLM provider model, such as `SYSTEM` or `USER` in the OpenAI API. |  |  |
| `content` _string_ | String content of the message. |  |  |


#### NamedLLMProvider







_Appears in:_
- [PriorityGroup](#prioritygroup)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _[SectionName](#sectionname)_ | Name of the provider. Policies can target this provider by name. |  |  |
| `policies` _[BackendWithAI](#backendwithai)_ | policies controls policies for communicating with this backend. Policies may also be set in AgentgatewayPolicy, or<br />in the top level AgentgatewayBackend. policies are merged on a field-level basis, with order: AgentgatewayPolicy <<br />AgentgatewayBackend < AgentgatewayBackend LLM provider (this field). |  |  |
| `openai` _[OpenAIConfig](#openaiconfig)_ | OpenAI provider |  |  |
| `azureopenai` _[AzureOpenAIConfig](#azureopenaiconfig)_ | Azure OpenAI provider |  |  |
| `anthropic` _[AnthropicConfig](#anthropicconfig)_ | Anthropic provider |  |  |
| `gemini` _[GeminiConfig](#geminiconfig)_ | Gemini provider |  |  |
| `vertexai` _[VertexAIConfig](#vertexaiconfig)_ | Vertex AI provider |  |  |
| `bedrock` _[BedrockConfig](#bedrockconfig)_ | Bedrock provider |  |  |
| `host` _string_ | Host specifies the hostname to send the requests to.<br />If not specified, the default hostname for the provider is used. |  |  |
| `port` _integer_ | Port specifies the port to send the requests to. |  | Maximum: 65535 <br />Minimum: 1 <br /> |
| `path` _string_ | Path specifies the URL path to use for the LLM provider API requests.<br />This is useful when you need to route requests to a different API endpoint while maintaining<br />compatibility with the original provider's API structure.<br />If not specified, the default path for the provider is used. |  |  |


#### OpenAIConfig



OpenAIConfig settings for the [OpenAI](https://platform.openai.com/docs/api-reference/streaming) LLM provider.



_Appears in:_
- [LLMProvider](#llmprovider)
- [NamedLLMProvider](#namedllmprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `model` _string_ | Optional: Override the model name, such as `gpt-4o-mini`.<br />If unset, the model name is taken from the request. |  |  |


#### OpenAIModeration







_Appears in:_
- [PromptguardRequest](#promptguardrequest)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `model` _string_ | model specifies the moderation model to use. For example, `omni-moderation`. |  |  |
| `policies` _[BackendSimple](#backendsimple)_ | policies controls policies for communicating with OpenAI. |  |  |


#### PolicyPhase

_Underlying type:_ _string_



_Validation:_
- Enum: [PreRouting PostRouting]

_Appears in:_
- [Traffic](#traffic)

| Field | Description |
| --- | --- |
| `PreRouting` |  |
| `PostRouting` |  |


#### PriorityGroup







_Appears in:_
- [AIBackend](#aibackend)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `providers` _[NamedLLMProvider](#namedllmprovider) array_ | providers specifies a list of LLM providers within this group. Each provider is treated equally in terms of priority,<br />with automatic weighting based on health. |  | MaxItems: 32 <br />MinItems: 1 <br /> |


#### PromptCachingConfig



PromptCachingConfig configures automatic prompt caching for supported LLM providers.
Currently only AWS Bedrock supports this feature (Claude 3+ and Nova models).


When enabled, the gateway automatically inserts cache points at strategic locations
to reduce API costs. Bedrock charges lower rates for cached tokens (90% discount).


Example:


	promptCaching:
	  cacheSystem: true       # Cache system prompts
	  cacheMessages: true     # Cache conversation history
	  cacheTools: false       # Don't cache tool definitions
	  minTokens: 1024         # Only cache if ≥1024 tokens


Cost savings example:
- Without caching: 10,000 tokens × $3/MTok = $0.03
- With caching (90% cached): 1,000 × $3/MTok + 9,000 × $0.30/MTok = $0.0057 (81% savings)



_Appears in:_
- [BackendAI](#backendai)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `cacheSystem` _boolean_ | CacheSystem enables caching for system prompts.<br />Inserts a cache point after all system messages. | true |  |
| `cacheMessages` _boolean_ | CacheMessages enables caching for conversation messages.<br />Caches all messages in the conversation for cost savings. | true |  |
| `cacheTools` _boolean_ | CacheTools enables caching for tool definitions.<br />Inserts a cache point after all tool specifications. | false |  |
| `minTokens` _integer_ | MinTokens specifies the minimum estimated token count<br />before caching is enabled. Uses rough heuristic (word count × 1.3) to estimate tokens.<br />Bedrock requires at least 1,024 tokens for caching to be effective. | 1024 | Minimum: 0 <br /> |


#### PromptguardRequest



PromptguardRequest defines the prompt guards to apply to requests sent by the client.



_Appears in:_
- [AIPromptGuard](#aipromptguard)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `response` _[CustomResponse](#customresponse)_ | A custom response message to return to the client. If not specified, defaults to<br />"The request was rejected due to inappropriate content". |  |  |
| `regex` _[Regex](#regex)_ | Regular expression (regex) matching for prompt guards and data masking. |  |  |
| `webhook` _[Webhook](#webhook)_ | Configure a webhook to forward requests to for prompt guarding. |  |  |
| `openAIModeration` _[OpenAIModeration](#openaimoderation)_ | openAIModeration passes prompt data through the OpenAI Moderations endpoint.<br />See https://platform.openai.com/docs/api-reference/moderations for more information. |  |  |


#### PromptguardResponse



PromptguardResponse configures the response that the prompt guard applies to responses returned by the LLM provider.



_Appears in:_
- [AIPromptGuard](#aipromptguard)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `response` _[CustomResponse](#customresponse)_ | A custom response message to return to the client. If not specified, defaults to<br />"The response was rejected due to inappropriate content". |  |  |
| `regex` _[Regex](#regex)_ | Regular expression (regex) matching for prompt guards and data masking. |  |  |
| `webhook` _[Webhook](#webhook)_ | Configure a webhook to forward responses to for prompt guarding. |  |  |


#### RateLimitDescriptor







_Appears in:_
- [GlobalRateLimit](#globalratelimit)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `entries` _[RateLimitDescriptorEntry](#ratelimitdescriptorentry) array_ | entries are the individual components that make up this descriptor. |  | MaxItems: 16 <br />MinItems: 1 <br /> |
| `unit` _[RateLimitUnit](#ratelimitunit)_ | unit defines what to use as the cost function. If unspecified, Requests is used. |  | Enum: [Requests Tokens] <br /> |






#### RateLimitDescriptorEntry

A descriptor entry defines a single entry in a rate limit descriptor.


_Appears in:_
- [Various types](#various-types)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _[TinyString](#tinystring)_ | name specifies the name of the descriptor. |  | Required |
| `expression` _[CELExpression](#celexpression)_ | expression is a Common Expression Language (CEL) expression that defines the value for the descriptor.  For example, to rate limit based on the Client IP: `source.address`.  See https://agentgateway.dev/docs/reference/cel/ for more info. |  | Required |

#### RateLimits







_Appears in:_
- [Traffic](#traffic)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `local` _[LocalRateLimit](#localratelimit) array_ | Local defines a local rate limiting policy. |  | MaxItems: 16 <br />MinItems: 1 <br /> |
| `global` _[GlobalRateLimit](#globalratelimit)_ | Global defines a global rate limiting policy using an external service. |  |  |


#### Regex



Regex configures the regular expression (regex) matching for prompt guards and data masking.



_Appears in:_
- [PromptguardRequest](#promptguardrequest)
- [PromptguardResponse](#promptguardresponse)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `matches` _string array_ | A list of regex patterns to match against the request or response.<br />Matches and built-ins are additive. |  |  |
| `builtins` _[BuiltIn](#builtin) array_ | A list of built-in regex patterns to match against the request or response.<br />Matches and built-ins are additive. |  | Enum: [Ssn CreditCard PhoneNumber Email] <br /> |
| `action` _[Action](#action)_ | The action to take if a regex pattern is matched in a request or response.<br />This setting applies only to request matches. PromptguardResponse matches are always masked by default.<br />Defaults to `MASK`. | MASK |  |


#### RemoteJWKS


_Appears in:_
- [JWKS](#jwks)
- [MCPAuthentication](#mcpauthentication)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `uri` _[string](#string)_ | IdP jwks endpoint. Default tls settings are used to connect to this url. |  | Optional <br />Pattern |
| `cacheDuration` _[Duration](#duration)_ |  | 5m | Optional <br />Pattern <br />XValidation |
| `backendRef` _[BackendObjectReference](#backendobjectreference)_ | backendRef references the remote JWKS server to reach. Not implemented yet, only jwksUri is currently supported. Supported types: Service and Backend. | 5m | Optional <br />XValidation |
#### Retry



Retry defines the retry policy



_Appears in:_
- [Traffic](#traffic)



#### RouteType

_Underlying type:_ _string_

RouteType specifies how the AI gateway should process incoming requests
based on the URL path and the API format expected.

_Validation:_
- Enum: [Completions Messages Models Passthrough Responses AnthropicTokenCount]

_Appears in:_
- [BackendAI](#backendai)

| Field | Description |
| --- | --- |
| `Completions` | RouteTypeCompletions processes OpenAI /v1/chat/completions format requests<br /> |
| `Messages` | RouteTypeMessages processes Anthropic /v1/messages format requests<br /> |
| `Models` | RouteTypeModels handles /v1/models endpoint (returns available models)<br /> |
| `Passthrough` | RouteTypePassthrough sends requests to upstream as-is without LLM processing<br /> |
| `Responses` | RouteTypeResponses processes OpenAI /v1/responses format requests<br /> |
| `AnthropicTokenCount` | RouteTypeAnthropicTokenCount processes Anthropic /v1/messages/count_tokens format requests<br /> |


#### SecretSelector







_Appears in:_
- [APIKeyAuthentication](#apikeyauthentication)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `matchLabels` _object (keys:string, values:string)_ | Label selector to select the target resource. |  |  |


#### ShutdownSpec







_Appears in:_
- [AgentgatewayParametersConfigs](#agentgatewayparametersconfigs)
- [AgentgatewayParametersSpec](#agentgatewayparametersspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `min` _integer_ | Minimum time (in seconds) to wait before allowing Agentgateway to<br />terminate. Refer to the CONNECTION_MIN_TERMINATION_DEADLINE environment<br />variable for details. |  | Maximum: 3.1536e+07 <br />Minimum: 0 <br /> |
| `max` _integer_ | Maximum time (in seconds) to wait before allowing Agentgateway to<br />terminate. Refer to the TERMINATION_GRACE_PERIOD_SECONDS environment<br />variable for details. |  | Maximum: 3.1536e+07 <br />Minimum: 0 <br /> |


#### StaticBackend







_Appears in:_
- [AgentgatewayBackendSpec](#agentgatewaybackendspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `host` _string_ | host to connect to. |  |  |
| `port` _integer_ | port to connect to. |  | Maximum: 65535 <br />Minimum: 1 <br /> |


#### Timeouts







_Appears in:_
- [Traffic](#traffic)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `request` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | request specifies a timeout for an individual request from the gateway to a backend. This covers the time from when<br />the request first starts being sent from the gateway to when the full response has been received from the backend. |  |  |


#### Tracing







_Appears in:_
- [Frontend](#frontend)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `backendRef` _[BackendObjectReference](https://gateway-api.sigs.k8s.io/reference/spec/#backendobjectreference)_ | backendRef references the OTLP server to reach.<br />Supported types: Service and Backend. |  |  |
| `protocol` _[TracingProtocol](#tracingprotocol)_ | protocol specifies the OTLP protocol variant to use. | HTTP | Enum: [HTTP GRPC] <br /> |
| `attributes` _[LogTracingAttributes](#logtracingattributes)_ | attributes specifies customizations to the key-value pairs that are included in the trace |  |  |
| `randomSampling` _[CELExpression](#celexpression)_ | randomSampling is an expression to determine the amount of random sampling. Random sampling will initiate a new<br />trace span if the incoming request does not have a trace initiated already. This should evaluate to a float between<br />0.0-1.0, or a boolean (true/false) If unspecified, random sampling is disabled. |  |  |
| `clientSampling` _[CELExpression](#celexpression)_ | clientSampling is an expression to determine the amount of client sampling. Client sampling determines whether to<br />initiate a new trace span if the incoming request does have a trace already. This should evaluate to a float between<br />0.0-1.0, or a boolean (true/false) If unspecified, client sampling is 100% enabled. |  |  |


#### TracingProtocol

_Underlying type:_ _string_





_Appears in:_
- [Tracing](#tracing)

| Field | Description |
| --- | --- |
| `HTTP` |  |
| `GRPC` |  |


#### Traffic







_Appears in:_
- [AgentgatewayPolicySpec](#agentgatewaypolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `phase` _[PolicyPhase](#policyphase)_ | The phase to apply the traffic policy to. If the phase is PreRouting, the targetRef must be a Gateway or a Listener.<br />PreRouting is typically used only when a policy needs to influence the routing decision.<br /><br />Even when using PostRouting mode, the policy can target the Gateway/Listener. This is a helper for applying the policy<br />to all routes under that Gateway/Listener, and follows the merging logic described above.<br /><br />Note: PreRouting and PostRouting rules do not merge together. These are independent execution phases. That is, all<br />PreRouting rules will merge and execute, then all PostRouting rules will merge and execute.<br /><br />If unset, this defaults to PostRouting. |  | Enum: [PreRouting PostRouting] <br /> |
| `transformation` _[Transformation](#transformation)_ | transformation is used to mutate and transform requests and responses<br />before forwarding them to the destination. |  |  |
| `extProc` _[ExtProc](#extproc)_ | extProc specifies the external processing configuration for the policy. |  |  |
| `extAuth` _[ExtAuth](#extauth)_ | extAuth specifies the external authentication configuration for the policy.<br />This controls what external server to send requests to for authentication. |  |  |
| `rateLimit` _[RateLimits](#ratelimits)_ | rateLimit specifies the rate limiting configuration for the policy.<br />This controls the rate at which requests are allowed to be processed. |  |  |
| `cors` _[CORS](#cors)_ | cors specifies the CORS configuration for the policy. |  |  |
| `csrf` _[CSRF](#csrf)_ | csrf specifies the Cross-Site Request Forgery (CSRF) policy for this traffic policy.<br /><br />The CSRF policy has the following behavior:<br />* Safe methods (GET, HEAD, OPTIONS) are automatically allowed<br />* Requests without Sec-Fetch-Site or Origin headers are assumed to be same-origin or non-browser requests and are allowed.<br />* Otherwise, the Sec-Fetch-Site header is checked, with a fallback to comparing the Origin header to the Host header. |  |  |
| `headerModifiers` _[HeaderModifiers](#headermodifiers)_ | headerModifiers defines the policy to modify request and response headers. |  |  |
| `hostRewrite` _[HostnameRewrite](#hostnamerewrite)_ | hostRewrite specifies how to rewrite the Host header for requests.<br /><br />If the HTTPRoute `urlRewrite` filter already specifies a host rewrite, this setting is ignored. |  | Enum: [Auto None] <br /> |
| `timeouts` _[Timeouts](#timeouts)_ | timeouts defines the timeouts for requests<br />It is applicable to HTTPRoutes and ignored for other targeted kinds. |  |  |
| `retry` _[Retry](#retry)_ | retry defines the policy for retrying requests. |  |  |
| `authorization` _[Authorization](#authorization)_ | authorization specifies the access rules based on roles and permissions.<br />If multiple authorization rules are applied across different policies (at the same, or different, attahcment points),<br />all rules are merged. |  |  |
| `jwtAuthentication` _[JWTAuthentication](#jwtauthentication)_ | jwtAuthentication authenticates users based on JWT tokens. |  |  |
| `basicAuthentication` _[BasicAuthentication](#basicauthentication)_ | basicAuthentication authenticates users based on the "Basic" authentication scheme (RFC 7617), where a username and password<br />are encoded in the request. |  |  |
| `apiKeyAuthentication` _[APIKeyAuthentication](#apikeyauthentication)_ | apiKeyAuthentication authenticates users based on a configured API Key. |  |  |
| `directResponse` _[DirectResponse](#directresponse)_ | direct response configures the policy to send a direct response to the client. |  |  |


#### Transform







_Appears in:_
- [Transformation](#transformation)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `set` _[HeaderTransformation](#headertransformation) array_ | set is a list of headers and the value they should be set to. |  | MaxItems: 16 <br />MinItems: 1 <br /> |
| `add` _[HeaderTransformation](#headertransformation) array_ | add is a list of headers to add to the request and what that value should be set to. If there is already a header<br />with these values then append the value as an extra entry. |  | MaxItems: 16 <br />MinItems: 1 <br /> |
| `remove` _[HeaderName](#headername) array_ | Remove is a list of header names to remove from the request/response. |  | MaxItems: 16 <br />MaxLength: 256 <br />MinItems: 1 <br />MinLength: 1 <br />Pattern: `^:?[A-Za-z0-9!#$%&'*+\-.^_\x60\|~]+$` <br /> |
| `body` _[CELExpression](#celexpression)_ | body controls manipulation of the HTTP body. |  |  |


#### Transformation







_Appears in:_
- [Traffic](#traffic)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `request` _[Transform](#transform)_ | request is used to modify the request path. |  |  |
| `response` _[Transform](#transform)_ | response is used to modify the response path. |  |  |


#### VertexAIConfig



VertexAIConfig settings for the [Vertex AI](https://cloud.google.com/vertex-ai/docs) LLM provider.



_Appears in:_
- [LLMProvider](#llmprovider)
- [NamedLLMProvider](#namedllmprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `model` _string_ | Optional: Override the model name, such as `gpt-4o-mini`.<br />If unset, the model name is taken from the request. |  |  |
| `projectId` _string_ | The ID of the Google Cloud Project that you use for the Vertex AI. |  | MinLength: 1 <br /> |
| `region` _string_ | The location of the Google Cloud Project that you use for the Vertex AI. |  | MinLength: 1 <br /> |


#### Webhook



Webhook configures a webhook to forward requests or responses to for prompt guarding.



_Appears in:_
- [PromptguardRequest](#promptguardrequest)
- [PromptguardResponse](#promptguardresponse)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `backendRef` _[BackendObjectReference](https://gateway-api.sigs.k8s.io/reference/spec/#backendobjectreference)_ | backendRef references the webhook server to reach.<br /><br />Supported types: Service and Backend. |  |  |
| `forwardHeaderMatches` _HTTPHeaderMatch array_ | ForwardHeaderMatches defines a list of HTTP header matches that will be<br />used to select the headers to forward to the webhook.<br />Request headers are used when forwarding requests and response headers<br />are used when forwarding responses.<br />By default, no headers are forwarded. |  |  |


