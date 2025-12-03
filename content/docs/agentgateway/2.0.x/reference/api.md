---
title: API reference
weight: 10
---

## Packages
- [gateway.kgateway.dev/v1alpha1](#gatewaykgatewaydevv1alpha1)


## gateway.kgateway.dev/v1alpha1


### Resource Types
- [Backend](#backend)
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
| `routeType` _[RouteType](#routetype)_ | The type of route to the LLM provider API. Currently, `CHAT` and `CHAT_STREAMING` are supported. | CHAT | Enum: [CHAT CHAT_STREAMING] <br /> |


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


#### AccessLog



AccessLog represents the top-level access log configuration.



_Appears in:_
- [HTTPListenerPolicySpec](#httplistenerpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `fileSink` _[FileSink](#filesink)_ | Output access logs to local file |  |  |
| `grpcService` _[GrpcService](#grpcservice)_ | Send access logs to gRPC service |  |  |
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


#### AiExtension



Configuration for the AI extension.



_Appears in:_
- [KubernetesProxyConfig](#kubernetesproxyconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `enabled` _boolean_ | Whether to enable the extension. |  | Optional: \{\} <br /> |
| `image` _[Image](#image)_ | The extension's container image. See<br />https://kubernetes.io/docs/concepts/containers/images<br />for details. |  | Optional: \{\} <br /> |
| `securityContext` _[SecurityContext](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#securitycontext-v1-core)_ | The security context for this container. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#securitycontext-v1-core<br />for details. |  | Optional: \{\} <br /> |
| `resources` _[ResourceRequirements](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#resourcerequirements-v1-core)_ | The compute resources required by this container. See<br />https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/<br />for details. |  | Optional: \{\} <br /> |
| `env` _[EnvVar](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#envvar-v1-core) array_ | The extension's container environment variables. |  | Optional: \{\} <br /> |
| `ports` _[ContainerPort](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#containerport-v1-core) array_ | The extension's container ports. |  | Optional: \{\} <br /> |
| `stats` _[AiExtensionStats](#aiextensionstats)_ | Additional stats config for AI Extension.<br />This config can be useful for adding custom labels to the request metrics.<br /><br />Example:<br />```yaml<br />stats:<br />  customLabels:<br />    - name: "subject"<br />      metadataNamespace: "envoy.filters.http.jwt_authn"<br />      metadataKey: "principal:sub"<br />    - name: "issuer"<br />      metadataNamespace: "envoy.filters.http.jwt_authn"<br />      metadataKey: "principal:iss"<br />``` |  |  |


#### AiExtensionStats







_Appears in:_
- [AiExtension](#aiextension)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `customLabels` _[CustomLabel](#customlabel) array_ | Set of custom labels to be added to the request metrics.<br />These will be added on each request which goes through the AI Extension. |  |  |


#### AnthropicConfig



AnthropicConfig settings for the [Anthropic](https://docs.anthropic.com/en/release-notes/api) LLM provider.



_Appears in:_
- [SupportedLLMProvider](#supportedllmprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `authToken` _[SingleAuthToken](#singleauthtoken)_ | The authorization token that the AI gateway uses to access the Anthropic API.<br />This token is automatically sent in the `x-api-key` header of the request. |  | Required: \{\} <br /> |
| `apiVersion` _string_ | Optional: A version header to pass to the Anthropic API.<br />For more information, see the [Anthropic API versioning docs](https://docs.anthropic.com/en/api/versioning). |  |  |
| `model` _string_ | Optional: Override the model name.<br />If unset, the model name is taken from the request.<br />This setting can be useful when testing model failover scenarios. |  |  |


#### AwsAuth



AwsAuth specifies the authentication method to use for the backend.



_Appears in:_
- [AwsBackend](#awsbackend)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `type` _[AwsAuthType](#awsauthtype)_ | Type specifies the authentication method to use for the backend. |  | Enum: [Secret] <br />Required: \{\} <br /> |
| `secretRef` _[LocalObjectReference](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#localobjectreference-v1-core)_ | SecretRef references a Kubernetes Secret containing the AWS credentials.<br />The Secret must have keys "accessKey", "secretKey", and optionally "sessionToken". |  | Optional: \{\} <br /> |


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
| `accountId` _string_ | AccountId is the AWS account ID to use for the backend. |  | MaxLength: 12 <br />MinLength: 1 <br />Pattern: `^[0-9]\{12\}$` <br />Required: \{\} <br /> |
| `auth` _[AwsAuth](#awsauth)_ | Auth specifies an explicit AWS authentication method for the backend.<br />When omitted, the authentication method will be inferred from the<br />environment (e.g. instance metadata, EKS Pod Identity, environment variables, etc.)<br />This may not work in all environments, so it is recommended to specify an authentication method.<br /><br />See the Envoy docs for more info:<br />https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/aws_request_signing_filter#credentials |  | Optional: \{\} <br /> |
| `lambda` _[AwsLambda](#awslambda)_ | Lambda configures the AWS lambda service. |  | Optional: \{\} <br /> |
| `region` _string_ | Region is the AWS region to use for the backend.<br />Defaults to us-east-1 if not specified. | us-east-1 | MaxLength: 63 <br />MinLength: 1 <br />Optional: \{\} <br />Pattern: `^[a-z0-9-]+$` <br /> |


#### AwsLambda



AwsLambda configures the AWS lambda service.



_Appears in:_
- [AwsBackend](#awsbackend)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `endpointURL` _string_ | EndpointURL is the URL or domain for the Lambda service. This is primarily<br />useful for testing and development purposes. When omitted, the default<br />lambda hostname will be used. |  | MaxLength: 2048 <br />Optional: \{\} <br />Pattern: `^https?://[-a-zA-Z0-9@:%.+~#?&/=]+$` <br /> |
| `functionName` _string_ | FunctionName is the name of the Lambda function to invoke. |  | Pattern: `^[A-Za-z0-9-_]\{1,140\}$` <br />Required: \{\} <br /> |
| `invocationMode` _string_ | InvocationMode defines how to invoke the Lambda function.<br />Defaults to Sync. | Sync | Enum: [Sync Async] <br />Optional: \{\} <br /> |
| `qualifier` _string_ | Qualifier is the alias or version for the Lambda function.<br />Valid values include a numeric version (e.g. "1"), an alias name<br />(alphanumeric plus "-" or "_"), or the special literal "$LATEST". |  | Optional: \{\} <br />Pattern: `^(\$LATEST\|[0-9]+\|[A-Za-z0-9-_]\{1,128\})$` <br /> |


#### AzureOpenAIConfig



AzureOpenAIConfig settings for the [Azure OpenAI](https://learn.microsoft.com/en-us/azure/ai-services/openai/) LLM provider.



_Appears in:_
- [SupportedLLMProvider](#supportedllmprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `authToken` _[SingleAuthToken](#singleauthtoken)_ | The authorization token that the AI gateway uses to access the Azure OpenAI API.<br />This token is automatically sent in the `api-key` header of the request. |  | Required: \{\} <br /> |
| `endpoint` _string_ | The endpoint for the Azure OpenAI API to use, such as `my-endpoint.openai.azure.com`.<br />If the scheme is included, it is stripped. |  | MinLength: 1 <br />Required: \{\} <br /> |
| `deploymentName` _string_ | The name of the Azure OpenAI model deployment to use.<br />For more information, see the [Azure OpenAI model docs](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models). |  | MinLength: 1 <br />Required: \{\} <br /> |
| `apiVersion` _string_ | The version of the Azure OpenAI API to use.<br />For more information, see the [Azure OpenAI API version reference](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#api-specs). |  | MinLength: 1 <br />Required: \{\} <br /> |


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


#### BackendSpec



BackendSpec defines the desired state of Backend.



_Appears in:_
- [Backend](#backend)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `type` _[BackendType](#backendtype)_ | Type indicates the type of the backend to be used. |  | Enum: [AI AWS Static] <br />Required: \{\} <br /> |
| `ai` _[AIBackend](#aibackend)_ | AI is the AI backend configuration. |  | MaxProperties: 1 <br />MinProperties: 1 <br /> |
| `aws` _[AwsBackend](#awsbackend)_ | Aws is the AWS backend configuration. |  |  |
| `static` _[StaticBackend](#staticbackend)_ | Static is the static backend configuration. |  |  |


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


#### BufferSettings



BufferSettings configures how the request body should be buffered.



_Appears in:_
- [ExtAuthPolicy](#extauthpolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `maxRequestBytes` _integer_ | MaxRequestBytes sets the maximum size of a message body to buffer.<br />Requests exceeding this size will receive HTTP 413 and not be sent to the authorization service. |  | Minimum: 1 <br />Required: \{\} <br /> |
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


#### ComparisonFilter

_Underlying type:_ _struct_

ComparisonFilter represents a filter based on a comparison.
Based on: https://www.envoyproxy.io/docs/envoy/v1.33.0/api-v3/config/accesslog/v3/accesslog.proto#config-accesslog-v3-comparisonfilter



_Appears in:_
- [DurationFilter](#durationfilter)
- [StatusCodeFilter](#statuscodefilter)



#### CustomLabel

_Underlying type:_ _struct_





_Appears in:_
- [AiExtensionStats](#aiextensionstats)



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
| `status` _integer_ | StatusCode defines the HTTP status code to return for this route. |  | Maximum: 599 <br />Minimum: 200 <br />Required: \{\} <br /> |
| `body` _string_ | Body defines the content to be returned in the HTTP response body.<br />The maximum length of the body is restricted to prevent excessively large responses. |  | MaxLength: 4096 <br />Optional: \{\} <br /> |


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



#### EnvoyBootstrap



Configuration for the Envoy proxy instance that is provisioned from a
Kubernetes Gateway.



_Appears in:_
- [EnvoyContainer](#envoycontainer)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `logLevel` _string_ | Envoy log level. Options include "trace", "debug", "info", "warn", "error",<br />"critical" and "off". Defaults to "info". See<br />https://www.envoyproxy.io/docs/envoy/latest/start/quick-start/run-envoy#debugging-envoy<br />for more information. |  | Optional: \{\} <br /> |
| `componentLogLevels` _object (keys:string, values:string)_ | Envoy log levels for specific components. The keys are component names and<br />the values are one of "trace", "debug", "info", "warn", "error",<br />"critical", or "off", e.g.<br /><br />	```yaml<br />	componentLogLevels:<br />	  upstream: debug<br />	  connection: trace<br />	```<br /><br />These will be converted to the `--component-log-level` Envoy argument<br />value. See<br />https://www.envoyproxy.io/docs/envoy/latest/start/quick-start/run-envoy#debugging-envoy<br />for more information.<br /><br />Note: the keys and values cannot be empty, but they are not otherwise validated. |  | Optional: \{\} <br /> |


#### EnvoyContainer



Configuration for the container running Envoy.



_Appears in:_
- [KubernetesProxyConfig](#kubernetesproxyconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `bootstrap` _[EnvoyBootstrap](#envoybootstrap)_ | Initial envoy configuration. |  | Optional: \{\} <br /> |
| `image` _[Image](#image)_ | The envoy container image. See<br />https://kubernetes.io/docs/concepts/containers/images<br />for details.<br /><br />Default values, which may be overridden individually:<br /><br />	registry: quay.io/solo-io<br />	repository: gloo-envoy-wrapper (OSS) / gloo-ee-envoy-wrapper (EE)<br />	tag: <gloo version> (OSS) / <gloo-ee version> (EE)<br />	pullPolicy: IfNotPresent |  | Optional: \{\} <br /> |
| `securityContext` _[SecurityContext](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#securitycontext-v1-core)_ | The security context for this container. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#securitycontext-v1-core<br />for details. |  | Optional: \{\} <br /> |
| `resources` _[ResourceRequirements](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#resourcerequirements-v1-core)_ | The compute resources required by this container. See<br />https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/<br />for details. |  | Optional: \{\} <br /> |


#### ExtAuthEnabled

_Underlying type:_ _string_

ExtAuthEnabled determines the enabled state of the ExtAuth filter.

_Validation:_
- Enum: [DisableAll]

_Appears in:_
- [ExtAuthPolicy](#extauthpolicy)

| Field | Description |
| --- | --- |
| `DisableAll` | ExtAuthDisableAll disables all instances of the ExtAuth filter for this route.<br />This is to enable a global disable such as for a health check route.<br /> |


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
| `extensionRef` _[LocalObjectReference](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#localobjectreference-v1-core)_ | ExtensionRef references the ExternalExtension that should be used for authentication. |  |  |
| `enablement` _[ExtAuthEnabled](#extauthenabled)_ | Enablement determines the enabled state of the ExtAuth filter.<br />When set to "DisableAll", the filter is disabled for this route.<br />When empty, the filter is enabled as long as it is not disabled by another policy. |  | Enum: [DisableAll] <br /> |
| `withRequestBody` _[BufferSettings](#buffersettings)_ | WithRequestBody allows the request body to be buffered and sent to the authorization service.<br />Warning buffering has implications for streaming and therefore performance. |  |  |
| `contextExtensions` _object (keys:string, values:string)_ | Additional context for the authorization service. |  |  |


#### ExtAuthProvider



ExtAuthProvider defines the configuration for an ExtAuth provider.



_Appears in:_
- [GatewayExtensionSpec](#gatewayextensionspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `grpcService` _[ExtGrpcService](#extgrpcservice)_ | GrpcService is the GRPC service that will handle the authentication. |  | Required: \{\} <br /> |


#### ExtGrpcService



ExtGrpcService defines the GRPC service that will handle the processing.



_Appears in:_
- [ExtAuthProvider](#extauthprovider)
- [ExtProcProvider](#extprocprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `backendRef` _[BackendRef](https://gateway-api.sigs.k8s.io/reference/spec/#backendref)_ | BackendRef references the backend GRPC service. |  | Required: \{\} <br /> |
| `authority` _string_ | Authority is the authority header to use for the GRPC service. |  |  |


#### ExtProcPolicy



ExtProcPolicy defines the configuration for the Envoy External Processing filter.



_Appears in:_
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `extensionRef` _[LocalObjectReference](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#localobjectreference-v1-core)_ | ExtensionRef references the GatewayExtension that should be used for external processing. |  | Required: \{\} <br /> |
| `processingMode` _[ProcessingMode](#processingmode)_ | ProcessingMode defines how the filter should interact with the request/response streams |  |  |


#### ExtProcProvider



ExtProcProvider defines the configuration for an ExtProc provider.



_Appears in:_
- [GatewayExtensionSpec](#gatewayextensionspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `grpcService` _[ExtGrpcService](#extgrpcservice)_ | GrpcService is the GRPC service that will handle the processing. |  | Required: \{\} <br /> |


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
| `field` _string_ | The name of the field. |  | MinLength: 1 <br />Required: \{\} <br /> |
| `value` _string_ | The field default value, which can be any JSON Data Type. |  | MinLength: 1 <br />Required: \{\} <br /> |
| `override` _boolean_ | Whether to override the field's value if it already exists.<br />Defaults to false. | false |  |


#### FileSink



FileSink represents the file sink configuration for access logs.



_Appears in:_
- [AccessLog](#accesslog)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `path` _string_ | the file path to which the file access logging service will sink |  | Required: \{\} <br /> |
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
| `type` _[GatewayExtensionType](#gatewayextensiontype)_ | Type indicates the type of the GatewayExtension to be used. |  | Enum: [ExtAuth ExtProc Extended] <br />Required: \{\} <br /> |
| `extAuth` _[ExtAuthProvider](#extauthprovider)_ | ExtAuth configuration for ExtAuth extension type. |  |  |
| `extProc` _[ExtProcProvider](#extprocprovider)_ | ExtProc configuration for ExtProc extension type. |  |  |


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
| `kube` _[KubernetesProxyConfig](#kubernetesproxyconfig)_ | The proxy will be deployed on Kubernetes. |  | Optional: \{\} <br /> |
| `selfManaged` _[SelfManagedGateway](#selfmanagedgateway)_ | The proxy will be self-managed and not auto-provisioned. |  | Optional: \{\} <br /> |


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
| `authToken` _[SingleAuthToken](#singleauthtoken)_ | The authorization token that the AI gateway uses to access the Gemini API.<br />This token is automatically sent in the `key` query parameter of the request. |  | Required: \{\} <br /> |
| `model` _string_ | The Gemini model to use.<br />For more information, see the [Gemini models docs](https://ai.google.dev/gemini-api/docs/models/gemini). |  | Required: \{\} <br /> |
| `apiVersion` _string_ | The version of the Gemini API to use.<br />For more information, see the [Gemini API version docs](https://ai.google.dev/gemini-api/docs/api-versions). |  | Required: \{\} <br /> |


#### GracefulShutdownSpec







_Appears in:_
- [Pod](#pod)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `enabled` _boolean_ | Enable grace period before shutdown to finish current requests while Envoy health checks fail to e.g. notify external load balancers. *NOTE:* This will not have any effect if you have not defined health checks via the health check filter |  | Optional: \{\} <br /> |
| `sleepTimeSeconds` _integer_ | Time (in seconds) for the preStop hook to wait before allowing Envoy to terminate |  | Optional: \{\} <br /> |


#### GrpcService



GrpcService represents the gRPC service configuration for access logs.



_Appears in:_
- [AccessLog](#accesslog)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `logName` _string_ | name of log stream |  | Required: \{\} <br /> |
| `backendRef` _[BackendRef](https://gateway-api.sigs.k8s.io/reference/spec/#backendref)_ | The backend gRPC service. Can be any type of supported backend (Kubernetes Service, kgateway Backend, etc..) |  | Required: \{\} <br /> |
| `additionalRequestHeadersToLog` _string array_ | Additional request headers to log in the access log |  |  |
| `additionalResponseHeadersToLog` _string array_ | Additional response headers to log in the access log |  |  |
| `additionalResponseTrailersToLog` _string array_ | Additional response trailers to log in the access log |  |  |




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









| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `gateway.kgateway.dev/v1alpha1` | | |
| `kind` _string_ | `HTTPListenerPolicy` | | |
| `kind` _string_ | Kind is a string value representing the REST resource this object represents.<br />Servers may infer this from the endpoint the client submits requests to.<br />Cannot be updated.<br />In CamelCase.<br />More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds |  |  |
| `apiVersion` _string_ | APIVersion defines the versioned schema of this representation of an object.<br />Servers should convert recognized schemas to the latest internal value, and<br />may reject unrecognized values.<br />More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources |  |  |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[HTTPListenerPolicySpec](#httplistenerpolicyspec)_ |  |  |  |
| `status` _[SimpleStatus](#simplestatus)_ |  |  |  |


#### HTTPListenerPolicySpec







_Appears in:_
- [HTTPListenerPolicy](#httplistenerpolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `targetRefs` _[LocalPolicyTargetReference](#localpolicytargetreference) array_ |  |  | MaxItems: 16 <br />MinItems: 1 <br /> |
| `accessLog` _[AccessLog](#accesslog) array_ | AccessLoggingConfig contains various settings for Envoy's access logging service.<br />See here for more information: https://www.envoyproxy.io/docs/envoy/v1.33.0/api-v3/config/accesslog/v3/accesslog.proto |  |  |


#### HeaderFilter



HeaderFilter filters requests based on headers.
Based on: https://www.envoyproxy.io/docs/envoy/v1.33.0/api-v3/config/accesslog/v3/accesslog.proto#config-accesslog-v3-headerfilter



_Appears in:_
- [FilterType](#filtertype)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `header` _[HTTPHeaderMatch](#httpheadermatch)_ |  |  | Required: \{\} <br /> |


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


#### Host



Host defines a static backend host.



_Appears in:_
- [LLMProvider](#llmprovider)
- [StaticBackend](#staticbackend)
- [Webhook](#webhook)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `host` _string_ | Host is the host name to use for the backend. |  | MinLength: 1 <br /> |
| `port` _[PortNumber](#portnumber)_ | Port is the port to use for the backend. |  | Required: \{\} <br /> |


#### Image



A container image. See https://kubernetes.io/docs/concepts/containers/images
for details.



_Appears in:_
- [AiExtension](#aiextension)
- [EnvoyContainer](#envoycontainer)
- [IstioContainer](#istiocontainer)
- [SdsContainer](#sdscontainer)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `registry` _string_ | The image registry. |  | Optional: \{\} <br /> |
| `repository` _string_ | The image repository (name). |  | Optional: \{\} <br /> |
| `tag` _string_ | The image tag. |  | Optional: \{\} <br /> |
| `digest` _string_ | The hash digest of the image, e.g. `sha256:12345...` |  | Optional: \{\} <br /> |
| `pullPolicy` _[PullPolicy](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#pullpolicy-v1-core)_ | The image pull policy for the container. See<br />https://kubernetes.io/docs/concepts/containers/images/#image-pull-policy<br />for details. |  | Optional: \{\} <br /> |


#### InjaTemplate

_Underlying type:_ _string_





_Appears in:_
- [BodyTransformation](#bodytransformation)
- [HeaderTransformation](#headertransformation)



#### IstioContainer



Configuration for the container running the istio-proxy.



_Appears in:_
- [IstioIntegration](#istiointegration)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `image` _[Image](#image)_ | The envoy container image. See<br />https://kubernetes.io/docs/concepts/containers/images<br />for details. |  | Optional: \{\} <br /> |
| `securityContext` _[SecurityContext](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#securitycontext-v1-core)_ | The security context for this container. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#securitycontext-v1-core<br />for details. |  | Optional: \{\} <br /> |
| `resources` _[ResourceRequirements](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#resourcerequirements-v1-core)_ | The compute resources required by this container. See<br />https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/<br />for details. |  | Optional: \{\} <br /> |
| `logLevel` _string_ | Log level for istio-proxy. Options include "info", "debug", "warning", and "error".<br />Default level is info Default is "warning". |  | Optional: \{\} <br /> |
| `istioDiscoveryAddress` _string_ | The address of the istio discovery service. Defaults to "istiod.istio-system.svc:15012". |  | Optional: \{\} <br /> |
| `istioMetaMeshId` _string_ | The mesh id of the istio mesh. Defaults to "cluster.local". |  | Optional: \{\} <br /> |
| `istioMetaClusterId` _string_ | The cluster id of the istio cluster. Defaults to "Kubernetes". |  | Optional: \{\} <br /> |


#### IstioIntegration



Configuration for the Istio integration settings used by a Gloo Gateway's data plane (Envoy proxy instance)



_Appears in:_
- [KubernetesProxyConfig](#kubernetesproxyconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `istioProxyContainer` _[IstioContainer](#istiocontainer)_ | Configuration for the container running istio-proxy.<br />Note that if Istio integration is not enabled, the istio container will not be injected<br />into the gateway proxy deployment. |  | Optional: \{\} <br /> |
| `customSidecars` _[Container](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#container-v1-core) array_ | do not use slice of pointers: https://github.com/kubernetes/code-generator/issues/166<br />Override the default Istio sidecar in gateway-proxy with a custom container. |  | Optional: \{\} <br /> |


#### KubernetesProxyConfig



Configuration for the set of Kubernetes resources that will be provisioned
for a given Gateway.



_Appears in:_
- [GatewayParametersSpec](#gatewayparametersspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `deployment` _[ProxyDeployment](#proxydeployment)_ | Use a Kubernetes deployment as the proxy workload type. Currently, this is the only<br />supported workload type. |  | Optional: \{\} <br /> |
| `envoyContainer` _[EnvoyContainer](#envoycontainer)_ | Configuration for the container running Envoy. |  | Optional: \{\} <br /> |
| `sdsContainer` _[SdsContainer](#sdscontainer)_ | Configuration for the container running the Secret Discovery Service (SDS). |  | Optional: \{\} <br /> |
| `podTemplate` _[Pod](#pod)_ | Configuration for the pods that will be created. |  | Optional: \{\} <br /> |
| `service` _[Service](#service)_ | Configuration for the Kubernetes Service that exposes the Envoy proxy over<br />the network. |  | Optional: \{\} <br /> |
| `serviceAccount` _[ServiceAccount](#serviceaccount)_ | Configuration for the Kubernetes ServiceAccount used by the Envoy pod. |  | Optional: \{\} <br /> |
| `istio` _[IstioIntegration](#istiointegration)_ | Configuration for the Istio integration. |  | Optional: \{\} <br /> |
| `stats` _[StatsConfig](#statsconfig)_ | Configuration for the stats server. |  | Optional: \{\} <br /> |
| `aiExtension` _[AiExtension](#aiextension)_ | Configuration for the AI extension. |  | Optional: \{\} <br /> |
| `floatingUserId` _boolean_ | Used to unset the `runAsUser` values in security contexts. |  |  |


#### LLMProvider







_Appears in:_
- [AIBackend](#aibackend)
- [Priority](#priority)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `provider` _[SupportedLLMProvider](#supportedllmprovider)_ | The LLM provider type to configure. |  | MaxProperties: 1 <br />MinProperties: 1 <br /> |
| `hostOverride` _[Host](#host)_ | Send requests to a custom host and port, such as to proxy the request,<br />or to use a different backend that is API-compliant with the Backend version. |  |  |


#### LocalPolicyTargetReference



Select the object to attach the policy to.
The object must be in the same namespace as the policy.
You can target only one object at a time.



_Appears in:_
- [HTTPListenerPolicySpec](#httplistenerpolicyspec)
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `group` _[Group](#group)_ | The API group of the target resource.<br />For Kubernetes Gateway API resources, the group is `gateway.networking.k8s.io`. |  | MaxLength: 253 <br />Pattern: `^$\|^[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*$` <br /> |
| `kind` _[Kind](#kind)_ | The API kind of the target resource,<br />such as Gateway or HTTPRoute. |  | MaxLength: 63 <br />MinLength: 1 <br />Pattern: `^[a-zA-Z]([-a-zA-Z0-9]*[a-zA-Z0-9])?$` <br /> |
| `name` _[ObjectName](#objectname)_ | The name of the target resource. |  | MaxLength: 253 <br />MinLength: 1 <br /> |


#### LocalRateLimitPolicy



LocalRateLimitPolicy represents a policy for local rate limiting.
It defines the configuration for rate limiting using a token bucket mechanism.



_Appears in:_
- [RateLimit](#ratelimit)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `tokenBucket` _[TokenBucket](#tokenbucket)_ | TokenBucket represents the configuration for a token bucket local rate-limiting mechanism.<br />It defines the parameters for controlling the rate at which requests are allowed. |  |  |


#### Message



An entry for a message to prepend or append to each prompt.



_Appears in:_
- [AIPromptEnrichment](#aipromptenrichment)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `role` _string_ | Role of the message. The available roles depend on the backend<br />LLM provider model, such as `SYSTEM` or `USER` in the OpenAI API. |  |  |
| `content` _string_ | String content of the message. |  |  |


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
| `priorities` _[Priority](#priority) array_ | The priority list of backend pools. Each entry represents a set of LLM provider backends.<br />The order defines the priority of the backend endpoints. |  | MaxItems: 20 <br />MinItems: 1 <br />Required: \{\} <br /> |




#### OpenAIConfig



OpenAIConfig settings for the [OpenAI](https://platform.openai.com/docs/api-reference/streaming) LLM provider.



_Appears in:_
- [Moderation](#moderation)
- [SupportedLLMProvider](#supportedllmprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `authToken` _[SingleAuthToken](#singleauthtoken)_ | The authorization token that the AI gateway uses to access the OpenAI API.<br />This token is automatically sent in the `Authorization` header of the<br />request and prefixed with `Bearer`. |  | Required: \{\} <br /> |
| `model` _string_ | Optional: Override the model name, such as `gpt-4o-mini`.<br />If unset, the model name is taken from the request.<br />This setting can be useful when setting up model failover within the same LLM provider. |  |  |


#### Pod



Configuration for a Kubernetes Pod template.



_Appears in:_
- [KubernetesProxyConfig](#kubernetesproxyconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `extraLabels` _object (keys:string, values:string)_ | Additional labels to add to the Pod object metadata. |  | Optional: \{\} <br /> |
| `extraAnnotations` _object (keys:string, values:string)_ | Additional annotations to add to the Pod object metadata. |  | Optional: \{\} <br /> |
| `securityContext` _[PodSecurityContext](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#podsecuritycontext-v1-core)_ | The pod security context. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#podsecuritycontext-v1-core<br />for details. |  | Optional: \{\} <br /> |
| `imagePullSecrets` _[LocalObjectReference](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#localobjectreference-v1-core) array_ | An optional list of references to secrets in the same namespace to use for<br />pulling any of the images used by this Pod spec. See<br />https://kubernetes.io/docs/concepts/containers/images/#specifying-imagepullsecrets-on-a-pod<br />for details. |  | Optional: \{\} <br /> |
| `nodeSelector` _object (keys:string, values:string)_ | A selector which must be true for the pod to fit on a node. See<br />https://kubernetes.io/docs/concepts/configuration/assign-pod-node/ for<br />details. |  | Optional: \{\} <br /> |
| `affinity` _[Affinity](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#affinity-v1-core)_ | If specified, the pod's scheduling constraints. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#affinity-v1-core<br />for details. |  | Optional: \{\} <br /> |
| `tolerations` _[Toleration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#toleration-v1-core) array_ | do not use slice of pointers: https://github.com/kubernetes/code-generator/issues/166<br />If specified, the pod's tolerations. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#toleration-v1-core<br />for details. |  | Optional: \{\} <br /> |
| `gracefulShutdown` _[GracefulShutdownSpec](#gracefulshutdownspec)_ | If specified, the pod's graceful shutdown spec. |  | Optional: \{\} <br /> |
| `terminationGracePeriodSeconds` _integer_ | If specified, the pod's termination grace period in seconds. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#pod-v1-core<br />for details |  | Optional: \{\} <br /> |
| `readinessProbe` _[Probe](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#probe-v1-core)_ | If specified, the pod's readiness probe. Periodic probe of container service readiness.<br />Container will be removed from service endpoints if the probe fails. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#probe-v1-core<br />for details. |  | Optional: \{\} <br /> |
| `livenessProbe` _[Probe](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#probe-v1-core)_ | If specified, the pod's liveness probe. Periodic probe of container service readiness.<br />Container will be restarted if the probe fails. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#probe-v1-core<br />for details. |  | Optional: \{\} <br /> |


#### PolicyAncestorStatus







_Appears in:_
- [PolicyStatus](#policystatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `ancestorRef` _[ParentReference](https://gateway-api.sigs.k8s.io/reference/spec/#parentreference)_ | AncestorRef corresponds with a ParentRef in the spec that this<br />PolicyAncestorStatus struct describes the status of. |  |  |
| `controllerName` _string_ | ControllerName is a domain/path string that indicates the name of the<br />controller that wrote this status. This corresponds with the<br />controllerName field on GatewayClass.<br /><br />Example: "example.net/gateway-controller".<br /><br />The format of this field is DOMAIN "/" PATH, where DOMAIN and PATH are<br />valid Kubernetes names<br />(https://kubernetes.io/docs/concepts/overview/working-with-objects/names/#names).<br /><br />Controllers MUST populate this field when writing status. Controllers should ensure that<br />entries to status populated with their ControllerName are cleaned up when they are no<br />longer necessary. |  |  |
| `conditions` _[Condition](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#condition-v1-meta) array_ | Conditions describes the status of the Policy with respect to the given Ancestor. |  | MaxItems: 8 <br />MinItems: 1 <br /> |




#### Port







_Appears in:_
- [Service](#service)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `port` _integer_ | The port number to match on the Gateway |  | Required: \{\} <br /> |
| `nodePort` _integer_ | The NodePort to be used for the service. If not specified, a random port<br />will be assigned by the Kubernetes API server. |  | Optional: \{\} <br /> |


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



_Appears in:_
- [AIPromptGuard](#aipromptguard)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `regex` _[Regex](#regex)_ | Regular expression (regex) matching for prompt guards and data masking. |  |  |
| `webhook` _[Webhook](#webhook)_ | Configure a webhook to forward responses to for prompt guarding. |  |  |


#### ProxyDeployment



Configuration for the Proxy deployment in Kubernetes.



_Appears in:_
- [KubernetesProxyConfig](#kubernetesproxyconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `replicas` _integer_ | The number of desired pods. Defaults to 1. |  | Optional: \{\} <br /> |


#### Publisher

_Underlying type:_ _string_

Publisher configures the type of publisher model to use for VertexAI. Currently, only Google is supported.



_Appears in:_
- [VertexAIConfig](#vertexaiconfig)

| Field | Description |
| --- | --- |
| `GOOGLE` |  |


#### RateLimit



RateLimit defines a rate limiting policy.



_Appears in:_
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `local` _[LocalRateLimitPolicy](#localratelimitpolicy)_ | Local defines a local rate limiting policy. |  |  |


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


#### ResponseFlagFilter



ResponseFlagFilter filters based on response flags.
Based on: https://www.envoyproxy.io/docs/envoy/v1.33.0/api-v3/config/accesslog/v3/accesslog.proto#config-accesslog-v3-responseflagfilter



_Appears in:_
- [FilterType](#filtertype)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `flags` _string array_ |  |  | MinItems: 1 <br /> |


#### RouteType

_Underlying type:_ _string_

RouteType is the type of route to the LLM provider API.



_Appears in:_
- [AIPolicy](#aipolicy)

| Field | Description |
| --- | --- |
| `CHAT` | The LLM generates the full response before responding to a client.<br /> |
| `CHAT_STREAMING` | Stream responses to a client, which allows the LLM to stream out tokens as they are generated.<br /> |


#### SdsBootstrap



Configuration for the SDS instance that is provisioned from a Kubernetes Gateway.



_Appears in:_
- [SdsContainer](#sdscontainer)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `logLevel` _string_ | Log level for SDS. Options include "info", "debug", "warn", "error", "panic" and "fatal".<br />Default level is "info". |  | Optional: \{\} <br /> |


#### SdsContainer



Configuration for the container running Gloo SDS.



_Appears in:_
- [KubernetesProxyConfig](#kubernetesproxyconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `image` _[Image](#image)_ | The SDS container image. See<br />https://kubernetes.io/docs/concepts/containers/images<br />for details. |  | Optional: \{\} <br /> |
| `securityContext` _[SecurityContext](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#securitycontext-v1-core)_ | The security context for this container. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#securitycontext-v1-core<br />for details. |  | Optional: \{\} <br /> |
| `resources` _[ResourceRequirements](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#resourcerequirements-v1-core)_ | The compute resources required by this container. See<br />https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/<br />for details. |  | Optional: \{\} <br /> |
| `bootstrap` _[SdsBootstrap](#sdsbootstrap)_ | Initial SDS container configuration. |  | Optional: \{\} <br /> |


#### SelfManagedGateway







_Appears in:_
- [GatewayParametersSpec](#gatewayparametersspec)



#### Service



Configuration for a Kubernetes Service.



_Appears in:_
- [KubernetesProxyConfig](#kubernetesproxyconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `type` _[ServiceType](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#servicetype-v1-core)_ | The Kubernetes Service type. |  | Enum: [ClusterIP NodePort LoadBalancer ExternalName] <br />Optional: \{\} <br /> |
| `clusterIP` _string_ | The manually specified IP address of the service, if a randomly assigned<br />IP is not desired. See<br />https://kubernetes.io/docs/concepts/services-networking/service/#choosing-your-own-ip-address<br />and<br />https://kubernetes.io/docs/concepts/services-networking/service/#headless-services<br />on the implications of setting `clusterIP`. |  | Optional: \{\} <br /> |
| `extraLabels` _object (keys:string, values:string)_ | Additional labels to add to the Service object metadata. |  | Optional: \{\} <br /> |
| `extraAnnotations` _object (keys:string, values:string)_ | Additional annotations to add to the Service object metadata. |  | Optional: \{\} <br /> |
| `ports` _[Port](#port) array_ | Additional configuration for the service ports.<br />The actual port numbers are specified in the Gateway resource. |  |  |


#### ServiceAccount







_Appears in:_
- [KubernetesProxyConfig](#kubernetesproxyconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `extraLabels` _object (keys:string, values:string)_ | Additional labels to add to the ServiceAccount object metadata. |  | Optional: \{\} <br /> |
| `extraAnnotations` _object (keys:string, values:string)_ | Additional annotations to add to the ServiceAccount object metadata. |  | Optional: \{\} <br /> |


#### SimpleStatus



SimpleStatus defines the observed state of the policy.



_Appears in:_
- [HTTPListenerPolicy](#httplistenerpolicy)
- [TrafficPolicy](#trafficpolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `conditions` _[Condition](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#condition-v1-meta) array_ | Conditions is the list of conditions for the policy. |  | MaxItems: 8 <br /> |


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


#### StaticBackend



StaticBackend references a static list of hosts.



_Appears in:_
- [BackendSpec](#backendspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `hosts` _[Host](#host) array_ | Hosts is a list of hosts to use for the backend. |  | MinItems: 1 <br /> |


#### StatsConfig



Configuration for the stats server.



_Appears in:_
- [KubernetesProxyConfig](#kubernetesproxyconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `enabled` _boolean_ | Whether to expose metrics annotations and ports for scraping metrics. |  | Optional: \{\} <br /> |
| `routePrefixRewrite` _string_ | The Envoy stats endpoint to which the metrics are written |  | Optional: \{\} <br /> |
| `enableStatsRoute` _boolean_ | Enables an additional route to the stats cluster defaulting to /stats |  | Optional: \{\} <br /> |
| `statsRoutePrefixRewrite` _string_ | The Envoy stats endpoint with general metrics for the additional stats route |  | Optional: \{\} <br /> |


#### StatusCodeFilter

_Underlying type:_ _[ComparisonFilter](#comparisonfilter)_

StatusCodeFilter filters based on HTTP status code.
Based on: https://www.envoyproxy.io/docs/envoy/v1.33.0/api-v3/config/accesslog/v3/accesslog.proto#envoy-v3-api-msg-config-accesslog-v3-statuscodefilter



_Appears in:_
- [FilterType](#filtertype)



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


#### TokenBucket



TokenBucket defines the configuration for a token bucket rate-limiting mechanism.
It controls the rate at which tokens are generated and consumed for a specific operation.



_Appears in:_
- [LocalRateLimitPolicy](#localratelimitpolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `maxTokens` _integer_ | MaxTokens specifies the maximum number of tokens that the bucket can hold.<br />This value must be greater than or equal to 1.<br />It determines the burst capacity of the rate limiter. |  | Minimum: 1 <br /> |
| `tokensPerFill` _integer_ | TokensPerFill specifies the number of tokens added to the bucket during each fill interval.<br />If not specified, it defaults to 1.<br />This controls the steady-state rate of token generation. | 1 |  |
| `fillInterval` _string_ | FillInterval defines the time duration between consecutive token fills.<br />This value must be a valid duration string (e.g., "1s", "500ms").<br />It determines the frequency of token replenishment. |  | Format: duration <br /> |


#### TrafficPolicy









| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `gateway.kgateway.dev/v1alpha1` | | |
| `kind` _string_ | `TrafficPolicy` | | |
| `kind` _string_ | Kind is a string value representing the REST resource this object represents.<br />Servers may infer this from the endpoint the client submits requests to.<br />Cannot be updated.<br />In CamelCase.<br />More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds |  |  |
| `apiVersion` _string_ | APIVersion defines the versioned schema of this representation of an object.<br />Servers should convert recognized schemas to the latest internal value, and<br />may reject unrecognized values.<br />More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources |  |  |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[TrafficPolicySpec](#trafficpolicyspec)_ |  |  |  |
| `status` _[SimpleStatus](#simplestatus)_ |  |  |  |


#### TrafficPolicySpec







_Appears in:_
- [TrafficPolicy](#trafficpolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `targetRefs` _[LocalPolicyTargetReference](#localpolicytargetreference) array_ |  |  | MaxItems: 16 <br />MinItems: 1 <br /> |
| `ai` _[AIPolicy](#aipolicy)_ | AI is used to configure AI-based policies for the policy. |  |  |
| `transformation` _[TransformationPolicy](#transformationpolicy)_ | Transformation is used to mutate and transform requests and responses<br />before forwarding them to the destination. |  |  |
| `extProc` _[ExtProcPolicy](#extprocpolicy)_ | ExtProc specifies the external processing configuration for the policy. |  |  |
| `extAuth` _[ExtAuthPolicy](#extauthpolicy)_ | ExtAuth specifies the external authentication configuration for the policy.<br />This controls what external server to send requests to for authentication. |  |  |
| `rateLimit` _[RateLimit](#ratelimit)_ | RateLimit specifies the rate limiting configuration for the policy.<br />This controls the rate at which requests are allowed to be processed. |  |  |


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


#### VertexAIConfig



VertexAIConfig settings for the [Vertex AI](https://cloud.google.com/vertex-ai/docs) LLM provider.
To find the values for the project ID, project location, and publisher, you can check the fields of an API request, such as
`https://{LOCATION}-aiplatform.googleapis.com/{VERSION}/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/{PROVIDER}/<model-path>`.



_Appears in:_
- [SupportedLLMProvider](#supportedllmprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `authToken` _[SingleAuthToken](#singleauthtoken)_ | The authorization token that the AI gateway uses to access the Vertex AI API.<br />This token is automatically sent in the `key` header of the request. |  | Required: \{\} <br /> |
| `model` _string_ | The Vertex AI model to use.<br />For more information, see the [Vertex AI model docs](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models). |  | MinLength: 1 <br />Required: \{\} <br /> |
| `apiVersion` _string_ | The version of the Vertex AI API to use.<br />For more information, see the [Vertex AI API reference](https://cloud.google.com/vertex-ai/docs/reference#versions). |  | MinLength: 1 <br />Required: \{\} <br /> |
| `projectId` _string_ | The ID of the Google Cloud Project that you use for the Vertex AI. |  | MinLength: 1 <br />Required: \{\} <br /> |
| `location` _string_ | The location of the Google Cloud Project that you use for the Vertex AI. |  | MinLength: 1 <br />Required: \{\} <br /> |
| `modelPath` _string_ | Optional: The model path to route to. Defaults to the Gemini model path, `generateContent`. |  |  |
| `publisher` _[Publisher](#publisher)_ | The type of publisher model to use. Currently, only Google is supported. |  | Enum: [GOOGLE] <br /> |


#### Webhook



Webhook configures a webhook to forward requests or responses to for prompt guarding.



_Appears in:_
- [PromptguardRequest](#promptguardrequest)
- [PromptguardResponse](#promptguardresponse)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `host` _[Host](#host)_ | Host to send the traffic to.<br />Note: TLS is not currently supported for webhook. |  | Required: \{\} <br /> |
| `forwardHeaders` _[HTTPHeaderMatch](#httpheadermatch) array_ | ForwardHeaders define headers to forward with the request to the webhook. |  |  |


