---
title: API reference
weight: 10
---


## Packages
- [gateway.kgateway.dev/v1alpha1](#gatewaykgatewaydevv1alpha1)


## gateway.kgateway.dev/v1alpha1


### Resource Types
- [Backend](#backend)
- [BackendConfigPolicy](#backendconfigpolicy)
- [DirectResponse](#directresponse)
- [GatewayExtension](#gatewayextension)
- [GatewayParameters](#gatewayparameters)
- [HTTPListenerPolicy](#httplistenerpolicy)
- [TrafficPolicy](#trafficpolicy)



#### AIBackend





_Validation:_
- MaxProperties: 1
- MinProperties: 1

_Appears in:_
- [BackendSpec](#backendspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `llm` _[LLMProvider](#llmprovider)_ | The LLM configures the AI gateway to use a single LLM provider backend. |  |  |
| `multipool` _[MultiPoolConfig](#multipoolconfig)_ | The MultiPool configures the backends for multiple hosts or models from the same provider in one Backend resource. |  |  |


#### AIPolicy



AIPolicy config is used to configure the behavior of the LLM provider
on the level of individual routes. These route settings, such as prompt enrichment,
retrieval augmented generation (RAG), and semantic caching, are applicable only
for routes that send requests to an LLM provider backend.



_Appears in:_
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `promptEnrichment` _[AIPromptEnrichment](#aipromptenrichment)_ | Enrich requests sent to the LLM provider by appending and prepending system prompts.<br />This can be configured only for LLM providers that use the `CHAT` or `CHAT_STREAMING` API route type. |  |  |
| `promptGuard` _[AIPromptGuard](#aipromptguard)_ | Set up prompt guards to block unwanted requests to the LLM provider and mask sensitive data.<br />Prompt guards can be used to reject requests based on the content of the prompt, as well as<br />mask responses based on the content of the response. |  |  |
| `defaults` _[FieldDefault](#fielddefault) array_ | Provide defaults to merge with user input fields.<br />Defaults do _not_ override the user input fields, unless you explicitly set `override` to `true`. |  |  |
| `routeType` _[RouteType](#routetype)_ | The type of route to the LLM provider API. Currently, `CHAT` and `CHAT_STREAMING` are supported.<br />Note: This field is not applicable when using agentgateway | CHAT | Enum: [CHAT CHAT_STREAMING] <br /> |


#### AIPromptEnrichment



AIPromptEnrichment defines the config to enrich requests sent to the LLM provider by appending and prepending system prompts.
This can be configured only for LLM providers that use the `CHAT` or `CHAT_STREAMING` API type.


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
- [AIPolicy](#aipolicy)

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
    customResponse:
      message: "Rejected due to inappropriate content"
    regex:
      action: REJECT
      matches:
      - pattern: "credit card"
        name: "CC"
  response:
    regex:
      builtins:
      - CREDIT_CARD
      action: MASK
```



_Appears in:_
- [AIPolicy](#aipolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `request` _[PromptguardRequest](#promptguardrequest)_ | Prompt guards to apply to requests sent by the client. |  |  |
| `response` _[PromptguardResponse](#promptguardresponse)_ | Prompt guards to apply to responses returned by the LLM provider. |  |  |


#### AWSGuardrailConfig







_Appears in:_
- [BedrockConfig](#bedrockconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `identifier` _string_ | GuardrailIdentifier is the identifier of the Guardrail policy to use for the backend. |  | MinLength: 1 <br /> |
| `version` _string_ | GuardrailVersion is the version of the Guardrail policy to use for the backend. |  | MinLength: 1 <br /> |


#### AWSLambdaPayloadTransformMode

_Underlying type:_ _string_

AWSLambdaPayloadTransformMode defines the transformation mode for the payload in the request
before it is sent to the AWS Lambda function.

_Validation:_
- Enum: [None Envoy]

_Appears in:_
- [AwsLambda](#awslambda)

| Field | Description |
| --- | --- |
| `None` | AWSLambdaPayloadTransformNone indicates that the payload will not be transformed using Envoy's<br />built-in transformation before it is sent to the Lambda function.<br />Note: Transformation policies configured on the route will still apply.<br /> |
| `Envoy` | AWSLambdaPayloadTransformEnvoy indicates that the payload will be transformed using Envoy's<br />built-in transformation. Refer to<br />https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/aws_lambda_filter#configuration-as-a-listener-filter<br />for more details on how Envoy transforms the payload.<br /> |


#### AccessLog



AccessLog represents the top-level access log configuration.



_Appears in:_
- [HTTPListenerPolicySpec](#httplistenerpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `fileSink` _[FileSink](#filesink)_ | Output access logs to local file |  |  |
| `grpcService` _[AccessLogGrpcService](#accessloggrpcservice)_ | Send access logs to gRPC service |  |  |
| `openTelemetry` _[OpenTelemetryAccessLogService](#opentelemetryaccesslogservice)_ | Send access logs to an OTel collector |  |  |
| `filter` _[AccessLogFilter](#accesslogfilter)_ | Filter access logs configuration |  | MaxProperties: 1 <br />MinProperties: 1 <br /> |


#### AccessLogFilter



AccessLogFilter represents the top-level filter structure.
Based on: https://www.envoyproxy.io/docs/envoy/v1.33.0/api-v3/config/accesslog/v3/accesslog.proto#config-accesslog-v3-accesslogfilter

_Validation:_
- MaxProperties: 1
- MinProperties: 1

_Appears in:_
- [AccessLog](#accesslog)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `andFilter` _[FilterType](#filtertype) array_ | Performs a logical "and" operation on the result of each individual filter.<br />Based on: https://www.envoyproxy.io/docs/envoy/v1.33.0/api-v3/config/accesslog/v3/accesslog.proto#config-accesslog-v3-andfilter |  | MaxProperties: 1 <br />MinItems: 2 <br />MinProperties: 1 <br /> |
| `orFilter` _[FilterType](#filtertype) array_ | Performs a logical "or" operation on the result of each individual filter.<br />Based on: https://www.envoyproxy.io/docs/envoy/v1.33.0/api-v3/config/accesslog/v3/accesslog.proto#config-accesslog-v3-orfilter |  | MaxProperties: 1 <br />MinItems: 2 <br />MinProperties: 1 <br /> |


#### AccessLogGrpcService



AccessLogGrpcService represents the gRPC service configuration for access logs.
Ref: https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/access_loggers/grpc/v3/als.proto#envoy-v3-api-msg-extensions-access-loggers-grpc-v3-httpgrpcaccesslogconfig



_Appears in:_
- [AccessLog](#accesslog)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `backendRef` _[BackendRef](#backendref)_ | The backend gRPC service. Can be any type of supported backend (Kubernetes Service, kgateway Backend, etc..) |  |  |
| `authority` _string_ | The :authority header in the grpc request. If this field is not set, the authority header value will be cluster_name.<br />Note that this authority does not override the SNI. The SNI is provided by the transport socket of the cluster. |  |  |
| `maxReceiveMessageLength` _integer_ | Maximum gRPC message size that is allowed to be received. If a message over this limit is received, the gRPC stream is terminated with the RESOURCE_EXHAUSTED error.<br />Defaults to 0, which means unlimited. |  |  |
| `skipEnvoyHeaders` _boolean_ | This provides gRPC client level control over envoy generated headers. If false, the header will be sent but it can be overridden by per stream option. If true, the header will be removed and can not be overridden by per stream option. Default to false. |  |  |
| `timeout` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | The timeout for the gRPC request. This is the timeout for a specific request |  |  |
| `initialMetadata` _[HeaderValue](#headervalue) array_ | Additional metadata to include in streams initiated to the GrpcService.<br />This can be used for scenarios in which additional ad hoc authorization headers (e.g. x-foo-bar: baz-key) are to be injected |  |  |
| `retryPolicy` _[RetryPolicy](#retrypolicy)_ | Indicates the retry policy for re-establishing the gRPC stream.<br />If max interval is not provided, it will be set to ten times the provided base interval |  |  |
| `logName` _string_ | name of log stream |  |  |
| `additionalRequestHeadersToLog` _string array_ | Additional request headers to log in the access log |  |  |
| `additionalResponseHeadersToLog` _string array_ | Additional response headers to log in the access log |  |  |
| `additionalResponseTrailersToLog` _string array_ | Additional response trailers to log in the access log |  |  |


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


#### AgentGateway



AgentGateway configures the AgentGateway integration. If AgentGateway is enabled, Envoy



_Appears in:_
- [KubernetesProxyConfig](#kubernetesproxyconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `enabled` _boolean_ | Whether to enable the extension. |  |  |
| `logLevel` _string_ | Log level for the agentgateway. Defaults to info.<br />Levels include "trace", "debug", "info", "error", "warn". See: https://docs.rs/tracing/latest/tracing/struct.Level.html |  |  |
| `image` _[Image](#image)_ | The agentgateway container image. See<br />https://kubernetes.io/docs/concepts/containers/images<br />for details.<br /><br />Default values, which may be overridden individually:<br /><br />	registry: ghcr.io/agentgateway<br />	repository: agentgateway<br />	tag: <agentgateway version><br />	pullPolicy: IfNotPresent |  |  |
| `securityContext` _[SecurityContext](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#securitycontext-v1-core)_ | The security context for this container. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#securitycontext-v1-core<br />for details. |  |  |
| `resources` _[ResourceRequirements](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#resourcerequirements-v1-core)_ | The compute resources required by this container. See<br />https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/<br />for details. |  |  |
| `env` _[EnvVar](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#envvar-v1-core) array_ | The container environment variables. |  |  |
| `customConfigMapName` _string_ | Name of the custom configmap to use instead of the default generated one.<br />When set, the agent gateway will use this configmap instead of creating the default one.<br />The configmap must contain a 'config.yaml' key with the agent gateway configuration. |  |  |


#### AiExtension



Configuration for the AI extension.



_Appears in:_
- [KubernetesProxyConfig](#kubernetesproxyconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `enabled` _boolean_ | Whether to enable the extension. |  |  |
| `image` _[Image](#image)_ | The extension's container image. See<br />https://kubernetes.io/docs/concepts/containers/images<br />for details. |  |  |
| `securityContext` _[SecurityContext](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#securitycontext-v1-core)_ | The security context for this container. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#securitycontext-v1-core<br />for details. |  |  |
| `resources` _[ResourceRequirements](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#resourcerequirements-v1-core)_ | The compute resources required by this container. See<br />https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/<br />for details. |  |  |
| `env` _[EnvVar](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#envvar-v1-core) array_ | The extension's container environment variables. |  |  |
| `ports` _[ContainerPort](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#containerport-v1-core) array_ | The extension's container ports. |  |  |
| `stats` _[AiExtensionStats](#aiextensionstats)_ | Additional stats config for AI Extension.<br />This config can be useful for adding custom labels to the request metrics.<br /><br />Example:<br />stats:<br />&nbsp;&nbsp;customLabels:<br />&nbsp;&nbsp;&nbsp;&nbsp;- name: "subject"<br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;metadataNamespace: "envoy.filters.http.jwt_authn"<br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;metadataKey: "principal:sub"<br />&nbsp;&nbsp;&nbsp;&nbsp;- name: "issuer"<br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;metadataNamespace: "envoy.filters.http.jwt_authn"<br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;metadataKey: "principal:iss"<br /> |  |  |
| `tracing` _[AiExtensionTrace](#aiextensiontrace)_ | Additional OTel tracing config for AI Extension. |  |  |


#### AiExtensionStats







_Appears in:_
- [AiExtension](#aiextension)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `customLabels` _[CustomLabel](#customlabel) array_ | Set of custom labels to be added to the request metrics.<br />These will be added on each request which goes through the AI Extension. |  |  |


#### AiExtensionTrace



AiExtensionTrace defines the tracing configuration for the AI extension



_Appears in:_
- [AiExtension](#aiextension)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `endpoint` _[AbsoluteURI](#absoluteuri)_ | EndPoint specifies the URL of the OTLP Exporter for traces.<br />Example: "http://my-otel-collector.svc.cluster.local:4317"<br />https://opentelemetry.io/docs/languages/sdk-configuration/otlp-exporter/#otel_exporter_otlp_traces_endpoint |  |  |
| `sampler` _[OTelTracesSampler](#oteltracessampler)_ | Sampler defines the sampling strategy for OpenTelemetry traces.<br />Sampling helps in reducing the volume of trace data by selectively<br />recording only a subset of traces.<br />https://opentelemetry.io/docs/languages/sdk-configuration/general/#otel_traces_sampler |  |  |
| `timeout` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | OTLPTimeout specifies timeout configurations for OTLP (OpenTelemetry Protocol) exports.<br />It allows setting general and trace-specific timeouts for sending data.<br />https://opentelemetry.io/docs/languages/sdk-configuration/otlp-exporter/#otel_exporter_otlp_traces_timeout |  |  |
| `protocol` _[OTLPTracesProtocolType](#otlptracesprotocoltype)_ | OTLPProtocol specifies the protocol to be used for OTLP exports.<br />This determines how tracing data is serialized and transported (e.g., gRPC, HTTP/Protobuf).<br />https://opentelemetry.io/docs/languages/sdk-configuration/otlp-exporter/#otel_exporter_otlp_traces_protocol |  | Enum: [grpc http/protobuf http/json] <br /> |


#### AlwaysOnConfig

_Underlying type:_ _[struct{}](#struct{})_

AlwaysOnConfig specified the AlwaysOn samplerc



_Appears in:_
- [Sampler](#sampler)



#### AnthropicConfig



AnthropicConfig settings for the [Anthropic](https://docs.anthropic.com/en/release-notes/api) LLM provider.



_Appears in:_
- [SupportedLLMProvider](#supportedllmprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `authToken` _[SingleAuthToken](#singleauthtoken)_ | The authorization token that the AI gateway uses to access the Anthropic API.<br />This token is automatically sent in the `x-api-key` header of the request. |  |  |
| `apiVersion` _string_ | Optional: A version header to pass to the Anthropic API.<br />For more information, see the [Anthropic API versioning docs](https://docs.anthropic.com/en/api/versioning). |  |  |
| `model` _string_ | Optional: Override the model name.<br />If unset, the model name is taken from the request.<br />This setting can be useful when testing model failover scenarios. |  |  |


#### AnyValue



AnyValue is used to represent any type of attribute value. AnyValue may contain a primitive value such as a string or integer or it may contain an arbitrary nested object containing arrays, key-value lists and primitives.
This is limited to string and nested values as OTel only supports them

_Validation:_
- MaxProperties: 1
- MinProperties: 1

_Appears in:_
- [AnyValue](#anyvalue)
- [KeyAnyValue](#keyanyvalue)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `stringValue` _string_ |  |  |  |
| `arrayValue` _[AnyValue](#anyvalue) array_ | TODO: Add support for ArrayValue && KvListValue |  | MaxProperties: 1 <br />MinProperties: 1 <br /> |


#### AppProtocol

_Underlying type:_ _string_

AppProtocol defines the application protocol to use when communicating with the backend.

_Validation:_
- Enum: [http2 grpc grpc-web kubernetes.io/h2c kubernetes.io/ws]

_Appears in:_
- [StaticBackend](#staticbackend)

| Field | Description |
| --- | --- |
| `http2` | AppProtocolHttp2 is the http2 app protocol.<br /> |
| `grpc` | AppProtocolGrpc is the grpc app protocol.<br /> |
| `grpc-web` | AppProtocolGrpcWeb is the grpc-web app protocol.<br /> |
| `kubernetes.io/h2c` | AppProtocolKubernetesH2C is the kubernetes.io/h2c app protocol.<br /> |
| `kubernetes.io/ws` | AppProtocolKubernetesWs is the kubernetes.io/ws app protocol.<br /> |


#### AuthHeaderOverride



AuthHeaderOverride allows customization of the default Authorization header sent to the LLM Provider.
The default header is `Authorization: Bearer <token>`. HeaderName can change the Authorization
header name and Prefix can change the Bearer prefix



_Appears in:_
- [LLMProvider](#llmprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `prefix` _string_ |  |  |  |
| `headerName` _string_ |  |  |  |


#### AuthorizationPolicyAction

_Underlying type:_ _string_

AuthorizationPolicyAction defines the action to take when the RBACPolicies matches.



_Appears in:_
- [RBAC](#rbac)

| Field | Description |
| --- | --- |
| `Allow` | AuthorizationPolicyActionAllow defines the action to take when the RBACPolicies matches.<br /> |
| `Deny` | AuthorizationPolicyActionDeny denies the action to take when the RBACPolicies matches.<br /> |


#### AwsAuth



AwsAuth specifies the authentication method to use for the backend.



_Appears in:_
- [AwsBackend](#awsbackend)
- [BedrockConfig](#bedrockconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `type` _[AwsAuthType](#awsauthtype)_ | Type specifies the authentication method to use for the backend. |  | Enum: [Secret] <br /> |
| `secretRef` _[LocalObjectReference](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#localobjectreference-v1-core)_ | SecretRef references a Kubernetes Secret containing the AWS credentials.<br />The Secret must have keys "accessKey", "secretKey", and optionally "sessionToken". |  |  |


#### AwsAuthType

_Underlying type:_ _string_

AwsAuthType specifies the authentication method to use for the backend.



_Appears in:_
- [AwsAuth](#awsauth)

| Field | Description |
| --- | --- |
| `Secret` | AwsAuthTypeSecret uses credentials stored in a Kubernetes Secret.<br /> |


#### AwsBackend



AwsBackend is the AWS backend configuration.



_Appears in:_
- [BackendSpec](#backendspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `lambda` _[AwsLambda](#awslambda)_ | Lambda configures the AWS lambda service. |  |  |
| `accountId` _string_ | AccountId is the AWS account ID to use for the backend. |  | MaxLength: 12 <br />MinLength: 1 <br />Pattern: `^[0-9]\{12\}$` <br /> |
| `auth` _[AwsAuth](#awsauth)_ | Auth specifies an explicit AWS authentication method for the backend.<br />When omitted, the following credential providers are tried in order, stopping when one<br />of them returns an access key ID and a secret access key (the session token is optional):<br />1. Environment variables: when the environment variables AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_SESSION_TOKEN are set.<br />2. AssumeRoleWithWebIdentity API call: when the environment variables AWS_WEB_IDENTITY_TOKEN_FILE and AWS_ROLE_ARN are set.<br />3. EKS Pod Identity: when the environment variable AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE is set.<br /><br />See the Envoy docs for more info:<br />https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/aws_request_signing_filter#credentials |  |  |
| `region` _string_ | Region is the AWS region to use for the backend.<br />Defaults to us-east-1 if not specified. | us-east-1 | MaxLength: 63 <br />MinLength: 1 <br />Pattern: `^[a-z0-9-]+$` <br /> |


#### AwsLambda



AwsLambda configures the AWS lambda service.



_Appears in:_
- [AwsBackend](#awsbackend)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `endpointURL` _string_ | EndpointURL is the URL or domain for the Lambda service. This is primarily<br />useful for testing and development purposes. When omitted, the default<br />lambda hostname will be used. |  | MaxLength: 2048 <br />Pattern: `^https?://[-a-zA-Z0-9@:%.+~#?&/=]+$` <br /> |
| `functionName` _string_ | FunctionName is the name of the Lambda function to invoke. |  | Pattern: `^[A-Za-z0-9-_]\{1,140\}$` <br /> |
| `invocationMode` _string_ | InvocationMode defines how to invoke the Lambda function.<br />Defaults to Sync. | Sync | Enum: [Sync Async] <br /> |
| `qualifier` _string_ | Qualifier is the alias or version for the Lambda function.<br />Valid values include a numeric version (e.g. "1"), an alias name<br />(alphanumeric plus "-" or "_"), or the special literal "$LATEST". | $LATEST | Pattern: `^(\$LATEST\|[0-9]+\|[A-Za-z0-9-_]\{1,128\})$` <br /> |
| `payloadTransformMode` _[AWSLambdaPayloadTransformMode](#awslambdapayloadtransformmode)_ | PayloadTransformation specifies payload transformation mode before it is sent to the Lambda function.<br />Defaults to Envoy. | Envoy | Enum: [None Envoy] <br /> |


#### AzureOpenAIConfig



AzureOpenAIConfig settings for the [Azure OpenAI](https://learn.microsoft.com/en-us/azure/ai-services/openai/) LLM provider.



_Appears in:_
- [SupportedLLMProvider](#supportedllmprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `authToken` _[SingleAuthToken](#singleauthtoken)_ | The authorization token that the AI gateway uses to access the Azure OpenAI API.<br />This token is automatically sent in the `api-key` header of the request. |  |  |
| `endpoint` _string_ | The endpoint for the Azure OpenAI API to use, such as `my-endpoint.openai.azure.com`.<br />If the scheme is included, it is stripped. |  | MinLength: 1 <br /> |
| `deploymentName` _string_ | The name of the Azure OpenAI model deployment to use.<br />For more information, see the [Azure OpenAI model docs](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models). |  | MinLength: 1 <br /> |
| `apiVersion` _string_ | The version of the Azure OpenAI API to use.<br />For more information, see the [Azure OpenAI API version reference](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#api-specs). |  | MinLength: 1 <br /> |


#### Backend









| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `gateway.kgateway.dev/v1alpha1` | | |
| `kind` _string_ | `Backend` | | |
| `kind` _string_ | Kind is a string value representing the REST resource this object represents.<br />Servers may infer this from the endpoint the client submits requests to.<br />Cannot be updated.<br />In CamelCase.<br />More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds |  |  |
| `apiVersion` _string_ | APIVersion defines the versioned schema of this representation of an object.<br />Servers should convert recognized schemas to the latest internal value, and<br />may reject unrecognized values.<br />More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources |  |  |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[BackendSpec](#backendspec)_ |  |  |  |
| `status` _[BackendStatus](#backendstatus)_ |  |  |  |


#### BackendConfigPolicy









| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `gateway.kgateway.dev/v1alpha1` | | |
| `kind` _string_ | `BackendConfigPolicy` | | |
| `kind` _string_ | Kind is a string value representing the REST resource this object represents.<br />Servers may infer this from the endpoint the client submits requests to.<br />Cannot be updated.<br />In CamelCase.<br />More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds |  |  |
| `apiVersion` _string_ | APIVersion defines the versioned schema of this representation of an object.<br />Servers should convert recognized schemas to the latest internal value, and<br />may reject unrecognized values.<br />More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources |  |  |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[BackendConfigPolicySpec](#backendconfigpolicyspec)_ |  |  |  |
| `status` _[PolicyStatus](#policystatus)_ |  |  |  |


#### BackendConfigPolicySpec



BackendConfigPolicySpec defines the desired state of BackendConfigPolicy.



_Appears in:_
- [BackendConfigPolicy](#backendconfigpolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `targetRefs` _[LocalPolicyTargetReference](#localpolicytargetreference) array_ | TargetRefs specifies the target references to attach the policy to. |  | MaxItems: 16 <br />MinItems: 1 <br /> |
| `targetSelectors` _[LocalPolicyTargetSelector](#localpolicytargetselector) array_ | TargetSelectors specifies the target selectors to select resources to attach the policy to. |  |  |
| `connectTimeout` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | The timeout for new network connections to hosts in the cluster. |  |  |
| `perConnectionBufferLimitBytes` _integer_ | Soft limit on size of the cluster's connections read and write buffers.<br />If unspecified, an implementation defined default is applied (1MiB). |  |  |
| `tcpKeepalive` _[TCPKeepalive](#tcpkeepalive)_ | Configure OS-level TCP keepalive checks. |  |  |
| `commonHttpProtocolOptions` _[CommonHttpProtocolOptions](#commonhttpprotocoloptions)_ | Additional options when handling HTTP requests upstream, applicable to<br />both HTTP1 and HTTP2 requests. |  |  |
| `http1ProtocolOptions` _[Http1ProtocolOptions](#http1protocoloptions)_ | Additional options when handling HTTP1 requests upstream. |  |  |
| `http2ProtocolOptions` _[Http2ProtocolOptions](#http2protocoloptions)_ | Http2ProtocolOptions contains the options necessary to configure HTTP/2 backends.<br />Note: Http2ProtocolOptions can only be applied to HTTP/2 backends.<br />See [Envoy documentation](https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/transport_sockets/tls/v3/tls.proto#envoy-v3-api-msg-extensions-transport-sockets-tls-v3-sslconfig) for more details. |  |  |
| `tls` _[TLS](#tls)_ | TLS contains the options necessary to configure a backend to use TLS origination.<br />See [Envoy documentation](https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/transport_sockets/tls/v3/tls.proto#envoy-v3-api-msg-extensions-transport-sockets-tls-v3-sslconfig) for more details. |  |  |
| `loadBalancer` _[LoadBalancer](#loadbalancer)_ | LoadBalancer contains the options necessary to configure the load balancer. |  |  |
| `healthCheck` _[HealthCheck](#healthcheck)_ | HealthCheck contains the options necessary to configure the health check. |  |  |
| `outlierDetection` _[OutlierDetection](#outlierdetection)_ | OutlierDetection contains the options necessary to configure passive health checking. |  |  |


#### BackendSpec



BackendSpec defines the desired state of Backend.



_Appears in:_
- [Backend](#backend)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `type` _[BackendType](#backendtype)_ | Type indicates the type of the backend to be used. |  | Enum: [AI AWS Static DynamicForwardProxy MCP] <br /> |
| `ai` _[AIBackend](#aibackend)_ | AI is the AI backend configuration. |  | MaxProperties: 1 <br />MinProperties: 1 <br /> |
| `aws` _[AwsBackend](#awsbackend)_ | Aws is the AWS backend configuration.<br />The Aws backend type is only supported with envoy-based gateways, it is not supported in agentgateway. |  |  |
| `static` _[StaticBackend](#staticbackend)_ | Static is the static backend configuration. |  |  |
| `dynamicForwardProxy` _[DynamicForwardProxyBackend](#dynamicforwardproxybackend)_ | DynamicForwardProxy is the dynamic forward proxy backend configuration.<br />The DynamicForwardProxy backend type is only supported with envoy-based gateways, it is not supported in agentgateway. |  |  |
| `mcp` _[MCP](#mcp)_ | MCP is the mcp backend configuration. The MCP backend type is only supported with agentgateway. |  |  |


#### BackendStatus



BackendStatus defines the observed state of Backend.



_Appears in:_
- [Backend](#backend)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `conditions` _[Condition](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#condition-v1-meta) array_ | Conditions is the list of conditions for the backend. |  | MaxItems: 8 <br /> |


#### BackendType

_Underlying type:_ _string_

BackendType indicates the type of the backend.



_Appears in:_
- [BackendSpec](#backendspec)

| Field | Description |
| --- | --- |
| `AI` | BackendTypeAI is the type for AI backends.<br /> |
| `AWS` | BackendTypeAWS is the type for AWS backends.<br /> |
| `Static` | BackendTypeStatic is the type for static backends.<br /> |
| `DynamicForwardProxy` | BackendTypeDynamicForwardProxy is the type for dynamic forward proxy backends.<br /> |
| `MCP` | BackendTypeMCP is the type for MCP backends.<br /> |




#### BedrockConfig







_Appears in:_
- [SupportedLLMProvider](#supportedllmprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `auth` _[AwsAuth](#awsauth)_ | Auth specifies an explicit AWS authentication method for the backend.<br />When omitted, the following credential providers are tried in order, stopping when one<br />of them returns an access key ID and a secret access key (the session token is optional):<br />1. Environment variables: when the environment variables AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_SESSION_TOKEN are set.<br />2. AssumeRoleWithWebIdentity API call: when the environment variables AWS_WEB_IDENTITY_TOKEN_FILE and AWS_ROLE_ARN are set.<br />3. EKS Pod Identity: when the environment variable AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE is set.<br /><br />See the Envoy docs for more info:<br />https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/aws_request_signing_filter#credentials |  |  |
| `model` _string_ | The model field is the supported model id published by AWS. See <https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html> |  | MinLength: 1 <br /> |
| `region` _string_ | Region is the AWS region to use for the backend.<br />Defaults to us-east-1 if not specified. | us-east-1 | MaxLength: 63 <br />MinLength: 1 <br />Pattern: `^[a-z0-9-]+$` <br /> |
| `guardrail` _[AWSGuardrailConfig](#awsguardrailconfig)_ | Guardrail configures the Guardrail policy to use for the backend. See <https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html><br />If not specified, the AWS Guardrail policy will not be used. |  |  |


#### BodyParseBehavior

_Underlying type:_ _string_

BodyparseBehavior defines how the body should be parsed
If set to json and the body is not json then the filter will not perform the transformation.

_Validation:_
- Enum: [AsString AsJson]

_Appears in:_
- [BodyTransformation](#bodytransformation)

| Field | Description |
| --- | --- |
| `AsString` | BodyParseBehaviorAsString will parse the body as a string.<br /> |
| `AsJson` | BodyParseBehaviorAsJSON will parse the body as a json object.<br /> |


#### BodyTransformation



BodyTransformation controls how the body should be parsed and transformed.



_Appears in:_
- [Transform](#transform)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `parseAs` _[BodyParseBehavior](#bodyparsebehavior)_ | ParseAs defines what auto formatting should be applied to the body.<br />This can make interacting with keys within a json body much easier if AsJson is selected. | AsString | Enum: [AsString AsJson] <br /> |
| `value` _[InjaTemplate](#injatemplate)_ | Value is the template to apply to generate the output value for the body. |  |  |


#### Buffer







_Appears in:_
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `maxRequestSize` _[Quantity](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#quantity-resource-api)_ | MaxRequestSize sets the maximum size in bytes of a message body to buffer.<br />Requests exceeding this size will receive HTTP 413.<br />Example format: "1Mi", "512Ki", "1Gi" |  |  |
| `disable` _[PolicyDisable](#policydisable)_ | Disable the buffer filter.<br />Can be used to disable buffer policies applied at a higher level in the config hierarchy. |  |  |


#### BufferSettings



BufferSettings configures how the request body should be buffered.



_Appears in:_
- [ExtAuthPolicy](#extauthpolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `maxRequestBytes` _integer_ | MaxRequestBytes sets the maximum size of a message body to buffer.<br />Requests exceeding this size will receive HTTP 413 and not be sent to the authorization service. |  | Minimum: 1 <br /> |
| `allowPartialMessage` _boolean_ | AllowPartialMessage determines if partial messages should be allowed.<br />When true, requests will be sent to the authorization service even if they exceed maxRequestBytes.<br />When unset, the default behavior is false. |  |  |
| `packAsBytes` _boolean_ | PackAsBytes determines if the body should be sent as raw bytes.<br />When true, the body is sent as raw bytes in the raw_body field.<br />When false, the body is sent as UTF-8 string in the body field.<br />When unset, the default behavior is false. |  |  |


#### BuiltIn

_Underlying type:_ _string_

BuiltIn regex patterns for specific types of strings in prompts.
For example, if you specify `CREDIT_CARD`, any credit card numbers
in the request or response are matched.

_Validation:_
- Enum: [SSN CREDIT_CARD PHONE_NUMBER EMAIL]

_Appears in:_
- [Regex](#regex)

| Field | Description |
| --- | --- |
| `SSN` | Default regex matching for Social Security numbers.<br /> |
| `CREDIT_CARD` | Default regex matching for credit card numbers.<br /> |
| `PHONE_NUMBER` | Default regex matching for phone numbers.<br /> |
| `EMAIL` | Default regex matching for email addresses.<br /> |


#### CELFilter



CELFilter filters requests based on Common Expression Language (CEL).



_Appears in:_
- [FilterType](#filtertype)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `match` _string_ | The CEL expressions to evaluate. AccessLogs are only emitted when the CEL expressions evaluates to true.<br />see: https://www.envoyproxy.io/docs/envoy/v1.33.0/xds/type/v3/cel.proto.html#common-expression-language-cel-proto |  |  |


#### CSRFPolicy



CSRFPolicy can be used to set percent of requests for which the CSRF filter is enabled,
enable shadow-only mode where policies will be evaluated and tracked, but not enforced and
add additional source origins that will be allowed in addition to the destination origin.



_Appears in:_
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `percentageEnabled` _integer_ | Specifies the percentage of requests for which the CSRF filter is enabled. |  | Maximum: 100 <br />Minimum: 0 <br /> |
| `percentageShadowed` _integer_ | Specifies that CSRF policies will be evaluated and tracked, but not enforced. |  | Maximum: 100 <br />Minimum: 0 <br /> |
| `additionalOrigins` _[StringMatcher](#stringmatcher) array_ | Specifies additional source origins that will be allowed in addition to the destination origin. |  | MaxItems: 16 <br /> |


#### CommonAccessLogGrpcService



Common configuration for gRPC access logs.
Ref: https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/access_loggers/grpc/v3/als.proto#envoy-v3-api-msg-extensions-access-loggers-grpc-v3-commongrpcaccesslogconfig



_Appears in:_
- [AccessLogGrpcService](#accessloggrpcservice)
- [OpenTelemetryAccessLogService](#opentelemetryaccesslogservice)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `backendRef` _[BackendRef](#backendref)_ | The backend gRPC service. Can be any type of supported backend (Kubernetes Service, kgateway Backend, etc..) |  |  |
| `authority` _string_ | The :authority header in the grpc request. If this field is not set, the authority header value will be cluster_name.<br />Note that this authority does not override the SNI. The SNI is provided by the transport socket of the cluster. |  |  |
| `maxReceiveMessageLength` _integer_ | Maximum gRPC message size that is allowed to be received. If a message over this limit is received, the gRPC stream is terminated with the RESOURCE_EXHAUSTED error.<br />Defaults to 0, which means unlimited. |  |  |
| `skipEnvoyHeaders` _boolean_ | This provides gRPC client level control over envoy generated headers. If false, the header will be sent but it can be overridden by per stream option. If true, the header will be removed and can not be overridden by per stream option. Default to false. |  |  |
| `timeout` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | The timeout for the gRPC request. This is the timeout for a specific request |  |  |
| `initialMetadata` _[HeaderValue](#headervalue) array_ | Additional metadata to include in streams initiated to the GrpcService.<br />This can be used for scenarios in which additional ad hoc authorization headers (e.g. x-foo-bar: baz-key) are to be injected |  |  |
| `retryPolicy` _[RetryPolicy](#retrypolicy)_ | Indicates the retry policy for re-establishing the gRPC stream.<br />If max interval is not provided, it will be set to ten times the provided base interval |  |  |
| `logName` _string_ | name of log stream |  |  |


#### CommonGrpcService



Common gRPC service configuration created by setting `envoy_grpc“ as the gRPC client
Ref: https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/core/v3/grpc_service.proto#envoy-v3-api-msg-config-core-v3-grpcservice
Ref: https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/core/v3/grpc_service.proto#envoy-v3-api-msg-config-core-v3-grpcservice-envoygrpc



_Appears in:_
- [AccessLogGrpcService](#accessloggrpcservice)
- [CommonAccessLogGrpcService](#commonaccessloggrpcservice)
- [OpenTelemetryTracingConfig](#opentelemetrytracingconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `backendRef` _[BackendRef](#backendref)_ | The backend gRPC service. Can be any type of supported backend (Kubernetes Service, kgateway Backend, etc..) |  |  |
| `authority` _string_ | The :authority header in the grpc request. If this field is not set, the authority header value will be cluster_name.<br />Note that this authority does not override the SNI. The SNI is provided by the transport socket of the cluster. |  |  |
| `maxReceiveMessageLength` _integer_ | Maximum gRPC message size that is allowed to be received. If a message over this limit is received, the gRPC stream is terminated with the RESOURCE_EXHAUSTED error.<br />Defaults to 0, which means unlimited. |  |  |
| `skipEnvoyHeaders` _boolean_ | This provides gRPC client level control over envoy generated headers. If false, the header will be sent but it can be overridden by per stream option. If true, the header will be removed and can not be overridden by per stream option. Default to false. |  |  |
| `timeout` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | The timeout for the gRPC request. This is the timeout for a specific request |  |  |
| `initialMetadata` _[HeaderValue](#headervalue) array_ | Additional metadata to include in streams initiated to the GrpcService.<br />This can be used for scenarios in which additional ad hoc authorization headers (e.g. x-foo-bar: baz-key) are to be injected |  |  |
| `retryPolicy` _[RetryPolicy](#retrypolicy)_ | Indicates the retry policy for re-establishing the gRPC stream.<br />If max interval is not provided, it will be set to ten times the provided base interval |  |  |


#### CommonHttpProtocolOptions



CommonHttpProtocolOptions are options that are applicable to both HTTP1 and HTTP2 requests.
See [Envoy documentation](https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/core/v3/protocol.proto#envoy-v3-api-msg-config-core-v3-httpprotocoloptions) for more details.



_Appears in:_
- [BackendConfigPolicySpec](#backendconfigpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `idleTimeout` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | The idle timeout for connections. The idle timeout is defined as the<br />period in which there are no active requests. When the<br />idle timeout is reached the connection will be closed. If the connection is an HTTP/2<br />downstream connection a drain sequence will occur prior to closing the connection.<br />Note that request based timeouts mean that HTTP/2 PINGs will not keep the connection alive.<br />If not specified, this defaults to 1 hour. To disable idle timeouts explicitly set this to 0.<br />	Disabling this timeout has a highly likelihood of yielding connection leaks due to lost TCP<br />	FIN packets, etc. |  |  |
| `maxHeadersCount` _integer_ | Specifies the maximum number of headers that the connection will accept.<br />If not specified, the default of 100 is used. Requests that exceed this limit will receive<br />a 431 response for HTTP/1.x and cause a stream reset for HTTP/2. |  |  |
| `maxStreamDuration` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | Total duration to keep alive an HTTP request/response stream. If the time limit is reached the stream will be<br />reset independent of any other timeouts. If not specified, this value is not set. |  |  |
| `maxRequestsPerConnection` _integer_ | Maximum requests for a single upstream connection.<br />If set to 0 or unspecified, defaults to unlimited. |  |  |


#### ComparisonFilter

_Underlying type:_ _[struct{Op Op "json:\"op,omitempty\""; Value uint32 "json:\"value,omitempty\""}](#struct{op-op-"json:\"op,omitempty\"";-value-uint32-"json:\"value,omitempty\""})_

ComparisonFilter represents a filter based on a comparison.
Based on: https://www.envoyproxy.io/docs/envoy/v1.33.0/api-v3/config/accesslog/v3/accesslog.proto#config-accesslog-v3-comparisonfilter



_Appears in:_
- [DurationFilter](#durationfilter)
- [StatusCodeFilter](#statuscodefilter)



#### Cookie

_Underlying type:_ _[struct{Name string "json:\"name\""; Path *string "json:\"path,omitempty\""; TTL *k8s.io/apimachinery/pkg/apis/meta/v1.Duration "json:\"ttl,omitempty\""; Secure *bool "json:\"secure,omitempty\""; HttpOnly *bool "json:\"httpOnly,omitempty\""; SameSite *string "json:\"sameSite,omitempty\""}](#struct{name-string-"json:\"name\"";-path-*string-"json:\"path,omitempty\"";-ttl-*k8sioapimachinerypkgapismetav1duration-"json:\"ttl,omitempty\"";-secure-*bool-"json:\"secure,omitempty\"";-httponly-*bool-"json:\"httponly,omitempty\"";-samesite-*string-"json:\"samesite,omitempty\""})_





_Appears in:_
- [HashPolicy](#hashpolicy)



#### CorsPolicy







_Appears in:_
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `disable` _[PolicyDisable](#policydisable)_ | Disable the CORS filter.<br />Can be used to disable CORS policies applied at a higher level in the config hierarchy. |  |  |


#### CustomAttribute



Describes attributes for the active span.
Ref: https://www.envoyproxy.io/docs/envoy/latest/api-v3/type/tracing/v3/custom_tag.proto#envoy-v3-api-msg-type-tracing-v3-customtag

_Validation:_
- MaxProperties: 2
- MinProperties: 1

_Appears in:_
- [Tracing](#tracing)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ | The name of the attribute |  |  |
| `literal` _[CustomAttributeLiteral](#customattributeliteral)_ | A literal attribute value. |  |  |
| `environment` _[CustomAttributeEnvironment](#customattributeenvironment)_ | An environment attribute value. |  |  |
| `requestHeader` _[CustomAttributeHeader](#customattributeheader)_ | A request header attribute value. |  |  |
| `metadata` _[CustomAttributeMetadata](#customattributemetadata)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |


#### CustomAttributeEnvironment



Environment type attribute with environment name and default value.
Ref: https://www.envoyproxy.io/docs/envoy/latest/api-v3/type/tracing/v3/custom_tag.proto#type-tracing-v3-customtag-environment



_Appears in:_
- [CustomAttribute](#customattribute)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ | Environment variable name to obtain the value to populate the attribute value. |  |  |
| `defaultValue` _string_ | When the environment variable is not found, the attribute value will be populated with this default value if specified,<br />otherwise no attribute will be populated. |  |  |


#### CustomAttributeHeader



Header type attribute with header name and default value.
https://www.envoyproxy.io/docs/envoy/latest/api-v3/type/tracing/v3/custom_tag.proto#type-tracing-v3-customtag-header



_Appears in:_
- [CustomAttribute](#customattribute)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ | Header name to obtain the value to populate the attribute value. |  |  |
| `defaultValue` _string_ | When the header does not exist, the attribute value will be populated with this default value if specified,<br />otherwise no attribute will be populated. |  |  |


#### CustomAttributeLiteral



Literal type attribute with a static value.
Ref: https://www.envoyproxy.io/docs/envoy/latest/api-v3/type/tracing/v3/custom_tag.proto#type-tracing-v3-customtag-literal



_Appears in:_
- [CustomAttribute](#customattribute)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `value` _string_ | Static literal value to populate the attribute value. |  |  |


#### CustomAttributeMetadata



Metadata type attribute using MetadataKey to retrieve the protobuf value from Metadata, and populate the attribute value with the canonical JSON representation of it.
Ref: https://www.envoyproxy.io/docs/envoy/latest/api-v3/type/tracing/v3/custom_tag.proto#type-tracing-v3-customtag-metadata



_Appears in:_
- [CustomAttribute](#customattribute)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `kind` _[MetadataKind](#metadatakind)_ | Specify what kind of metadata to obtain attribute value from |  | Enum: [Request Route Cluster Host] <br /> |
| `metadataKey` _[MetadataKey](#metadatakey)_ | Metadata key to define the path to retrieve the attribute value. |  |  |
| `defaultValue` _string_ | When no valid metadata is found, the attribute value would be populated with this default value if specified, otherwise no attribute would be populated. |  |  |


#### CustomLabel







_Appears in:_
- [AiExtensionStats](#aiextensionstats)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ | Name of the label to use in the prometheus metrics |  | MinLength: 1 <br /> |
| `metadataNamespace` _string_ | The dynamic metadata namespace to get the data from. If not specified, the default namespace will be<br />the envoy JWT filter namespace.<br />This can also be used in combination with early_transformations to insert custom data. |  | Enum: [envoy.filters.http.jwt_authn io.solo.transformation] <br /> |
| `metadataKey` _string_ | The key to use to get the data from the metadata namespace.<br />If using a JWT data please see the following envoy docs: https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/filters/http/jwt_authn/v3/config.proto#envoy-v3-api-field-extensions-filters-http-jwt-authn-v3-jwtprovider-payload-in-metadata<br />This key follows the same format as the envoy access logging for dynamic metadata.<br />Examples can be found here: https://www.envoyproxy.io/docs/envoy/latest/configuration/observability/access_log/usage |  | MinLength: 1 <br /> |
| `keyDelimiter` _string_ | The key delimiter to use, by default this is set to `:`.<br />This allows for keys with `.` in them to be used.<br />For example, if you have keys in your path with `:` in them, (e.g. `key1:key2:value`)<br />you can instead set this to `~` to be able to split those keys properly. |  |  |


#### CustomResponse



CustomResponse configures a response to return to the client if request content
is matched against a regex pattern and the action is `REJECT`.



_Appears in:_
- [PromptguardRequest](#promptguardrequest)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `message` _string_ | A custom response message to return to the client. If not specified, defaults to<br />"The request was rejected due to inappropriate content". | The request was rejected due to inappropriate content |  |
| `statusCode` _integer_ | The status code to return to the client. Defaults to 403. | 403 | Maximum: 599 <br />Minimum: 200 <br /> |




#### DirectResponse



DirectResponse contains configuration for defining direct response routes.





| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `gateway.kgateway.dev/v1alpha1` | | |
| `kind` _string_ | `DirectResponse` | | |
| `kind` _string_ | Kind is a string value representing the REST resource this object represents.<br />Servers may infer this from the endpoint the client submits requests to.<br />Cannot be updated.<br />In CamelCase.<br />More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds |  |  |
| `apiVersion` _string_ | APIVersion defines the versioned schema of this representation of an object.<br />Servers should convert recognized schemas to the latest internal value, and<br />may reject unrecognized values.<br />More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources |  |  |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[DirectResponseSpec](#directresponsespec)_ |  |  |  |
| `status` _[DirectResponseStatus](#directresponsestatus)_ |  |  |  |


#### DirectResponseSpec



DirectResponseSpec describes the desired state of a DirectResponse.



_Appears in:_
- [DirectResponse](#directresponse)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `status` _integer_ | StatusCode defines the HTTP status code to return for this route. |  | Maximum: 599 <br />Minimum: 200 <br /> |
| `body` _string_ | Body defines the content to be returned in the HTTP response body.<br />The maximum length of the body is restricted to prevent excessively large responses.<br />If this field is omitted, no body is included in the response. |  | MaxLength: 4096 <br />MinLength: 1 <br /> |


#### DirectResponseStatus



DirectResponseStatus defines the observed state of a DirectResponse.



_Appears in:_
- [DirectResponse](#directresponse)



#### DurationFilter

_Underlying type:_ _[ComparisonFilter](#comparisonfilter)_

DurationFilter filters based on request duration.
Based on: https://www.envoyproxy.io/docs/envoy/v1.33.0/api-v3/config/accesslog/v3/accesslog.proto#config-accesslog-v3-durationfilter



_Appears in:_
- [FilterType](#filtertype)



#### DynamicForwardProxyBackend



DynamicForwardProxyBackend is the dynamic forward proxy backend configuration.



_Appears in:_
- [BackendSpec](#backendspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `enableTls` _boolean_ | EnableTls enables TLS. When true, the backend will be configured to use TLS. System CA will be used for validation.<br />The hostname will be used for SNI and auto SAN validation. |  |  |


#### EnvironmentResourceDetectorConfig

_Underlying type:_ _[struct{}](#struct{})_

EnvironmentResourceDetectorConfig specified the EnvironmentResourceDetector



_Appears in:_
- [ResourceDetector](#resourcedetector)



#### EnvoyBootstrap



EnvoyBootstrap configures the Envoy proxy instance that is provisioned from a
Kubernetes Gateway.



_Appears in:_
- [EnvoyContainer](#envoycontainer)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `logLevel` _string_ | Envoy log level. Options include "trace", "debug", "info", "warn", "error",<br />"critical" and "off". Defaults to "info". See<br />https://www.envoyproxy.io/docs/envoy/latest/start/quick-start/run-envoy#debugging-envoy<br />for more information. |  |  |
| `componentLogLevels` _object (keys:string, values:string)_ | Envoy log levels for specific components. The keys are component names and<br />the values are one of "trace", "debug", "info", "warn", "error",<br />"critical", or "off", e.g.<br /><br />		componentLogLevels:<br />	  upstream: debug<br />	  connection: trace<br />	<br /><br />These will be converted to the `--component-log-level` Envoy argument<br />value. See<br />https://www.envoyproxy.io/docs/envoy/latest/start/quick-start/run-envoy#debugging-envoy<br />for more information.<br /><br />Note: the keys and values cannot be empty, but they are not otherwise validated. |  |  |


#### EnvoyContainer



EnvoyContainer configures the container running Envoy.



_Appears in:_
- [KubernetesProxyConfig](#kubernetesproxyconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `bootstrap` _[EnvoyBootstrap](#envoybootstrap)_ | Initial envoy configuration. |  |  |
| `image` _[Image](#image)_ | The envoy container image. See<br />https://kubernetes.io/docs/concepts/containers/images<br />for details.<br /><br />Default values, which may be overridden individually:<br /><br />	registry: quay.io/solo-io<br />	repository: envoy-wrapper<br />	tag: <kgateway version><br />	pullPolicy: IfNotPresent |  |  |
| `securityContext` _[SecurityContext](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#securitycontext-v1-core)_ | The security context for this container. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#securitycontext-v1-core<br />for details. |  |  |
| `resources` _[ResourceRequirements](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#resourcerequirements-v1-core)_ | The compute resources required by this container. See<br />https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/<br />for details. |  |  |
| `env` _[EnvVar](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#envvar-v1-core) array_ | The container environment variables. |  |  |


#### EnvoyHealthCheck



EnvoyHealthCheck represents configuration for Envoy's health check filter.
The filter will be configured in No pass through mode, and will only match requests with the specified path.



_Appears in:_
- [HTTPListenerPolicySpec](#httplistenerpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `path` _string_ | Path defines the exact path that will be matched for health check requests. |  | MaxLength: 2048 <br />Pattern: `^/[-a-zA-Z0-9@:%.+~#?&/=_]+$` <br /> |


#### ExtAuthPolicy



ExtAuthPolicy configures external authentication for a route.
This policy will determine the ext auth server to use and how to  talk to it.
Note that most of these fields are passed along as is to Envoy.
For more details on particular fields please see the Envoy ExtAuth documentation.
https://raw.githubusercontent.com/envoyproxy/envoy/f910f4abea24904aff04ec33a00147184ea7cffa/api/envoy/extensions/filters/http/ext_authz/v3/ext_authz.proto



_Appears in:_
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `extensionRef` _[NamespacedObjectReference](#namespacedobjectreference)_ | ExtensionRef references the GatewayExtension that should be used for authentication. |  |  |
| `withRequestBody` _[BufferSettings](#buffersettings)_ | WithRequestBody allows the request body to be buffered and sent to the authorization service.<br />Warning buffering has implications for streaming and therefore performance. |  |  |
| `contextExtensions` _object (keys:string, values:string)_ | Additional context for the authorization service. |  |  |
| `disable` _[PolicyDisable](#policydisable)_ | Disable all external authorization filters.<br />Can be used to disable external authorization policies applied at a higher level in the config hierarchy. |  |  |


#### ExtAuthProvider



ExtAuthProvider defines the configuration for an ExtAuth provider.



_Appears in:_
- [GatewayExtensionSpec](#gatewayextensionspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `grpcService` _[ExtGrpcService](#extgrpcservice)_ | GrpcService is the GRPC service that will handle the authentication. |  |  |


#### ExtGrpcService



ExtGrpcService defines the GRPC service that will handle the processing.



_Appears in:_
- [ExtAuthProvider](#extauthprovider)
- [ExtProcProvider](#extprocprovider)
- [RateLimitProvider](#ratelimitprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `backendRef` _[BackendRef](#backendref)_ | BackendRef references the backend GRPC service. |  |  |
| `authority` _string_ | Authority is the authority header to use for the GRPC service. |  |  |


#### ExtProcPolicy



ExtProcPolicy defines the configuration for the Envoy External Processing filter.



_Appears in:_
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `extensionRef` _[NamespacedObjectReference](#namespacedobjectreference)_ | ExtensionRef references the GatewayExtension that should be used for external processing. |  |  |
| `processingMode` _[ProcessingMode](#processingmode)_ | ProcessingMode defines how the filter should interact with the request/response streams |  |  |
| `disable` _[PolicyDisable](#policydisable)_ | Disable all external processing filters.<br />Can be used to disable external processing policies applied at a higher level in the config hierarchy. |  |  |


#### ExtProcProvider



ExtProcProvider defines the configuration for an ExtProc provider.



_Appears in:_
- [GatewayExtensionSpec](#gatewayextensionspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `grpcService` _[ExtGrpcService](#extgrpcservice)_ | GrpcService is the GRPC service that will handle the processing. |  |  |


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


Example: Overriding a custom list field:
```yaml
defaults:
  - field: "custom_list"
    value: "[a,b,c]"
```


Note: The `field` values correspond to keys in the JSON request body, not fields in this CRD.



_Appears in:_
- [AIPolicy](#aipolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `field` _string_ | The name of the field. |  | MinLength: 1 <br /> |
| `value` _string_ | The field default value, which can be any JSON Data Type. |  | MinLength: 1 <br /> |
| `override` _boolean_ | Whether to override the field's value if it already exists.<br />Defaults to false. | false |  |


#### FileSink



FileSink represents the file sink configuration for access logs.



_Appears in:_
- [AccessLog](#accesslog)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `path` _string_ | the file path to which the file access logging service will sink |  |  |
| `stringFormat` _string_ | the format string by which envoy will format the log lines<br />https://www.envoyproxy.io/docs/envoy/v1.33.0/configuration/observability/access_log/usage#format-strings |  |  |
| `jsonFormat` _[RawExtension](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#rawextension-runtime-pkg)_ | the format object by which to envoy will emit the logs in a structured way.<br />https://www.envoyproxy.io/docs/envoy/v1.33.0/configuration/observability/access_log/usage#format-dictionaries |  |  |


#### FilterType



FilterType represents the type of filter to apply (only one of these should be set).
Based on: https://www.envoyproxy.io/docs/envoy/v1.33.0/api-v3/config/accesslog/v3/accesslog.proto#envoy-v3-api-msg-config-accesslog-v3-accesslogfilter

_Validation:_
- MaxProperties: 1
- MinProperties: 1

_Appears in:_
- [AccessLogFilter](#accesslogfilter)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `statusCodeFilter` _[StatusCodeFilter](#statuscodefilter)_ |  |  |  |
| `durationFilter` _[DurationFilter](#durationfilter)_ |  |  |  |
| `notHealthCheckFilter` _boolean_ | Filters for requests that are not health check requests.<br />Based on: https://www.envoyproxy.io/docs/envoy/v1.33.0/api-v3/config/accesslog/v3/accesslog.proto#config-accesslog-v3-nothealthcheckfilter |  |  |
| `traceableFilter` _boolean_ | Filters for requests that are traceable.<br />Based on: https://www.envoyproxy.io/docs/envoy/v1.33.0/api-v3/config/accesslog/v3/accesslog.proto#config-accesslog-v3-traceablefilter |  |  |
| `headerFilter` _[HeaderFilter](#headerfilter)_ |  |  |  |
| `responseFlagFilter` _[ResponseFlagFilter](#responseflagfilter)_ |  |  |  |
| `grpcStatusFilter` _[GrpcStatusFilter](#grpcstatusfilter)_ |  |  |  |
| `celFilter` _[CELFilter](#celfilter)_ |  |  |  |


#### GatewayExtension









| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `gateway.kgateway.dev/v1alpha1` | | |
| `kind` _string_ | `GatewayExtension` | | |
| `kind` _string_ | Kind is a string value representing the REST resource this object represents.<br />Servers may infer this from the endpoint the client submits requests to.<br />Cannot be updated.<br />In CamelCase.<br />More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds |  |  |
| `apiVersion` _string_ | APIVersion defines the versioned schema of this representation of an object.<br />Servers should convert recognized schemas to the latest internal value, and<br />may reject unrecognized values.<br />More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources |  |  |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[GatewayExtensionSpec](#gatewayextensionspec)_ |  |  |  |
| `status` _[GatewayExtensionStatus](#gatewayextensionstatus)_ |  |  |  |


#### GatewayExtensionSpec



GatewayExtensionSpec defines the desired state of GatewayExtension.



_Appears in:_
- [GatewayExtension](#gatewayextension)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `type` _[GatewayExtensionType](#gatewayextensiontype)_ | Type indicates the type of the GatewayExtension to be used. |  | Enum: [ExtAuth ExtProc RateLimit] <br /> |
| `extAuth` _[ExtAuthProvider](#extauthprovider)_ | ExtAuth configuration for ExtAuth extension type. |  |  |
| `extProc` _[ExtProcProvider](#extprocprovider)_ | ExtProc configuration for ExtProc extension type. |  |  |
| `rateLimit` _[RateLimitProvider](#ratelimitprovider)_ | RateLimit configuration for RateLimit extension type. |  |  |


#### GatewayExtensionStatus



GatewayExtensionStatus defines the observed state of GatewayExtension.



_Appears in:_
- [GatewayExtension](#gatewayextension)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `conditions` _[Condition](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#condition-v1-meta) array_ | Conditions is the list of conditions for the GatewayExtension. |  | MaxItems: 8 <br /> |


#### GatewayExtensionType

_Underlying type:_ _string_

GatewayExtensionType indicates the type of the GatewayExtension.



_Appears in:_
- [GatewayExtensionSpec](#gatewayextensionspec)

| Field | Description |
| --- | --- |
| `ExtAuth` | GatewayExtensionTypeExtAuth is the type for Extauth extensions.<br /> |
| `ExtProc` | GatewayExtensionTypeExtProc is the type for ExtProc extensions.<br /> |
| `RateLimit` | GatewayExtensionTypeRateLimit is the type for RateLimit extensions.<br /> |


#### GatewayParameters



A GatewayParameters contains configuration that is used to dynamically
provision kgateway's data plane (Envoy proxy instance), based on a
Kubernetes Gateway.





| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `gateway.kgateway.dev/v1alpha1` | | |
| `kind` _string_ | `GatewayParameters` | | |
| `kind` _string_ | Kind is a string value representing the REST resource this object represents.<br />Servers may infer this from the endpoint the client submits requests to.<br />Cannot be updated.<br />In CamelCase.<br />More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds |  |  |
| `apiVersion` _string_ | APIVersion defines the versioned schema of this representation of an object.<br />Servers should convert recognized schemas to the latest internal value, and<br />may reject unrecognized values.<br />More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources |  |  |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[GatewayParametersSpec](#gatewayparametersspec)_ |  |  |  |
| `status` _[GatewayParametersStatus](#gatewayparametersstatus)_ |  |  |  |


#### GatewayParametersSpec



A GatewayParametersSpec describes the type of environment/platform in which
the proxy will be provisioned.



_Appears in:_
- [GatewayParameters](#gatewayparameters)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `kube` _[KubernetesProxyConfig](#kubernetesproxyconfig)_ | The proxy will be deployed on Kubernetes. |  |  |
| `selfManaged` _[SelfManagedGateway](#selfmanagedgateway)_ | The proxy will be self-managed and not auto-provisioned. |  |  |


#### GatewayParametersStatus



The current conditions of the GatewayParameters. This is not currently implemented.



_Appears in:_
- [GatewayParameters](#gatewayparameters)



#### GeminiConfig



GeminiConfig settings for the [Gemini](https://ai.google.dev/gemini-api/docs) LLM provider.



_Appears in:_
- [SupportedLLMProvider](#supportedllmprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `authToken` _[SingleAuthToken](#singleauthtoken)_ | The authorization token that the AI gateway uses to access the Gemini API.<br />This token is automatically sent in the `key` query parameter of the request. |  |  |
| `model` _string_ | The Gemini model to use.<br />For more information, see the [Gemini models docs](https://ai.google.dev/gemini-api/docs/models/gemini). |  |  |
| `apiVersion` _string_ | The version of the Gemini API to use.<br />For more information, see the [Gemini API version docs](https://ai.google.dev/gemini-api/docs/api-versions). |  |  |


#### GracefulShutdownSpec







_Appears in:_
- [Pod](#pod)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `enabled` _boolean_ | Enable grace period before shutdown to finish current requests while Envoy health checks fail to e.g. notify external load balancers. *NOTE:* This will not have any effect if you have not defined health checks via the health check filter |  |  |
| `sleepTimeSeconds` _integer_ | Time (in seconds) for the preStop hook to wait before allowing Envoy to terminate |  |  |




#### GrpcStatusFilter



GrpcStatusFilter filters gRPC requests based on their response status.
Based on: https://www.envoyproxy.io/docs/envoy/v1.33.0/api-v3/config/accesslog/v3/accesslog.proto#enum-config-accesslog-v3-grpcstatusfilter-status



_Appears in:_
- [FilterType](#filtertype)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `statuses` _[GrpcStatus](#grpcstatus) array_ |  |  | Enum: [OK CANCELED UNKNOWN INVALID_ARGUMENT DEADLINE_EXCEEDED NOT_FOUND ALREADY_EXISTS PERMISSION_DENIED RESOURCE_EXHAUSTED FAILED_PRECONDITION ABORTED OUT_OF_RANGE UNIMPLEMENTED INTERNAL UNAVAILABLE DATA_LOSS UNAUTHENTICATED] <br />MinItems: 1 <br /> |
| `exclude` _boolean_ |  |  |  |


#### HTTPListenerPolicy



HTTPListenerPolicy is intended to be used for configuring the Envoy `HttpConnectionManager` and any other config or policy
that should map 1-to-1 with a given HTTP listener, such as the Envoy health check HTTP filter.
Currently these policies can only be applied per `Gateway` but support for `Listener` attachment may be added in the future.
See https://github.com/kgateway-dev/kgateway/issues/11786 for more details.





| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `gateway.kgateway.dev/v1alpha1` | | |
| `kind` _string_ | `HTTPListenerPolicy` | | |
| `kind` _string_ | Kind is a string value representing the REST resource this object represents.<br />Servers may infer this from the endpoint the client submits requests to.<br />Cannot be updated.<br />In CamelCase.<br />More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds |  |  |
| `apiVersion` _string_ | APIVersion defines the versioned schema of this representation of an object.<br />Servers should convert recognized schemas to the latest internal value, and<br />may reject unrecognized values.<br />More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources |  |  |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[HTTPListenerPolicySpec](#httplistenerpolicyspec)_ |  |  |  |
| `status` _[PolicyStatus](#policystatus)_ |  |  |  |


#### HTTPListenerPolicySpec



HTTPListenerPolicySpec defines the desired state of a HTTP listener policy.



_Appears in:_
- [HTTPListenerPolicy](#httplistenerpolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `targetRefs` _[LocalPolicyTargetReference](#localpolicytargetreference) array_ | TargetRefs specifies the target resources by reference to attach the policy to. |  | MaxItems: 16 <br />MinItems: 1 <br /> |
| `targetSelectors` _[LocalPolicyTargetSelector](#localpolicytargetselector) array_ | TargetSelectors specifies the target selectors to select resources to attach the policy to. |  |  |
| `accessLog` _[AccessLog](#accesslog) array_ | AccessLoggingConfig contains various settings for Envoy's access logging service.<br />See here for more information: https://www.envoyproxy.io/docs/envoy/v1.33.0/api-v3/config/accesslog/v3/accesslog.proto |  | MaxItems: 16 <br /> |
| `tracing` _[Tracing](#tracing)_ | Tracing contains various settings for Envoy's OpenTelemetry tracer.<br />See here for more information: https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/trace/v3/opentelemetry.proto.html |  |  |
| `upgradeConfig` _[UpgradeConfig](#upgradeconfig)_ | UpgradeConfig contains configuration for HTTP upgrades like WebSocket.<br />See here for more information: https://www.envoyproxy.io/docs/envoy/v1.34.1/intro/arch_overview/http/upgrades.html |  |  |
| `useRemoteAddress` _boolean_ | UseRemoteAddress determines whether to use the remote address for the original client.<br />Note: If this field is omitted, it will fallback to the default value of 'true', which we set for all Envoy HCMs.<br />Thus, setting this explicitly to true is unnecessary (but will not cause any harm).<br />When true, Envoy will use the remote address of the connection as the client address.<br />When false, Envoy will use the X-Forwarded-For header to determine the client address.<br />See here for more information: https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/filters/network/http_connection_manager/v3/http_connection_manager.proto#envoy-v3-api-field-extensions-filters-network-http-connection-manager-v3-httpconnectionmanager-use-remote-address |  |  |
| `xffNumTrustedHops` _integer_ | XffNumTrustedHops is the number of additional ingress proxy hops from the right side of the X-Forwarded-For HTTP header to trust when determining the origin client's IP address.<br />See here for more information: https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/filters/network/http_connection_manager/v3/http_connection_manager.proto#envoy-v3-api-field-extensions-filters-network-http-connection-manager-v3-httpconnectionmanager-xff-num-trusted-hops |  | Minimum: 0 <br /> |
| `serverHeaderTransformation` _[ServerHeaderTransformation](#serverheadertransformation)_ | ServerHeaderTransformation determines how the server header is transformed.<br />See here for more information: https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/filters/network/http_connection_manager/v3/http_connection_manager.proto#envoy-v3-api-field-extensions-filters-network-http-connection-manager-v3-httpconnectionmanager-server-header-transformation |  | Enum: [Overwrite AppendIfAbsent PassThrough] <br /> |
| `streamIdleTimeout` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | StreamIdleTimeout is the idle timeout for HTTP streams.<br />See here for more information: https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/filters/network/http_connection_manager/v3/http_connection_manager.proto#envoy-v3-api-field-extensions-filters-network-http-connection-manager-v3-httpconnectionmanager-stream-idle-timeout |  |  |
| `idleTimeout` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | IdleTimeout is the idle timeout for connnections.<br />See here for more information: https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/core/v3/protocol.proto#envoy-v3-api-msg-config-core-v3-httpprotocoloptions |  |  |
| `healthCheck` _[EnvoyHealthCheck](#envoyhealthcheck)_ | HealthCheck configures [Envoy health checks](https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/filters/http/health_check/v3/health_check.proto) |  |  |
| `preserveHttp1HeaderCase` _boolean_ | PreserveHttp1HeaderCase determines whether to preserve the case of HTTP1 request headers.<br />See here for more information: https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_conn_man/header_casing |  |  |
| `acceptHttp10` _boolean_ | AcceptHTTP10 determines whether to accept incoming HTTP/1.0 and HTTP 0.9 requests.<br />See here for more information: https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/core/v3/protocol.proto#config-core-v3-http1protocoloptions |  |  |
| `defaultHostForHttp10` _string_ | DefaultHostForHttp10 specifies a default host for HTTP/1.0 requests. This is highly suggested if acceptHttp10 is true and a no-op if acceptHttp10 is false.<br />See here for more information: https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/core/v3/protocol.proto#config-core-v3-http1protocoloptions |  | MinLength: 1 <br /> |


#### HashPolicy







_Appears in:_
- [LoadBalancerMaglevConfig](#loadbalancermaglevconfig)
- [LoadBalancerRingHashConfig](#loadbalancerringhashconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `header` _[Header](#header)_ | Header specifies a header's value as a component of the hash key. |  |  |
| `cookie` _[Cookie](#cookie)_ | Cookie specifies a given cookie as a component of the hash key. |  |  |
| `sourceIP` _[SourceIP](#sourceip)_ | SourceIP specifies whether to use the request's source IP address as a component of the hash key. |  |  |
| `terminal` _boolean_ | Terminal, if set, and a hash key is available after evaluating this policy, will cause Envoy to skip the subsequent policies and<br />use the key as it is.<br />This is useful for defining "fallback" policies and limiting the time Envoy spends generating hash keys. |  |  |


#### Header

_Underlying type:_ _[struct{Name string "json:\"name\""}](#struct{name-string-"json:\"name\""})_





_Appears in:_
- [HashPolicy](#hashpolicy)



#### HeaderFilter



HeaderFilter filters requests based on headers.
Based on: https://www.envoyproxy.io/docs/envoy/v1.33.0/api-v3/config/accesslog/v3/accesslog.proto#config-accesslog-v3-headerfilter



_Appears in:_
- [FilterType](#filtertype)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `header` _[HTTPHeaderMatch](#httpheadermatch)_ |  |  |  |


#### HeaderModifiers



HeaderModifiers can be used to define the policy to modify request and response headers.



_Appears in:_
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `request` _[HTTPHeaderFilter](#httpheaderfilter)_ | Request modifies request headers. |  |  |
| `response` _[HTTPHeaderFilter](#httpheaderfilter)_ | Response modifies response headers. |  |  |


#### HeaderName

_Underlying type:_ _string_





_Appears in:_
- [HeaderTransformation](#headertransformation)



#### HeaderTransformation







_Appears in:_
- [Transform](#transform)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _[HeaderName](#headername)_ | Name is the name of the header to interact with. |  |  |
| `value` _[InjaTemplate](#injatemplate)_ | Value is the template to apply to generate the output value for the header. |  |  |


#### HeaderValue



Header name/value pair.
Ref: https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/core/v3/base.proto#envoy-v3-api-msg-config-core-v3-headervalue



_Appears in:_
- [AccessLogGrpcService](#accessloggrpcservice)
- [CommonAccessLogGrpcService](#commonaccessloggrpcservice)
- [CommonGrpcService](#commongrpcservice)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `key` _string_ | Header name. |  |  |
| `value` _string_ | Header value. |  |  |


#### HealthCheck



HealthCheck contains the options to configure the health check.
See [Envoy documentation](https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/core/v3/health_check.proto) for more details.



_Appears in:_
- [BackendConfigPolicySpec](#backendconfigpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `timeout` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | Timeout is time to wait for a health check response. If the timeout is reached the<br />health check attempt will be considered a failure. |  |  |
| `interval` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | Interval is the time between health checks. |  |  |
| `unhealthyThreshold` _integer_ | UnhealthyThreshold is the number of consecutive failed health checks that will be considered<br />unhealthy.<br />Note that for HTTP health checks, if a host responds with a code not in ExpectedStatuses or RetriableStatuses,<br />this threshold is ignored and the host is considered immediately unhealthy. |  |  |
| `healthyThreshold` _integer_ | HealthyThreshold is the number of healthy health checks required before a host is marked<br />healthy. Note that during startup, only a single successful health check is<br />required to mark a host healthy. |  |  |
| `http` _[HealthCheckHttp](#healthcheckhttp)_ | Http contains the options to configure the HTTP health check. |  |  |
| `grpc` _[HealthCheckGrpc](#healthcheckgrpc)_ | Grpc contains the options to configure the gRPC health check. |  |  |


#### HealthCheckGrpc







_Appears in:_
- [HealthCheck](#healthcheck)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `serviceName` _string_ | ServiceName is the optional name of the service to check. |  |  |
| `authority` _string_ | Authority is the authority header used to make the gRPC health check request.<br />If unset, the name of the cluster this health check is associated<br />with will be used. |  |  |


#### HealthCheckHttp







_Appears in:_
- [HealthCheck](#healthcheck)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `host` _string_ | Host is the value of the host header in the HTTP health check request. If<br />unset, the name of the cluster this health check is associated<br />with will be used. |  |  |
| `path` _string_ | Path is the HTTP path requested. |  |  |
| `method` _string_ | Method is the HTTP method to use.<br />If unset, GET is used. |  | Enum: [GET HEAD POST PUT DELETE OPTIONS TRACE PATCH] <br /> |


#### Host



Host defines a static backend host.



_Appears in:_
- [LLMProvider](#llmprovider)
- [StaticBackend](#staticbackend)
- [Webhook](#webhook)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `host` _string_ | Host is the host name to use for the backend. |  | MinLength: 1 <br /> |
| `port` _[PortNumber](#portnumber)_ | Port is the port to use for the backend. |  |  |


#### Http1ProtocolOptions



See [Envoy documentation](https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/core/v3/protocol.proto#envoy-v3-api-msg-config-core-v3-http1protocoloptions) for more details.



_Appears in:_
- [BackendConfigPolicySpec](#backendconfigpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `enableTrailers` _boolean_ | Enables trailers for HTTP/1. By default the HTTP/1 codec drops proxied trailers.<br />Note: Trailers must also be enabled at the gateway level in order for this option to take effect |  |  |
| `preserveHttp1HeaderCase` _boolean_ | PreserveHttp1HeaderCase determines whether to preserve the case of HTTP1 response headers.<br />See here for more information: https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_conn_man/header_casing |  |  |
| `overrideStreamErrorOnInvalidHttpMessage` _boolean_ | Allows invalid HTTP messaging. When this option is false, then Envoy will terminate<br />HTTP/1.1 connections upon receiving an invalid HTTP message. However,<br />when this option is true, then Envoy will leave the HTTP/1.1 connection<br />open where possible. |  |  |


#### Http2ProtocolOptions







_Appears in:_
- [BackendConfigPolicySpec](#backendconfigpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `initialStreamWindowSize` _[Quantity](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#quantity-resource-api)_ | InitialStreamWindowSize is the initial window size for the stream.<br />Valid values range from 65535 (2^16 - 1, HTTP/2 default) to 2147483647 (2^31 - 1, HTTP/2 maximum).<br />Defaults to 268435456 (256 * 1024 * 1024).<br />Values can be specified with units like "64Ki". |  |  |
| `initialConnectionWindowSize` _[Quantity](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#quantity-resource-api)_ | InitialConnectionWindowSize is similar to InitialStreamWindowSize, but for the connection level.<br />Same range and default value as InitialStreamWindowSize.<br />Values can be specified with units like "64Ki". |  |  |
| `maxConcurrentStreams` _integer_ | The maximum number of concurrent streams that the connection can have. |  |  |
| `overrideStreamErrorOnInvalidHttpMessage` _boolean_ | Allows invalid HTTP messaging and headers. When disabled (default), then<br />the whole HTTP/2 connection is terminated upon receiving invalid HEADERS frame.<br />When enabled, only the offending stream is terminated. |  |  |


#### Image



A container image. See https://kubernetes.io/docs/concepts/containers/images
for details.



_Appears in:_
- [AgentGateway](#agentgateway)
- [AiExtension](#aiextension)
- [EnvoyContainer](#envoycontainer)
- [IstioContainer](#istiocontainer)
- [SdsContainer](#sdscontainer)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `registry` _string_ | The image registry. |  |  |
| `repository` _string_ | The image repository (name). |  |  |
| `tag` _string_ | The image tag. |  |  |
| `digest` _string_ | The hash digest of the image, e.g. `sha256:12345...` |  |  |
| `pullPolicy` _[PullPolicy](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#pullpolicy-v1-core)_ | The image pull policy for the container. See<br />https://kubernetes.io/docs/concepts/containers/images/#image-pull-policy<br />for details. |  |  |


#### InjaTemplate

_Underlying type:_ _string_





_Appears in:_
- [BodyTransformation](#bodytransformation)
- [HeaderTransformation](#headertransformation)



#### IstioContainer



IstioContainer configures the container running the istio-proxy.



_Appears in:_
- [IstioIntegration](#istiointegration)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `image` _[Image](#image)_ | The envoy container image. See<br />https://kubernetes.io/docs/concepts/containers/images<br />for details. |  |  |
| `securityContext` _[SecurityContext](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#securitycontext-v1-core)_ | The security context for this container. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#securitycontext-v1-core<br />for details. |  |  |
| `resources` _[ResourceRequirements](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#resourcerequirements-v1-core)_ | The compute resources required by this container. See<br />https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/<br />for details. |  |  |
| `logLevel` _string_ | Log level for istio-proxy. Options include "info", "debug", "warning", and "error".<br />Default level is info Default is "warning". |  |  |
| `istioDiscoveryAddress` _string_ | The address of the istio discovery service. Defaults to "istiod.istio-system.svc:15012". |  |  |
| `istioMetaMeshId` _string_ | The mesh id of the istio mesh. Defaults to "cluster.local". |  |  |
| `istioMetaClusterId` _string_ | The cluster id of the istio cluster. Defaults to "Kubernetes". |  |  |


#### IstioIntegration



IstioIntegration configures the Istio integration settings used by a kgateway's data plane (Envoy proxy instance)



_Appears in:_
- [KubernetesProxyConfig](#kubernetesproxyconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `istioProxyContainer` _[IstioContainer](#istiocontainer)_ | Configuration for the container running istio-proxy.<br />Note that if Istio integration is not enabled, the istio container will not be injected<br />into the gateway proxy deployment. |  |  |
| `customSidecars` _[Container](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#container-v1-core) array_ | do not use slice of pointers: https://github.com/kubernetes/code-generator/issues/166<br />Override the default Istio sidecar in gateway-proxy with a custom container. |  |  |




#### KubernetesProxyConfig



KubernetesProxyConfig configures the set of Kubernetes resources that will be provisioned
for a given Gateway.



_Appears in:_
- [GatewayParametersSpec](#gatewayparametersspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `deployment` _[ProxyDeployment](#proxydeployment)_ | Use a Kubernetes deployment as the proxy workload type. Currently, this is the only<br />supported workload type. |  |  |
| `envoyContainer` _[EnvoyContainer](#envoycontainer)_ | Configuration for the container running Envoy.<br />If AgentGateway is enabled, the EnvoyContainer values will be ignored. |  |  |
| `sdsContainer` _[SdsContainer](#sdscontainer)_ | Configuration for the container running the Secret Discovery Service (SDS). |  |  |
| `podTemplate` _[Pod](#pod)_ | Configuration for the pods that will be created. |  |  |
| `service` _[Service](#service)_ | Configuration for the Kubernetes Service that exposes the Envoy proxy over<br />the network. |  |  |
| `serviceAccount` _[ServiceAccount](#serviceaccount)_ | Configuration for the Kubernetes ServiceAccount used by the Envoy pod. |  |  |
| `istio` _[IstioIntegration](#istiointegration)_ | Configuration for the Istio integration. |  |  |
| `stats` _[StatsConfig](#statsconfig)_ | Configuration for the stats server. |  |  |
| `aiExtension` _[AiExtension](#aiextension)_ | Configuration for the AI extension. |  |  |
| `agentGateway` _[AgentGateway](#agentgateway)_ | Configure the AgentGateway integration. If AgentGateway is disabled, the EnvoyContainer values will be used by<br />default to configure the data plane proxy. |  |  |
| `floatingUserId` _boolean_ | Used to unset the `runAsUser` values in security contexts. |  |  |


#### LLMProvider



LLMProvider specifies the target large language model provider that the backend should route requests to.
TODO: Move auth options off of SupportedLLMProvider to BackendConfigPolicy: https://github.com/kgateway-dev/kgateway/issues/11930



_Appears in:_
- [AIBackend](#aibackend)
- [Priority](#priority)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `provider` _[SupportedLLMProvider](#supportedllmprovider)_ | The LLM provider type to configure. |  | MaxProperties: 1 <br />MinProperties: 1 <br /> |
| `hostOverride` _[Host](#host)_ | Send requests to a custom host and port, such as to proxy the request,<br />or to use a different backend that is API-compliant with the Backend version. |  |  |
| `pathOverride` _[PathOverride](#pathoverride)_ | TODO: Consolidate all Override options into ProviderOverride.<br />Overrides the default API path for the LLM provider.<br />Allows routing requests to a custom API endpoint path. |  | MinProperties: 1 <br /> |
| `authHeaderOverride` _[AuthHeaderOverride](#authheaderoverride)_ | Customizes the Authorization header sent to the LLM provider.<br />Allows changing the header name and/or the prefix (e.g., "Bearer").<br />Note: Not all LLM providers use the Authorization header and prefix.<br />For example, OpenAI uses header: "Authorization" and prefix: "Bearer" But Azure OpenAI uses header: "api-key"<br />and no Bearer. |  |  |


#### LoadBalancer







_Appears in:_
- [BackendConfigPolicySpec](#backendconfigpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `healthyPanicThreshold` _integer_ | HealthyPanicThreshold configures envoy's panic threshold percentage between 0-100. Once the number of non-healthy hosts<br />reaches this percentage, envoy disregards health information.<br />See [Envoy documentation](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/panic_threshold.html). |  | Maximum: 100 <br />Minimum: 0 <br /> |
| `updateMergeWindow` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | This allows batch updates of endpoints health/weight/metadata that happen during a time window.<br />this help lower cpu usage when endpoint change rate is high. defaults to 1 second.<br />Set to 0 to disable and have changes applied immediately. |  |  |
| `leastRequest` _[LoadBalancerLeastRequestConfig](#loadbalancerleastrequestconfig)_ | LeastRequest configures the least request load balancer type. |  |  |
| `roundRobin` _[LoadBalancerRoundRobinConfig](#loadbalancerroundrobinconfig)_ | RoundRobin configures the round robin load balancer type. |  |  |
| `ringHash` _[LoadBalancerRingHashConfig](#loadbalancerringhashconfig)_ | RingHash configures the ring hash load balancer type. |  |  |
| `maglev` _[LoadBalancerMaglevConfig](#loadbalancermaglevconfig)_ | Maglev configures the maglev load balancer type. |  |  |
| `random` _[LoadBalancerRandomConfig](#loadbalancerrandomconfig)_ | Random configures the random load balancer type. |  |  |
| `localityType` _[LocalityType](#localitytype)_ | LocalityType specifies the locality config type to use.<br />See https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/load_balancing_policies/common/v3/common.proto#envoy-v3-api-msg-extensions-load-balancing-policies-common-v3-localitylbconfig |  | Enum: [WeightedLb] <br /> |
| `closeConnectionsOnHostSetChange` _boolean_ | If set to true, the load balancer will drain connections when the host set changes.<br /><br />Ring Hash or Maglev can be used to ensure that clients with the same key<br />are routed to the same upstream host.<br />Distruptions can cause new connections with the same key as existing connections<br />to be routed to different hosts.<br />Enabling this feature will cause the load balancer to drain existing connections<br />when the host set changes, ensuring that new connections with the same key are<br />consistently routed to the same host.<br />Connections are not immediately closed, but are allowed to drain<br />before being closed. |  |  |


#### LoadBalancerLeastRequestConfig



LoadBalancerLeastRequestConfig configures the least request load balancer type.



_Appears in:_
- [LoadBalancer](#loadbalancer)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `choiceCount` _integer_ | How many choices to take into account.<br />Defaults to 2. |  |  |
| `slowStart` _[SlowStart](#slowstart)_ | SlowStart configures the slow start configuration for the load balancer. |  |  |


#### LoadBalancerMaglevConfig







_Appears in:_
- [LoadBalancer](#loadbalancer)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `useHostnameForHashing` _boolean_ | UseHostnameForHashing specifies whether to use the hostname instead of the resolved IP address for hashing.<br />Defaults to false. |  |  |
| `hashPolicies` _[HashPolicy](#hashpolicy) array_ | HashPolicies specifies the hash policies for hashing load balancers (RingHash, Maglev). |  | MaxItems: 16 <br />MinItems: 1 <br /> |


#### LoadBalancerRandomConfig







_Appears in:_
- [LoadBalancer](#loadbalancer)



#### LoadBalancerRingHashConfig



LoadBalancerRingHashConfig configures the ring hash load balancer type.



_Appears in:_
- [LoadBalancer](#loadbalancer)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `minimumRingSize` _integer_ | MinimumRingSize is the minimum size of the ring. |  |  |
| `maximumRingSize` _integer_ | MaximumRingSize is the maximum size of the ring. |  |  |
| `useHostnameForHashing` _boolean_ | UseHostnameForHashing specifies whether to use the hostname instead of the resolved IP address for hashing.<br />Defaults to false. |  |  |
| `hashPolicies` _[HashPolicy](#hashpolicy) array_ | HashPolicies specifies the hash policies for hashing load balancers (RingHash, Maglev). |  | MaxItems: 16 <br />MinItems: 1 <br /> |


#### LoadBalancerRoundRobinConfig



LoadBalancerRoundRobinConfig configures the round robin load balancer type.



_Appears in:_
- [LoadBalancer](#loadbalancer)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `slowStart` _[SlowStart](#slowstart)_ | SlowStart configures the slow start configuration for the load balancer. |  |  |


#### LocalPolicyTargetReference



Select the object to attach the policy by Group, Kind, and Name.
The object must be in the same namespace as the policy.
You can target only one object at a time.



_Appears in:_
- [BackendConfigPolicySpec](#backendconfigpolicyspec)
- [HTTPListenerPolicySpec](#httplistenerpolicyspec)
- [LocalPolicyTargetReferenceWithSectionName](#localpolicytargetreferencewithsectionname)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `group` _[Group](#group)_ | The API group of the target resource.<br />For Kubernetes Gateway API resources, the group is `gateway.networking.k8s.io`. |  |  |
| `kind` _[Kind](#kind)_ | The API kind of the target resource,<br />such as Gateway or HTTPRoute. |  |  |
| `name` _[ObjectName](#objectname)_ | The name of the target resource. |  |  |


#### LocalPolicyTargetReferenceWithSectionName



Select the object to attach the policy by Group, Kind, Name and SectionName.
The object must be in the same namespace as the policy.
You can target only one object at a time.



_Appears in:_
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `group` _[Group](#group)_ | The API group of the target resource.<br />For Kubernetes Gateway API resources, the group is `gateway.networking.k8s.io`. |  |  |
| `kind` _[Kind](#kind)_ | The API kind of the target resource,<br />such as Gateway or HTTPRoute. |  |  |
| `name` _[ObjectName](#objectname)_ | The name of the target resource. |  |  |
| `sectionName` _[SectionName](#sectionname)_ | The section name of the target resource. |  | MaxLength: 253 <br />MinLength: 1 <br />Pattern: `^[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*$` <br /> |


#### LocalPolicyTargetSelector



LocalPolicyTargetSelector selects the object to attach the policy by Group, Kind, and MatchLabels.
The object must be in the same namespace as the policy and match the
specified labels.
Do not use targetSelectors when reconciliation times are critical, especially if you
have a large number of policies that target the same resource.
Instead, use targetRefs to attach the policy.



_Appears in:_
- [BackendConfigPolicySpec](#backendconfigpolicyspec)
- [HTTPListenerPolicySpec](#httplistenerpolicyspec)
- [LocalPolicyTargetSelectorWithSectionName](#localpolicytargetselectorwithsectionname)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `group` _[Group](#group)_ | The API group of the target resource.<br />For Kubernetes Gateway API resources, the group is `gateway.networking.k8s.io`. |  |  |
| `kind` _[Kind](#kind)_ | The API kind of the target resource,<br />such as Gateway or HTTPRoute. |  |  |
| `matchLabels` _object (keys:string, values:string)_ | Label selector to select the target resource. |  |  |


#### LocalPolicyTargetSelectorWithSectionName



LocalPolicyTargetSelectorWithSectionName the object to attach the policy by Group, Kind, MatchLabels, and optionally SectionName.
The object must be in the same namespace as the policy and match the
specified labels.
Do not use targetSelectors when reconciliation times are critical, especially if you
have a large number of policies that target the same resource.
Instead, use targetRefs to attach the policy.



_Appears in:_
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `group` _[Group](#group)_ | The API group of the target resource.<br />For Kubernetes Gateway API resources, the group is `gateway.networking.k8s.io`. |  |  |
| `kind` _[Kind](#kind)_ | The API kind of the target resource,<br />such as Gateway or HTTPRoute. |  |  |
| `matchLabels` _object (keys:string, values:string)_ | Label selector to select the target resource. |  |  |
| `sectionName` _[SectionName](#sectionname)_ | The section name of the target resource. |  | MaxLength: 253 <br />MinLength: 1 <br />Pattern: `^[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*$` <br /> |


#### LocalRateLimitPolicy



LocalRateLimitPolicy represents a policy for local rate limiting.
It defines the configuration for rate limiting using a token bucket mechanism.



_Appears in:_
- [RateLimit](#ratelimit)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `tokenBucket` _[TokenBucket](#tokenbucket)_ | TokenBucket represents the configuration for a token bucket local rate-limiting mechanism.<br />It defines the parameters for controlling the rate at which requests are allowed. |  |  |


#### LocalityType

_Underlying type:_ _string_





_Appears in:_
- [LoadBalancer](#loadbalancer)

| Field | Description |
| --- | --- |
| `WeightedLb` | https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/locality_weight#locality-weighted-load-balancing<br />Locality weighted load balancing enables weighting assignments across different zones and geographical locations by using explicit weights.<br />This field is required to enable locality weighted load balancing.<br /> |


#### MCP



MCP configures mcp backends



_Appears in:_
- [BackendSpec](#backendspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `targets` _[McpTargetSelector](#mcptargetselector) array_ | Targets is a list of MCP targets to use for this backend.<br />Policies targeting MCP targets must use targetRefs[].sectionName<br />to select the target by name. |  | MaxItems: 32 <br />MinItems: 1 <br /> |


#### MCPProtocol

_Underlying type:_ _string_

MCPProtocol defines the protocol to use for the MCP target



_Appears in:_
- [McpTarget](#mcptarget)

| Field | Description |
| --- | --- |
| `StreamableHTTP` | MCPProtocolStreamableHTTP specifies Streamable HTTP must be used as the protocol<br /> |
| `SSE` | MCPProtocolSSE specifies Server-Sent Events (SSE) must be used as the protocol<br /> |


#### McpSelector



McpSelector defines the selector logic to search for MCP targets.



_Appears in:_
- [McpTargetSelector](#mcptargetselector)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `namespace` _[LabelSelector](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#labelselector-v1-meta)_ | Namespace is the label selector in which namespace the MCP targets<br />are searched for. |  |  |
| `service` _[LabelSelector](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#labelselector-v1-meta)_ | Service is the label selector in which services the MCP targets<br />are searched for. |  |  |


#### McpTarget



McpTarget defines a single MCP target configuration.



_Appears in:_
- [McpTargetSelector](#mcptargetselector)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `host` _string_ | Host is the hostname or IP address of the MCP target. |  | MinLength: 1 <br /> |
| `port` _integer_ | Port is the port number of the MCP target. |  | Maximum: 65535 <br />Minimum: 1 <br /> |
| `path` _string_ | Path is the URL path of the MCP target endpoint.<br />Defaults to "/sse" for SSE protocol or "/mcp" for StreamableHTTP protocol if not specified. |  |  |
| `protocol` _[MCPProtocol](#mcpprotocol)_ | Protocol is the protocol to use for the connection to the MCP target. |  | Enum: [StreamableHTTP SSE] <br /> |


#### McpTargetSelector



McpTargetSelector defines the MCP target to use for this backend.



_Appears in:_
- [MCP](#mcp)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ | Name of the MCP target. |  |  |
| `selector` _[McpSelector](#mcpselector)_ | Selector is the selector to use to select the MCP targets.<br />Note: Policies must target the resource selected by the target and<br />not the name of the selector-based target on the Backend resource. |  |  |
| `static` _[McpTarget](#mcptarget)_ | Static is the static MCP target to use.<br />Policies can target static backends by targeting the Backend resource<br />and using sectionName to target the specific static target by name. |  |  |


#### Message



An entry for a message to prepend or append to each prompt.



_Appears in:_
- [AIPromptEnrichment](#aipromptenrichment)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `role` _string_ | Role of the message. The available roles depend on the backend<br />LLM provider model, such as `SYSTEM` or `USER` in the OpenAI API. |  |  |
| `content` _string_ | String content of the message. |  |  |


#### MetadataKey



MetadataKey provides a way to retrieve values from Metadata using a key and a path.



_Appears in:_
- [CustomAttributeMetadata](#customattributemetadata)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `key` _string_ | The key name of the Metadata from which to retrieve the Struct |  |  |
| `path` _[MetadataPathSegment](#metadatapathsegment) array_ | The path used to retrieve a specific Value from the Struct. This can be either a prefix or a full path,<br />depending on the use case |  |  |


#### MetadataKind

_Underlying type:_ _string_

Describes different types of metadata sources.
Ref: https://www.envoyproxy.io/docs/envoy/latest/api-v3/type/metadata/v3/metadata.proto#envoy-v3-api-msg-type-metadata-v3-metadatakind-request

_Validation:_
- Enum: [Request Route Cluster Host]

_Appears in:_
- [CustomAttributeMetadata](#customattributemetadata)

| Field | Description |
| --- | --- |
| `Request` | Request kind of metadata.<br /> |
| `Route` | Route kind of metadata.<br /> |
| `Cluster` | Cluster kind of metadata.<br /> |
| `Host` | Host kind of metadata.<br /> |


#### MetadataPathSegment

_Underlying type:_ _[struct{Key string "json:\"key\""}](#struct{key-string-"json:\"key\""})_

Specifies a segment in a path for retrieving values from Metadata.



_Appears in:_
- [MetadataKey](#metadatakey)



#### Moderation



Moderation configures an external moderation model endpoint. This endpoint evaluates
request prompt data against predefined content rules to determine if the content
adheres to those rules.


Any requests routed through the AI Gateway are processed by the specified
moderation model. If the model identifies the content as harmful based on its rules,
the request is automatically rejected.


You can configure a moderation endpoint either as a standalone prompt guard setting
or alongside other request and response guard settings.



_Appears in:_
- [PromptguardRequest](#promptguardrequest)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `openAIModeration` _[OpenAIConfig](#openaiconfig)_ | Pass prompt data through an external moderation model endpoint,<br />which compares the request prompt input to predefined content rules.<br />Configure an OpenAI moderation endpoint. |  |  |


#### MultiPoolConfig



MultiPoolConfig configures the backends for multiple hosts or models from the same provider in one Backend resource.
This method can be useful for creating one logical endpoint that is backed
by multiple hosts or models.


In the `priorities` section, the order of `pool` entries defines the priority of the backend endpoints.
The `pool` entries can either define a list of backends or a single backend.
Note: Only two levels of nesting are permitted. Any nested entries after the second level are ignored.


```yaml
multi:
  priorities:
  - pool:
    - azureOpenai:
        deploymentName: gpt-4o-mini
        apiVersion: 2024-02-15-preview
        endpoint: ai-gateway.openai.azure.com
        authToken:
          secretRef:
            name: azure-secret
            namespace: kgateway-system
  - pool:
    - azureOpenai:
        deploymentName: gpt-4o-mini-2
        apiVersion: 2024-02-15-preview
        endpoint: ai-gateway-2.openai.azure.com
        authToken:
          secretRef:
            name: azure-secret-2
            namespace: kgateway-system
```



_Appears in:_
- [AIBackend](#aibackend)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `priorities` _[Priority](#priority) array_ | The priority list of backend pools. Each entry represents a set of LLM provider backends.<br />The order defines the priority of the backend endpoints. |  | MaxItems: 20 <br />MinItems: 1 <br /> |


#### NamespacedObjectReference



Select the object by Name and Namespace.
You can target only one object at a time.



_Appears in:_
- [ExtAuthPolicy](#extauthpolicy)
- [ExtProcPolicy](#extprocpolicy)
- [RateLimitPolicy](#ratelimitpolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _[ObjectName](#objectname)_ | The name of the target resource. |  |  |
| `namespace` _[Namespace](#namespace)_ | The namespace of the target resource.<br />If not set, defaults to the namespace of the parent object. |  | MaxLength: 63 <br />MinLength: 1 <br />Pattern: `^[a-z0-9]([-a-z0-9]*[a-z0-9])?$` <br /> |


#### OTLPTracesProtocolType

_Underlying type:_ _string_

OTLPTracesProtocolType defines the supported protocols for OTLP exporter.



_Appears in:_
- [AiExtensionTrace](#aiextensiontrace)

| Field | Description |
| --- | --- |
| `grpc` | OTLPTracesProtocolTypeGrpc specifies OTLP over gRPC protocol.<br />This is typically the most efficient protocol for OpenTelemetry data transfer.<br /> |
| `http/protobuf` | OTLPTracesProtocolTypeProtobuf specifies OTLP over HTTP with Protobuf serialization.<br />Data is sent via HTTP POST requests with Protobuf message bodies.<br /> |
| `http/json` | OTLPTracesProtocolTypeJson specifies OTLP over HTTP with JSON serialization.<br />Data is sent via HTTP POST requests with JSON message bodies.<br /> |




#### OTelTracesSampler



OTelTracesSampler defines the configuration for an OpenTelemetry trace sampler.
It combines the sampler type with any required arguments for that type.



_Appears in:_
- [AiExtensionTrace](#aiextensiontrace)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `type` _[OTelTracesSamplerType](#oteltracessamplertype)_ | SamplerType specifies the type of sampler to use (default value: "parentbased_always_on").<br />Refer to OTelTracesSamplerType for available options.<br />https://opentelemetry.io/docs/languages/sdk-configuration/general/#otel_traces_sampler |  | Enum: [alwaysOn alwaysOff traceidratio parentbasedAlwaysOn parentbasedAlwaysOff parentbasedTraceidratio] <br /> |
| `arg` _string_ | SamplerArg provides an argument for the chosen sampler type.<br />For "traceidratio" or "parentbased_traceidratio" samplers: Sampling probability, a number in the [0..1] range,<br />e.g. 0.25. Default is 1.0 if unset.<br />https://opentelemetry.io/docs/languages/sdk-configuration/general/#otel_traces_sampler_arg |  | Pattern: `^0(\.\d+)?\|1(\.0+)?$` <br /> |






#### OpenAIConfig



OpenAIConfig settings for the [OpenAI](https://platform.openai.com/docs/api-reference/streaming) LLM provider.



_Appears in:_
- [Moderation](#moderation)
- [SupportedLLMProvider](#supportedllmprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `authToken` _[SingleAuthToken](#singleauthtoken)_ | The authorization token that the AI gateway uses to access the OpenAI API.<br />This token is automatically sent in the `Authorization` header of the<br />request and prefixed with `Bearer`. |  |  |
| `model` _string_ | Optional: Override the model name, such as `gpt-4o-mini`.<br />If unset, the model name is taken from the request.<br />This setting can be useful when setting up model failover within the same LLM provider. |  |  |


#### OpenTelemetryAccessLogService



OpenTelemetryAccessLogService represents the OTel configuration for access logs.
Ref: https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/access_loggers/open_telemetry/v3/logs_service.proto



_Appears in:_
- [AccessLog](#accesslog)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `grpcService` _[CommonAccessLogGrpcService](#commonaccessloggrpcservice)_ | Send access logs to gRPC service |  |  |
| `body` _string_ | OpenTelemetry LogResource fields, following Envoy access logging formatting. |  |  |
| `disableBuiltinLabels` _boolean_ | If specified, Envoy will not generate built-in resource labels like log_name, zone_name, cluster_name, node_name. |  |  |


#### OpenTelemetryTracingConfig



OpenTelemetryTracingConfig represents the top-level Envoy's OpenTelemetry tracer.
See here for more information: https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/trace/v3/opentelemetry.proto.html



_Appears in:_
- [TracingProvider](#tracingprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `grpcService` _[CommonGrpcService](#commongrpcservice)_ | Send traces to the gRPC service |  |  |
| `serviceName` _string_ | The name for the service. This will be populated in the ResourceSpan Resource attributes<br />Defaults to the envoy cluster name. Ie: `<gateway-name>.<gateway-namespace>` |  |  |
| `resourceDetectors` _[ResourceDetector](#resourcedetector) array_ | An ordered list of resource detectors. Currently supported values are `EnvironmentResourceDetector` |  | MaxProperties: 1 <br />MinProperties: 1 <br /> |
| `sampler` _[Sampler](#sampler)_ | Specifies the sampler to be used by the OpenTelemetry tracer. This field can be left empty. In this case, the default Envoy sampling decision is used.<br />Currently supported values are `AlwaysOn` |  | MaxProperties: 1 <br />MinProperties: 1 <br /> |


#### OutlierDetection



OutlierDetection contains the options to configure passive health checks.
See [Envoy documentation](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/outlier#outlier-detection) for more details.



_Appears in:_
- [BackendConfigPolicySpec](#backendconfigpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `consecutive5xx` _integer_ | The number of consecutive server-side error responses (for HTTP traffic,<br />5xx responses; for TCP traffic, connection failures; etc.) before an<br />ejection occurs. Defaults to 5. If this is zero, consecutive 5xx passive<br />health checks will be disabled. In the future, other types of passive<br />health checking might be added, but none will be enabled by default. | 5 |  |
| `interval` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | The time interval between ejection analysis sweeps. This can result in<br />both new ejections as well as hosts being returned to service. Defaults<br />to 10s. | 10s |  |
| `baseEjectionTime` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | The base time that a host is ejected for. The real time is equal to the<br />base time multiplied by the number of times the host has been ejected.<br />Defaults to 30s. | 30s |  |
| `maxEjectionPercent` _integer_ | The maximum % of an upstream cluster that can be ejected due to outlier<br />detection. Defaults to 10%. | 10 | Maximum: 100 <br />Minimum: 0 <br /> |


#### Parameters







_Appears in:_
- [TLS](#tls)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `tlsMinVersion` _[TLSVersion](#tlsversion)_ | Minimum TLS version. |  | Enum: [AUTO 1.0 1.1 1.2 1.3] <br /> |
| `tlsMaxVersion` _[TLSVersion](#tlsversion)_ | Maximum TLS version. |  | Enum: [AUTO 1.0 1.1 1.2 1.3] <br /> |
| `cipherSuites` _string array_ |  |  |  |
| `ecdhCurves` _string array_ |  |  |  |


#### PathOverride



PathOverride configures the AI gateway to use a custom path for LLM provider chat-completion API requests.
It allows overriding the default API path with a custom one.
This is useful when you need to route requests to a different API endpoint while maintaining
compatibility with the original provider's API structure.

_Validation:_
- MinProperties: 1

_Appears in:_
- [LLMProvider](#llmprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `fullPath` _string_ | FullPath specifies the custom API path to use for the LLM provider requests.<br />This path will replace the default API path for the provider. |  |  |


#### Pod



Configuration for a Kubernetes Pod template.



_Appears in:_
- [KubernetesProxyConfig](#kubernetesproxyconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `extraLabels` _object (keys:string, values:string)_ | Additional labels to add to the Pod object metadata. |  |  |
| `extraAnnotations` _object (keys:string, values:string)_ | Additional annotations to add to the Pod object metadata. |  |  |
| `securityContext` _[PodSecurityContext](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#podsecuritycontext-v1-core)_ | The pod security context. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#podsecuritycontext-v1-core<br />for details. |  |  |
| `imagePullSecrets` _[LocalObjectReference](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#localobjectreference-v1-core) array_ | An optional list of references to secrets in the same namespace to use for<br />pulling any of the images used by this Pod spec. See<br />https://kubernetes.io/docs/concepts/containers/images/#specifying-imagepullsecrets-on-a-pod<br />for details. |  |  |
| `nodeSelector` _object (keys:string, values:string)_ | A selector which must be true for the pod to fit on a node. See<br />https://kubernetes.io/docs/concepts/configuration/assign-pod-node/ for<br />details. |  |  |
| `affinity` _[Affinity](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#affinity-v1-core)_ | If specified, the pod's scheduling constraints. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#affinity-v1-core<br />for details. |  |  |
| `tolerations` _[Toleration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#toleration-v1-core) array_ | do not use slice of pointers: https://github.com/kubernetes/code-generator/issues/166<br />If specified, the pod's tolerations. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#toleration-v1-core<br />for details. |  |  |
| `gracefulShutdown` _[GracefulShutdownSpec](#gracefulshutdownspec)_ | If specified, the pod's graceful shutdown spec. |  |  |
| `terminationGracePeriodSeconds` _integer_ | If specified, the pod's termination grace period in seconds. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#pod-v1-core<br />for details |  |  |
| `readinessProbe` _[Probe](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#probe-v1-core)_ | If specified, the pod's readiness probe. Periodic probe of container service readiness.<br />Container will be removed from service endpoints if the probe fails. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#probe-v1-core<br />for details. |  |  |
| `livenessProbe` _[Probe](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#probe-v1-core)_ | If specified, the pod's liveness probe. Periodic probe of container service readiness.<br />Container will be restarted if the probe fails. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#probe-v1-core<br />for details. |  |  |
| `topologySpreadConstraints` _[TopologySpreadConstraint](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#topologyspreadconstraint-v1-core) array_ | If specified, the pod's topology spread constraints. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#topologyspreadconstraint-v1-core<br />for details. |  |  |


#### PolicyAncestorStatus







_Appears in:_
- [PolicyStatus](#policystatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `ancestorRef` _[ParentReference](#parentreference)_ | AncestorRef corresponds with a ParentRef in the spec that this<br />PolicyAncestorStatus struct describes the status of. |  |  |
| `controllerName` _string_ | ControllerName is a domain/path string that indicates the name of the<br />controller that wrote this status. This corresponds with the<br />controllerName field on GatewayClass.<br /><br />Example: "example.net/gateway-controller".<br /><br />The format of this field is DOMAIN "/" PATH, where DOMAIN and PATH are<br />valid Kubernetes names<br />(https://kubernetes.io/docs/concepts/overview/working-with-objects/names/#names).<br /><br />Controllers MUST populate this field when writing status. Controllers should ensure that<br />entries to status populated with their ControllerName are cleaned up when they are no<br />longer necessary. |  |  |
| `conditions` _[Condition](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#condition-v1-meta) array_ | Conditions describes the status of the Policy with respect to the given Ancestor. |  | MaxItems: 8 <br />MinItems: 1 <br /> |






#### PolicyDisable



PolicyDisable is used to disable a policy.



_Appears in:_
- [Buffer](#buffer)
- [CorsPolicy](#corspolicy)
- [ExtAuthPolicy](#extauthpolicy)
- [ExtProcPolicy](#extprocpolicy)





#### Port







_Appears in:_
- [Service](#service)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `port` _integer_ | The port number to match on the Gateway |  |  |
| `nodePort` _integer_ | The NodePort to be used for the service. If not specified, a random port<br />will be assigned by the Kubernetes API server. |  |  |


#### Priority



Priority configures the priority of the backend endpoints.



_Appears in:_
- [MultiPoolConfig](#multipoolconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `pool` _[LLMProvider](#llmprovider) array_ | A list of LLM provider backends within a single endpoint pool entry. |  | MaxItems: 20 <br />MinItems: 1 <br /> |


#### ProcessingMode



ProcessingMode defines how the filter should interact with the request/response streams



_Appears in:_
- [ExtProcPolicy](#extprocpolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `requestHeaderMode` _string_ | RequestHeaderMode determines how to handle the request headers | SEND | Enum: [DEFAULT SEND SKIP] <br /> |
| `responseHeaderMode` _string_ | ResponseHeaderMode determines how to handle the response headers | SEND | Enum: [DEFAULT SEND SKIP] <br /> |
| `requestBodyMode` _string_ | RequestBodyMode determines how to handle the request body | NONE | Enum: [NONE STREAMED BUFFERED BUFFERED_PARTIAL FULL_DUPLEX_STREAMED] <br /> |
| `responseBodyMode` _string_ | ResponseBodyMode determines how to handle the response body | NONE | Enum: [NONE STREAMED BUFFERED BUFFERED_PARTIAL FULL_DUPLEX_STREAMED] <br /> |
| `requestTrailerMode` _string_ | RequestTrailerMode determines how to handle the request trailers | SKIP | Enum: [DEFAULT SEND SKIP] <br /> |
| `responseTrailerMode` _string_ | ResponseTrailerMode determines how to handle the response trailers | SKIP | Enum: [DEFAULT SEND SKIP] <br /> |


#### PromptguardRequest



PromptguardRequest defines the prompt guards to apply to requests sent by the client.
Multiple prompt guard configurations can be set, and they will be executed in the following order:
webhook → regex → moderation for requests, where each step can reject the request and stop further processing.



_Appears in:_
- [AIPromptGuard](#aipromptguard)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `customResponse` _[CustomResponse](#customresponse)_ | A custom response message to return to the client. If not specified, defaults to<br />"The request was rejected due to inappropriate content". |  |  |
| `regex` _[Regex](#regex)_ | Regular expression (regex) matching for prompt guards and data masking. |  |  |
| `webhook` _[Webhook](#webhook)_ | Configure a webhook to forward requests to for prompt guarding. |  |  |
| `moderation` _[Moderation](#moderation)_ | Pass prompt data through an external moderation model endpoint,<br />which compares the request prompt input to predefined content rules. |  |  |


#### PromptguardResponse



PromptguardResponse configures the response that the prompt guard applies to responses returned by the LLM provider.
Both webhook and regex can be set, they will be executed in the following order: webhook → regex, where each step
can reject the request and stop further processing.
Note: This is not yet supported for agentgateway.



_Appears in:_
- [AIPromptGuard](#aipromptguard)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `regex` _[Regex](#regex)_ | Regular expression (regex) matching for prompt guards and data masking. |  |  |
| `webhook` _[Webhook](#webhook)_ | Configure a webhook to forward responses to for prompt guarding. |  |  |


#### ProxyDeployment



ProxyDeployment configures the Proxy deployment in Kubernetes.



_Appears in:_
- [KubernetesProxyConfig](#kubernetesproxyconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `replicas` _integer_ | The number of desired pods. Defaults to 1. |  |  |
| `omitReplicas` _boolean_ | If true, replicas will not be set in the deployment (allowing HPA to control scaling) |  |  |


#### Publisher

_Underlying type:_ _string_

Publisher configures the type of publisher model to use for VertexAI. Currently, only Google is supported.



_Appears in:_
- [VertexAIConfig](#vertexaiconfig)

| Field | Description |
| --- | --- |
| `GOOGLE` |  |


#### RBAC



RBAC defines the configuration for role-based access control.



_Appears in:_
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `policy` _[RBACPolicy](#rbacpolicy)_ | Policy specifies the RBAC rule to evaluate.<br />A policy matches only **all** the conditions evaluates to true. |  |  |
| `action` _[AuthorizationPolicyAction](#authorizationpolicyaction)_ | Action defines whether the rule allows or denies the request if matched.<br />If unspecified, the default is "Allow". | Allow | Enum: [Allow Deny] <br /> |


#### RBACPolicy



RBACPolicy defines a single RBAC rule.



_Appears in:_
- [RBAC](#rbac)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `matchExpressions` _string array_ | MatchExpressions defines a set of conditions that must be satisfied for the rule to match.<br />These expression should be in the form of a Common Expression Language (CEL) expression.<br />See: https://www.envoyproxy.io/docs/envoy/latest/xds/type/matcher/v3/cel.proto |  | MinItems: 1 <br /> |


#### RateLimit



RateLimit defines a rate limiting policy.



_Appears in:_
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `local` _[LocalRateLimitPolicy](#localratelimitpolicy)_ | Local defines a local rate limiting policy. |  |  |
| `global` _[RateLimitPolicy](#ratelimitpolicy)_ | Global defines a global rate limiting policy using an external service. |  |  |


#### RateLimitDescriptor



RateLimitDescriptor defines a descriptor for rate limiting.
A descriptor is a group of entries that form a single rate limit rule.



_Appears in:_
- [RateLimitPolicy](#ratelimitpolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `entries` _[RateLimitDescriptorEntry](#ratelimitdescriptorentry) array_ | Entries are the individual components that make up this descriptor.<br />When translated to Envoy, these entries combine to form a single descriptor. |  | MinItems: 1 <br /> |


#### RateLimitDescriptorEntry



RateLimitDescriptorEntry defines a single entry in a rate limit descriptor.
Only one entry type may be specified.



_Appears in:_
- [RateLimitDescriptor](#ratelimitdescriptor)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `type` _[RateLimitDescriptorEntryType](#ratelimitdescriptorentrytype)_ | Type specifies what kind of rate limit descriptor entry this is. |  | Enum: [Generic Header RemoteAddress Path] <br /> |
| `generic` _[RateLimitDescriptorEntryGeneric](#ratelimitdescriptorentrygeneric)_ | Generic contains the configuration for a generic key-value descriptor entry.<br />This field must be specified when Type is Generic. |  |  |
| `header` _string_ | Header specifies a request header to extract the descriptor value from.<br />This field must be specified when Type is Header. |  | MinLength: 1 <br /> |




#### RateLimitDescriptorEntryType

_Underlying type:_ _string_

RateLimitDescriptorEntryType defines the type of a rate limit descriptor entry.

_Validation:_
- Enum: [Generic Header RemoteAddress Path]

_Appears in:_
- [RateLimitDescriptorEntry](#ratelimitdescriptorentry)

| Field | Description |
| --- | --- |
| `Generic` | RateLimitDescriptorEntryTypeGeneric represents a generic key-value descriptor entry.<br /> |
| `Header` | RateLimitDescriptorEntryTypeHeader represents a descriptor entry that extracts its value from a request header.<br /> |
| `RemoteAddress` | RateLimitDescriptorEntryTypeRemoteAddress represents a descriptor entry that uses the client's IP address as its value.<br /> |
| `Path` | RateLimitDescriptorEntryTypePath represents a descriptor entry that uses the request path as its value.<br /> |


#### RateLimitPolicy



RateLimitPolicy defines a global rate limiting policy using an external service.



_Appears in:_
- [RateLimit](#ratelimit)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `descriptors` _[RateLimitDescriptor](#ratelimitdescriptor) array_ | Descriptors define the dimensions for rate limiting.<br />These values are passed to the rate limit service which applies configured limits based on them.<br />Each descriptor represents a single rate limit rule with one or more entries. |  | MinItems: 1 <br /> |
| `extensionRef` _[NamespacedObjectReference](#namespacedobjectreference)_ | ExtensionRef references a GatewayExtension that provides the global rate limit service. |  |  |


#### RateLimitProvider



RateLimitProvider defines the configuration for a RateLimit service provider.



_Appears in:_
- [GatewayExtensionSpec](#gatewayextensionspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `grpcService` _[ExtGrpcService](#extgrpcservice)_ | GrpcService is the GRPC service that will handle the rate limiting. |  |  |
| `domain` _string_ | Domain identifies a rate limiting configuration for the rate limit service.<br />All rate limit requests must specify a domain, which enables the configuration<br />to be per application without fear of overlap (e.g., "api", "web", "admin"). |  |  |
| `failOpen` _boolean_ | FailOpen determines if requests are limited when the rate limit service is unavailable.<br />When true, requests are not limited if the rate limit service is unavailable. | true |  |
| `timeout` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | Timeout for requests to the rate limit service. | 100ms |  |


#### Regex



Regex configures the regular expression (regex) matching for prompt guards and data masking.



_Appears in:_
- [PromptguardRequest](#promptguardrequest)
- [PromptguardResponse](#promptguardresponse)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `matches` _[RegexMatch](#regexmatch) array_ | A list of regex patterns to match against the request or response.<br />Matches and built-ins are additive. |  |  |
| `builtins` _[BuiltIn](#builtin) array_ | A list of built-in regex patterns to match against the request or response.<br />Matches and built-ins are additive. |  | Enum: [SSN CREDIT_CARD PHONE_NUMBER EMAIL] <br /> |
| `action` _[Action](#action)_ | The action to take if a regex pattern is matched in a request or response.<br />This setting applies only to request matches. PromptguardResponse matches are always masked by default.<br />Defaults to `MASK`. | MASK |  |


#### RegexMatch



RegexMatch configures the regular expression (regex) matching for prompt guards and data masking.



_Appears in:_
- [Regex](#regex)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `pattern` _string_ | The regex pattern to match against the request or response. |  |  |
| `name` _string_ | An optional name for this match, which can be used for debugging purposes. |  |  |


#### ResourceDetector



ResourceDetector defines the list of supported ResourceDetectors

_Validation:_
- MaxProperties: 1
- MinProperties: 1

_Appears in:_
- [OpenTelemetryTracingConfig](#opentelemetrytracingconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `environmentResourceDetector` _[EnvironmentResourceDetectorConfig](#environmentresourcedetectorconfig)_ |  |  |  |


#### ResponseFlagFilter



ResponseFlagFilter filters based on response flags.
Based on: https://www.envoyproxy.io/docs/envoy/v1.33.0/api-v3/config/accesslog/v3/accesslog.proto#config-accesslog-v3-responseflagfilter



_Appears in:_
- [FilterType](#filtertype)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `flags` _string array_ |  |  | MinItems: 1 <br /> |


#### Retry



Retry defines the retry policy



_Appears in:_
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `retryOn` _[RetryOnCondition](#retryoncondition) array_ | RetryOn specifies the conditions under which a retry should be attempted. |  | Enum: [5xx gateway-error reset reset-before-request connect-failure envoy-ratelimited retriable-4xx refused-stream retriable-status-codes http3-post-connect-failure cancelled deadline-exceeded internal resource-exhausted unavailable] <br />MinItems: 1 <br /> |
| `attempts` _integer_ | Attempts specifies the number of retry attempts for a request.<br />Defaults to 1 attempt if not set.<br />A value of 0 effectively disables retries. | 1 | Minimum: 0 <br /> |
| `perTryTimeout` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | PerTryTimeout specifies the timeout per retry attempt (incliding the initial attempt).<br />If a global timeout is configured on a route, this timeout must be less than the global<br />route timeout.<br />It is specified as a sequence of decimal numbers, each with optional fraction and a unit suffix, such as "1s" or "500ms". |  |  |
| `statusCodes` _HTTPRouteRetryStatusCode array_ | StatusCodes specifies the HTTP status codes in the range 400-599 that should be retried in addition<br />to the conditions specified in RetryOn. |  | MinItems: 1 <br /> |
| `backoffBaseInterval` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | BackoffBaseInterval specifies the base interval used with a fully jittered exponential back-off between retries.<br />Defaults to 25ms if not set.<br />Given a backoff base interval B and retry number N, the back-off for the retry is in the range [0, (2^N-1)*B].<br />The backoff interval is capped at a max of 10 times the base interval.<br />E.g., given a value of 25ms, the first retry will be delayed randomly by 0-24ms, the 2nd by 0-74ms,<br />the 3rd by 0-174ms, and so on, and capped to a max of 10 times the base interval (250ms). | 25ms |  |


#### RetryOnCondition

_Underlying type:_ _string_

RetryOnCondition specifies the condition under which retry takes place.

_Validation:_
- Enum: [5xx gateway-error reset reset-before-request connect-failure envoy-ratelimited retriable-4xx refused-stream retriable-status-codes http3-post-connect-failure cancelled deadline-exceeded internal resource-exhausted unavailable]

_Appears in:_
- [Retry](#retry)



#### RetryPolicy



Specifies the retry policy of remote data source when fetching fails.
Ref: https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/core/v3/base.proto#envoy-v3-api-msg-config-core-v3-retrypolicy



_Appears in:_
- [AccessLogGrpcService](#accessloggrpcservice)
- [CommonAccessLogGrpcService](#commonaccessloggrpcservice)
- [CommonGrpcService](#commongrpcservice)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `retryBackOff` _[BackoffStrategy](#backoffstrategy)_ | Specifies parameters that control retry backoff strategy.<br />the default base interval is 1000 milliseconds and the default maximum interval is 10 times the base interval. |  |  |
| `numRetries` _integer_ | Specifies the allowed number of retries. Defaults to 1. |  |  |


#### RouteType

_Underlying type:_ _string_

RouteType is the type of route to the LLM provider API.



_Appears in:_
- [AIPolicy](#aipolicy)

| Field | Description |
| --- | --- |
| `CHAT` | The LLM generates the full response before responding to a client.<br /> |
| `CHAT_STREAMING` | Stream responses to a client, which allows the LLM to stream out tokens as they are generated.<br /> |


#### Sampler



Sampler defines the list of supported Samplers

_Validation:_
- MaxProperties: 1
- MinProperties: 1

_Appears in:_
- [OpenTelemetryTracingConfig](#opentelemetrytracingconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `alwaysOnConfig` _[AlwaysOnConfig](#alwaysonconfig)_ |  |  |  |


#### SdsBootstrap



SdsBootstrap configures the SDS instance that is provisioned from a Kubernetes Gateway.



_Appears in:_
- [SdsContainer](#sdscontainer)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `logLevel` _string_ | Log level for SDS. Options include "info", "debug", "warn", "error", "panic" and "fatal".<br />Default level is "info". |  |  |


#### SdsContainer



SdsContainer configures the container running SDS sidecar.



_Appears in:_
- [KubernetesProxyConfig](#kubernetesproxyconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `image` _[Image](#image)_ | The SDS container image. See<br />https://kubernetes.io/docs/concepts/containers/images<br />for details. |  |  |
| `securityContext` _[SecurityContext](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#securitycontext-v1-core)_ | The security context for this container. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#securitycontext-v1-core<br />for details. |  |  |
| `resources` _[ResourceRequirements](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#resourcerequirements-v1-core)_ | The compute resources required by this container. See<br />https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/<br />for details. |  |  |
| `bootstrap` _[SdsBootstrap](#sdsbootstrap)_ | Initial SDS container configuration. |  |  |


#### SelfManagedGateway







_Appears in:_
- [GatewayParametersSpec](#gatewayparametersspec)



#### ServerHeaderTransformation

_Underlying type:_ _string_

ServerHeaderTransformation determines how the server header is transformed.



_Appears in:_
- [HTTPListenerPolicySpec](#httplistenerpolicyspec)

| Field | Description |
| --- | --- |
| `Overwrite` | OverwriteServerHeaderTransformation overwrites the server header.<br /> |
| `AppendIfAbsent` | AppendIfAbsentServerHeaderTransformation appends to the server header if it's not present.<br /> |
| `PassThrough` | PassThroughServerHeaderTransformation passes through the server header unchanged.<br /> |


#### Service



Configuration for a Kubernetes Service.



_Appears in:_
- [KubernetesProxyConfig](#kubernetesproxyconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `type` _[ServiceType](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#servicetype-v1-core)_ | The Kubernetes Service type. |  | Enum: [ClusterIP NodePort LoadBalancer ExternalName] <br /> |
| `clusterIP` _string_ | The manually specified IP address of the service, if a randomly assigned<br />IP is not desired. See<br />https://kubernetes.io/docs/concepts/services-networking/service/#choosing-your-own-ip-address<br />and<br />https://kubernetes.io/docs/concepts/services-networking/service/#headless-services<br />on the implications of setting `clusterIP`. |  |  |
| `extraLabels` _object (keys:string, values:string)_ | Additional labels to add to the Service object metadata. |  |  |
| `extraAnnotations` _object (keys:string, values:string)_ | Additional annotations to add to the Service object metadata. |  |  |
| `ports` _[Port](#port) array_ | Additional configuration for the service ports.<br />The actual port numbers are specified in the Gateway resource. |  |  |
| `externalTrafficPolicy` _string_ | ExternalTrafficPolicy defines the external traffic policy for the service.<br />Valid values are Cluster and Local. Default value is Cluster. |  |  |


#### ServiceAccount







_Appears in:_
- [KubernetesProxyConfig](#kubernetesproxyconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `extraLabels` _object (keys:string, values:string)_ | Additional labels to add to the ServiceAccount object metadata. |  |  |
| `extraAnnotations` _object (keys:string, values:string)_ | Additional annotations to add to the ServiceAccount object metadata. |  |  |


#### SingleAuthToken



SingleAuthToken configures the authorization token that the AI gateway uses to access the LLM provider API.
This token is automatically sent in a request header, depending on the LLM provider.



_Appears in:_
- [AnthropicConfig](#anthropicconfig)
- [AzureOpenAIConfig](#azureopenaiconfig)
- [GeminiConfig](#geminiconfig)
- [OpenAIConfig](#openaiconfig)
- [VertexAIConfig](#vertexaiconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `kind` _[SingleAuthTokenKind](#singleauthtokenkind)_ | Kind specifies which type of authorization token is being used.<br />Must be one of: "Inline", "SecretRef", "Passthrough". |  | Enum: [Inline SecretRef Passthrough] <br /> |
| `inline` _string_ | Provide the token directly in the configuration for the Backend.<br />This option is the least secure. Only use this option for quick tests such as trying out AI Gateway. |  |  |
| `secretRef` _[LocalObjectReference](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#localobjectreference-v1-core)_ | Store the API key in a Kubernetes secret in the same namespace as the Backend.<br />Then, refer to the secret in the Backend configuration. This option is more secure than an inline token,<br />because the API key is encoded and you can restrict access to secrets through RBAC rules.<br />You might use this option in proofs of concept, controlled development and staging environments,<br />or well-controlled prod environments that use secrets. |  |  |


#### SingleAuthTokenKind

_Underlying type:_ _string_





_Appears in:_
- [SingleAuthToken](#singleauthtoken)

| Field | Description |
| --- | --- |
| `Inline` | Inline provides the token directly in the configuration for the Backend.<br /> |
| `SecretRef` | SecretRef provides the token directly in the configuration for the Backend.<br /> |
| `Passthrough` | Passthrough the existing token. This token can either<br />come directly from the client, or be generated by an OIDC flow<br />early in the request lifecycle. This option is useful for<br />backends which have federated identity setup and can re-use<br />the token from the client.<br />Currently, this token must exist in the `Authorization` header.<br /> |


#### SlowStart







_Appears in:_
- [LoadBalancerLeastRequestConfig](#loadbalancerleastrequestconfig)
- [LoadBalancerRoundRobinConfig](#loadbalancerroundrobinconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `window` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | Represents the size of slow start window.<br />If set, the newly created host remains in slow start mode starting from its creation time<br />for the duration of slow start window. |  |  |
| `aggression` _string_ | This parameter controls the speed of traffic increase over the slow start window. Defaults to 1.0,<br />so that endpoint would get linearly increasing amount of traffic.<br />When increasing the value for this parameter, the speed of traffic ramp-up increases non-linearly.<br />The value of aggression parameter should be greater than 0.0.<br />By tuning the parameter, is possible to achieve polynomial or exponential shape of ramp-up curve.<br /><br />During slow start window, effective weight of an endpoint would be scaled with time factor and aggression:<br />`new_weight = weight * max(min_weight_percent, time_factor ^ (1 / aggression))`,<br />where `time_factor=(time_since_start_seconds / slow_start_time_seconds)`.<br /><br />As time progresses, more and more traffic would be sent to endpoint, which is in slow start window.<br />Once host exits slow start, time_factor and aggression no longer affect its weight. |  |  |
| `minWeightPercent` _integer_ | Minimum weight percentage of an endpoint during slow start. |  |  |


#### SourceIP

_Underlying type:_ _[struct{}](#struct{})_





_Appears in:_
- [HashPolicy](#hashpolicy)



#### StaticBackend



StaticBackend references a static list of hosts.



_Appears in:_
- [BackendSpec](#backendspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `hosts` _[Host](#host) array_ | Hosts is a list of hosts to use for the backend. |  | MinItems: 1 <br /> |
| `appProtocol` _[AppProtocol](#appprotocol)_ | AppProtocol is the application protocol to use when communicating with the backend. |  | Enum: [http2 grpc grpc-web kubernetes.io/h2c kubernetes.io/ws] <br /> |


#### StatsConfig



Configuration for the stats server.



_Appears in:_
- [KubernetesProxyConfig](#kubernetesproxyconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `enabled` _boolean_ | Whether to expose metrics annotations and ports for scraping metrics. |  |  |
| `routePrefixRewrite` _string_ | The Envoy stats endpoint to which the metrics are written |  |  |
| `enableStatsRoute` _boolean_ | Enables an additional route to the stats cluster defaulting to /stats |  |  |
| `statsRoutePrefixRewrite` _string_ | The Envoy stats endpoint with general metrics for the additional stats route |  |  |


#### StatusCodeFilter

_Underlying type:_ _[ComparisonFilter](#comparisonfilter)_

StatusCodeFilter filters based on HTTP status code.
Based on: https://www.envoyproxy.io/docs/envoy/v1.33.0/api-v3/config/accesslog/v3/accesslog.proto#envoy-v3-api-msg-config-accesslog-v3-statuscodefilter



_Appears in:_
- [FilterType](#filtertype)



#### StringMatcher



Specifies the way to match a string.



_Appears in:_
- [CSRFPolicy](#csrfpolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `exact` _string_ | The input string must match exactly the string specified here.<br />Example: abc matches the value abc |  |  |
| `prefix` _string_ | The input string must have the prefix specified here.<br />Note: empty prefix is not allowed, please use regex instead.<br />Example: abc matches the value abc.xyz |  |  |
| `suffix` _string_ | The input string must have the suffix specified here.<br />Note: empty prefix is not allowed, please use regex instead.<br />Example: abc matches the value xyz.abc |  |  |
| `contains` _string_ | The input string must contain the substring specified here.<br />Example: abc matches the value xyz.abc.def |  |  |
| `safeRegex` _string_ | The input string must match the Google RE2 regular expression specified here.<br />See https://github.com/google/re2/wiki/Syntax for the syntax. |  |  |
| `ignoreCase` _boolean_ | If true, indicates the exact/prefix/suffix/contains matching should be<br />case insensitive. This has no effect on the regex match.<br />For example, the matcher data will match both input string Data and data if this<br />option is set to true. | false |  |


#### SupportedLLMProvider



SupportedLLMProvider configures the AI gateway to use a single LLM provider backend.

_Validation:_
- MaxProperties: 1
- MinProperties: 1

_Appears in:_
- [LLMProvider](#llmprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `openai` _[OpenAIConfig](#openaiconfig)_ |  |  |  |
| `azureopenai` _[AzureOpenAIConfig](#azureopenaiconfig)_ |  |  |  |
| `anthropic` _[AnthropicConfig](#anthropicconfig)_ |  |  |  |
| `gemini` _[GeminiConfig](#geminiconfig)_ |  |  |  |
| `vertexai` _[VertexAIConfig](#vertexaiconfig)_ |  |  |  |
| `bedrock` _[BedrockConfig](#bedrockconfig)_ |  |  |  |


#### TCPKeepalive



See [Envoy documentation](https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/core/v3/address.proto#envoy-v3-api-msg-config-core-v3-tcpkeepalive) for more details.



_Appears in:_
- [BackendConfigPolicySpec](#backendconfigpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `keepAliveProbes` _integer_ | Maximum number of keep-alive probes to send before dropping the connection. |  |  |
| `keepAliveTime` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | The number of seconds a connection needs to be idle before keep-alive probes start being sent. |  |  |
| `keepAliveInterval` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | The number of seconds between keep-alive probes. |  |  |


#### TLS







_Appears in:_
- [BackendConfigPolicySpec](#backendconfigpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `secretRef` _[LocalObjectReference](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#localobjectreference-v1-core)_ | Reference to the TLS secret containing the certificate, key, and optionally the root CA. |  |  |
| `tlsFiles` _[TLSFiles](#tlsfiles)_ | File paths to certificates local to the proxy. |  |  |
| `insecureSkipVerify` _boolean_ | InsecureSkipVerify originates TLS but skips verification of the backend's certificate.<br />WARNING: This is an insecure option that should only be used if the risks are understood. |  |  |
| `sni` _string_ | The SNI domains that should be considered for TLS connection |  | MinLength: 1 <br /> |
| `verifySubjectAltName` _string array_ | Verify that the Subject Alternative Name in the peer certificate is one of the specified values.<br />note that a root_ca must be provided if this option is used. |  |  |
| `parameters` _[Parameters](#parameters)_ | General TLS parameters. See the [envoy docs](https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/transport_sockets/tls/v3/common.proto#extensions-transport-sockets-tls-v3-tlsparameters)<br />for more information on the meaning of these values. |  |  |
| `alpnProtocols` _string array_ | Set Application Level Protocol Negotiation<br />If empty, defaults to ["h2", "http/1.1"]. |  |  |
| `allowRenegotiation` _boolean_ | Allow Tls renegotiation, the default value is false.<br />TLS renegotiation is considered insecure and shouldn't be used unless absolutely necessary. |  |  |
| `simpleTLS` _boolean_ | If the TLS config has the tls cert and key provided, kgateway uses it to perform mTLS by default.<br />Set simpleTLS to true to disable mTLS in favor of server-only TLS (one-way TLS), even if kgateway has the client cert.<br />If unset, defaults to false. |  |  |


#### TLSFiles







_Appears in:_
- [TLS](#tls)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `tlsCertificate` _string_ |  |  | MinLength: 1 <br /> |
| `tlsKey` _string_ |  |  | MinLength: 1 <br /> |
| `rootCA` _string_ |  |  | MinLength: 1 <br /> |


#### TLSVersion

_Underlying type:_ _string_

TLSVersion defines the TLS version.

_Validation:_
- Enum: [AUTO 1.0 1.1 1.2 1.3]

_Appears in:_
- [Parameters](#parameters)

| Field | Description |
| --- | --- |
| `AUTO` |  |
| `1.0` |  |
| `1.1` |  |
| `1.2` |  |
| `1.3` |  |


#### Timeouts







_Appears in:_
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `request` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | Request specifies a timeout for an individual request from the gateway to a backend.<br />This spans between the point at which the entire downstream request (i.e. end-of-stream) has been<br />processed and when the backend response has been completely processed.<br />A value of 0 effectively disables the timeout.<br />It is specified as a sequence of decimal numbers, each with optional fraction and a unit suffix, such as "1s" or "500ms". |  |  |
| `streamIdle` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | StreamIdle specifies a timeout for a requests' idle streams.<br />A value of 0 effectively disables the timeout. |  |  |


#### TokenBucket



TokenBucket defines the configuration for a token bucket rate-limiting mechanism.
It controls the rate at which tokens are generated and consumed for a specific operation.



_Appears in:_
- [LocalRateLimitPolicy](#localratelimitpolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `maxTokens` _integer_ | MaxTokens specifies the maximum number of tokens that the bucket can hold.<br />This value must be greater than or equal to 1.<br />It determines the burst capacity of the rate limiter. |  | Minimum: 1 <br /> |
| `tokensPerFill` _integer_ | TokensPerFill specifies the number of tokens added to the bucket during each fill interval.<br />If not specified, it defaults to 1.<br />This controls the steady-state rate of token generation. | 1 | Minimum: 1 <br /> |
| `fillInterval` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | FillInterval defines the time duration between consecutive token fills.<br />This value must be a valid duration string (e.g., "1s", "500ms").<br />It determines the frequency of token replenishment. |  |  |


#### Tracing



Tracing represents the top-level Envoy's tracer.
Ref: https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/filters/network/http_connection_manager/v3/http_connection_manager.proto#extensions-filters-network-http-connection-manager-v3-httpconnectionmanager-tracing



_Appears in:_
- [HTTPListenerPolicySpec](#httplistenerpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `provider` _[TracingProvider](#tracingprovider)_ | Provider defines the upstream to which envoy sends traces |  | MaxProperties: 1 <br />MinProperties: 1 <br /> |
| `clientSampling` _integer_ | Target percentage of requests managed by this HTTP connection manager that will be force traced if the x-client-trace-id header is set. Defaults to 100% |  | Maximum: 100 <br />Minimum: 0 <br /> |
| `randomSampling` _integer_ | Target percentage of requests managed by this HTTP connection manager that will be randomly selected for trace generation, if not requested by the client or not forced. Defaults to 100% |  | Maximum: 100 <br />Minimum: 0 <br /> |
| `overallSampling` _integer_ | Target percentage of requests managed by this HTTP connection manager that will be traced after all other sampling checks have been applied (client-directed, force tracing, random sampling). Defaults to 100% |  | Maximum: 100 <br />Minimum: 0 <br /> |
| `verbose` _boolean_ | Whether to annotate spans with additional data. If true, spans will include logs for stream events. Defaults to false |  |  |
| `maxPathTagLength` _integer_ | Maximum length of the request path to extract and include in the HttpUrl tag. Used to truncate lengthy request paths to meet the needs of a tracing backend. Default: 256 |  |  |
| `attributes` _[CustomAttribute](#customattribute) array_ | A list of attributes with a unique name to create attributes for the active span. |  | MaxProperties: 2 <br />MinProperties: 1 <br /> |
| `spawnUpstreamSpan` _boolean_ | Create separate tracing span for each upstream request if true. Defaults to false<br />Link to envoy docs for more info |  |  |


#### TracingProvider



TracingProvider defines the list of providers for tracing

_Validation:_
- MaxProperties: 1
- MinProperties: 1

_Appears in:_
- [Tracing](#tracing)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `openTelemetry` _[OpenTelemetryTracingConfig](#opentelemetrytracingconfig)_ | Tracing contains various settings for Envoy's OTel tracer. |  |  |


#### TrafficPolicy









| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `gateway.kgateway.dev/v1alpha1` | | |
| `kind` _string_ | `TrafficPolicy` | | |
| `kind` _string_ | Kind is a string value representing the REST resource this object represents.<br />Servers may infer this from the endpoint the client submits requests to.<br />Cannot be updated.<br />In CamelCase.<br />More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds |  |  |
| `apiVersion` _string_ | APIVersion defines the versioned schema of this representation of an object.<br />Servers should convert recognized schemas to the latest internal value, and<br />may reject unrecognized values.<br />More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources |  |  |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[TrafficPolicySpec](#trafficpolicyspec)_ |  |  |  |
| `status` _[PolicyStatus](#policystatus)_ |  |  |  |


#### TrafficPolicySpec



TrafficPolicySpec defines the desired state of a traffic policy.
Note: Backend attachment is only supported for agentgateway.



_Appears in:_
- [TrafficPolicy](#trafficpolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `targetRefs` _[LocalPolicyTargetReferenceWithSectionName](#localpolicytargetreferencewithsectionname) array_ | TargetRefs specifies the target resources by reference to attach the policy to. |  | MaxItems: 16 <br />MinItems: 1 <br /> |
| `targetSelectors` _[LocalPolicyTargetSelectorWithSectionName](#localpolicytargetselectorwithsectionname) array_ | TargetSelectors specifies the target selectors to select resources to attach the policy to. |  |  |
| `ai` _[AIPolicy](#aipolicy)_ | AI is used to configure AI-based policies for the policy. |  |  |
| `transformation` _[TransformationPolicy](#transformationpolicy)_ | Transformation is used to mutate and transform requests and responses<br />before forwarding them to the destination. |  |  |
| `extProc` _[ExtProcPolicy](#extprocpolicy)_ | ExtProc specifies the external processing configuration for the policy. |  |  |
| `extAuth` _[ExtAuthPolicy](#extauthpolicy)_ | ExtAuth specifies the external authentication configuration for the policy.<br />This controls what external server to send requests to for authentication. |  |  |
| `rateLimit` _[RateLimit](#ratelimit)_ | RateLimit specifies the rate limiting configuration for the policy.<br />This controls the rate at which requests are allowed to be processed. |  |  |
| `cors` _[CorsPolicy](#corspolicy)_ | Cors specifies the CORS configuration for the policy. |  |  |
| `csrf` _[CSRFPolicy](#csrfpolicy)_ | Csrf specifies the Cross-Site Request Forgery (CSRF) policy for this traffic policy. |  |  |
| `headerModifiers` _[HeaderModifiers](#headermodifiers)_ | HeaderModifiers defines the policy to modify request and response headers. |  |  |
| `autoHostRewrite` _boolean_ | AutoHostRewrite rewrites the Host header to the DNS name of the selected upstream.<br />NOTE: This field is only honoured for HTTPRoute targets.<br />NOTE: If `autoHostRewrite` is set on a route that also has a [URLRewrite filter](https://gateway-api.sigs.k8s.io/reference/spec/#httpurlrewritefilter)<br />configured to override the `hostname`, the `hostname` value will be used and `autoHostRewrite` will be ignored. |  |  |
| `buffer` _[Buffer](#buffer)_ | Buffer can be used to set the maximum request size that will be buffered.<br />Requests exceeding this size will return a 413 response. |  |  |
| `timeouts` _[Timeouts](#timeouts)_ | Timeouts defines the timeouts for requests<br />It is applicable to HTTPRoutes and ignored for other targeted kinds. |  |  |
| `retry` _[Retry](#retry)_ | Retry defines the policy for retrying requests.<br />It is applicable to HTTPRoutes, Gateway listeners and XListenerSets, and ignored for other targeted kinds. |  |  |
| `rbac` _[RBAC](#rbac)_ | RBAC specifies the role-based access control configuration for the policy.<br />This defines the rules for authorization based on roles and permissions. |  |  |


#### Transform



Transform defines the operations to be performed by the transformation.
These operations may include changing the actual request/response but may also cause side effects.
Side effects may include setting info that can be used in future steps (e.g. dynamic metadata) and can cause envoy to buffer.



_Appears in:_
- [TransformationPolicy](#transformationpolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `set` _[HeaderTransformation](#headertransformation) array_ | Set is a list of headers and the value they should be set to. |  | MaxItems: 16 <br /> |
| `add` _[HeaderTransformation](#headertransformation) array_ | Add is a list of headers to add to the request and what that value should be set to.<br />If there is already a header with these values then append the value as an extra entry. |  | MaxItems: 16 <br /> |
| `remove` _string array_ | Remove is a list of header names to remove from the request/response. |  | MaxItems: 16 <br /> |
| `body` _[BodyTransformation](#bodytransformation)_ | Body controls both how to parse the body and if needed how to set.<br />If empty, body will not be buffered. |  |  |


#### TransformationPolicy



TransformationPolicy config is used to modify envoy behavior at a route level.
These modifications can be performed on the request and response paths.



_Appears in:_
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `request` _[Transform](#transform)_ | Request is used to modify the request path. |  |  |
| `response` _[Transform](#transform)_ | Response is used to modify the response path. |  |  |


#### UpgradeConfig



UpgradeConfig represents configuration for HTTP upgrades.



_Appears in:_
- [HTTPListenerPolicySpec](#httplistenerpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `enabledUpgrades` _string array_ | List of upgrade types to enable (e.g. "websocket", "CONNECT", etc.) |  | MinItems: 1 <br /> |


#### VertexAIConfig



VertexAIConfig settings for the [Vertex AI](https://cloud.google.com/vertex-ai/docs) LLM provider.
To find the values for the project ID, project location, and publisher, you can check the fields of an API request, such as
`https://{LOCATION}-aiplatform.googleapis.com/{VERSION}/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/{PROVIDER}/<model-path>`.



_Appears in:_
- [SupportedLLMProvider](#supportedllmprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `authToken` _[SingleAuthToken](#singleauthtoken)_ | The authorization token that the AI gateway uses to access the Vertex AI API.<br />This token is automatically sent in the `key` header of the request. |  |  |
| `model` _string_ | The Vertex AI model to use.<br />For more information, see the [Vertex AI model docs](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models). |  | MinLength: 1 <br /> |
| `apiVersion` _string_ | The version of the Vertex AI API to use.<br />For more information, see the [Vertex AI API reference](https://cloud.google.com/vertex-ai/docs/reference#versions). |  | MinLength: 1 <br /> |
| `projectId` _string_ | The ID of the Google Cloud Project that you use for the Vertex AI. |  | MinLength: 1 <br /> |
| `location` _string_ | The location of the Google Cloud Project that you use for the Vertex AI. |  | MinLength: 1 <br /> |
| `modelPath` _string_ | Optional: The model path to route to. Defaults to the Gemini model path, `generateContent`. |  |  |
| `publisher` _[Publisher](#publisher)_ | The type of publisher model to use. Currently, only Google is supported. |  | Enum: [GOOGLE] <br /> |


#### Webhook



Webhook configures a webhook to forward requests or responses to for prompt guarding.



_Appears in:_
- [PromptguardRequest](#promptguardrequest)
- [PromptguardResponse](#promptguardresponse)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `host` _[Host](#host)_ | Host to send the traffic to.<br />Note: TLS is not currently supported for webhook.<br />Example:<br />host:<br />  host: example.com  #The host name of the webhook endpoint.<br />  port: 443 	        #The port number on which the webhook is listening.<br /> |  |  |
| `forwardHeaders` _[HTTPHeaderMatch](#httpheadermatch) array_ | ForwardHeaders define headers to forward with the request to the webhook.<br />Note: This is not yet supported for agentgateway. |  |  |


