---
title: API reference
weight: 10
---

## Packages
- [gateway.kgateway.dev/v1alpha1](#gatewaykgatewaydevv1alpha1)


## gateway.kgateway.dev/v1alpha1


### Resource Types
- [AgentgatewayBackend](#agentgatewaybackend)
- [AgentgatewayPolicy](#agentgatewaypolicy)
- [Backend](#backend)
- [BackendConfigPolicy](#backendconfigpolicy)
- [DirectResponse](#directresponse)
- [GatewayExtension](#gatewayextension)
- [GatewayParameters](#gatewayparameters)
- [HTTPListenerPolicy](#httplistenerpolicy)
- [ListenerPolicy](#listenerpolicy)
- [TrafficPolicy](#trafficpolicy)



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


#### APIKeyAuthenticationMode

_Underlying type:_ _string_



_Validation:_
- Enum: [Strict Optional]

_Appears in:_
- [AgentAPIKeyAuthentication](#agentapikeyauthentication)

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
| `backendRef` _[BackendRef](https://gateway-api.sigs.k8s.io/reference/spec/#backendref)_ | The backend gRPC service. Can be any type of supported backend (Kubernetes Service, kgateway Backend, etc..) |  |  |
| `authority` _string_ | The :authority header in the grpc request. If this field is not set, the authority header value will be cluster_name.<br />Note that this authority does not override the SNI. The SNI is provided by the transport socket of the cluster. |  |  |
| `maxReceiveMessageLength` _integer_ | Maximum gRPC message size that is allowed to be received. If a message over this limit is received, the gRPC stream is terminated with the RESOURCE_EXHAUSTED error.<br />Defaults to 0, which means unlimited. |  | Minimum: 1 <br /> |
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


#### AgentAPIKeyAuthentication







_Appears in:_
- [AgentgatewayPolicyTraffic](#agentgatewaypolicytraffic)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `mode` _[APIKeyAuthenticationMode](#apikeyauthenticationmode)_ | Validation mode for api key authentication. | Strict | Enum: [Strict Optional] <br /> |
| `secretRef` _[LocalObjectReference](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#localobjectreference-v1-core)_ | secretRef references a Kubernetes secret storing a set of API Keys. If there are many keys, 'secretSelector' can be<br />used instead.<br /><br />Each entry in the Secret represents one API Key. The key is an arbitrary identifier. The value can either be:<br />* A string, representing the API Key.<br />* A JSON object, with two fields, `key` and `metadata`. `key` contains the API Key. `metadata` contains arbitrary JSON<br />  metadata associated with the key, which may be used by other policies. For example, you may write an authorization<br />  policy allow `apiKey.group == 'sales'`.<br /><br />Example:<br /><br />apiVersion: v1<br />kind: Secret<br />metadata:<br />  name: api-key<br />stringData:<br />  client1: \|<br />    \{<br />      "key": "k-123",<br />      "metadata": \{<br />        "group": "sales",<br />        "created_at": "2024-10-01T12:00:00Z",<br />      \}<br />    \}<br />  client2: "k-456" |  |  |
| `secretSelector` _[SecretSelector](#secretselector)_ | secretSelector selects multiple secrets containing API Keys. If the same key is defined in multiple secrets, the<br />behavior is undefined.<br /><br />Each entry in the Secret represents one API Key. The key is an arbitrary identifier. The value can either be:<br />* A string, representing the API Key.<br />* A JSON object, with two fields, `key` and `metadata`. `key` contains the API Key. `metadata` contains arbitrary JSON<br />  metadata associated with the key, which may be used by other policies. For example, you may write an authorization<br />  policy allow `apiKey.group == 'sales'`.<br /><br />Example:<br /><br />apiVersion: v1<br />kind: Secret<br />metadata:<br />  name: api-key<br />stringData:<br />  client1: \|<br />    \{<br />      "key": "k-123",<br />      "metadata": \{<br />        "group": "sales",<br />        "created_at": "2024-10-01T12:00:00Z",<br />      \}<br />    \}<br />  client2: "k-456" |  |  |


#### AgentAccessLog



accessLogs specifies how per-request access logs are emitted.



_Appears in:_
- [AgentgatewayPolicyFrontend](#agentgatewaypolicyfrontend)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `filter` _[CELExpression](#celexpression)_ | filter specifies a CEL expression that is used to filter logs. A log will only be emitted if the expression evaluates<br />to 'true'. |  | MaxLength: 16384 <br />MinLength: 1 <br /> |
| `attributes` _[AgentLogTracingFields](#agentlogtracingfields)_ | attributes specifies customizations to the key-value pairs that are logged |  |  |


#### AgentAttributeAdd







_Appears in:_
- [AgentLogTracingFields](#agentlogtracingfields)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ |  |  |  |
| `expression` _[CELExpression](#celexpression)_ |  |  | MaxLength: 16384 <br />MinLength: 1 <br /> |


#### AgentBasicAuthentication







_Appears in:_
- [AgentgatewayPolicyTraffic](#agentgatewaypolicytraffic)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `mode` _[BasicAuthenticationMode](#basicauthenticationmode)_ | validation mode for basic auth authentication. | Strict | Enum: [Strict Optional] <br /> |
| `realm` _string_ | realm specifies the 'realm' to return in the WWW-Authenticate header for failed authentication requests.<br />If unset, "Restricted" will be used. |  |  |
| `users` _string array_ | users provides an inline list of username/password pairs that will be accepted.<br />Each entry represents one line of the htpasswd format: https://httpd.apache.org/docs/2.4/programs/htpasswd.html.<br /><br />Note: passwords should be the hash of the password, not the raw password. Use the `htpasswd` or similar commands<br />to generate a hash. MD5, bcrypt, crypt, and SHA-1 are supported.<br /><br />Example:<br />users:<br />- "user1:$apr1$ivPt0D4C$DmRhnewfHRSrb3DQC.WHC."<br />- "user2:$2y$05$r3J4d3VepzFkedkd/q1vI.pBYIpSqjfN0qOARV3ScUHysatnS0cL2" |  | MaxItems: 256 <br />MinItems: 1 <br /> |
| `secretRef` _[LocalObjectReference](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#localobjectreference-v1-core)_ | secretRef references a Kubernetes secret storing the .htaccess file. The Secret must have a key named '.htaccess',<br />and should contain the complete .htaccess file.<br /><br />Note: passwords should be the hash of the password, not the raw password. Use the `htpasswd` or similar commands<br />to generate a hash. MD5, bcrypt, crypt, and SHA-1 are supported.<br /><br />Example:<br /><br />apiVersion: v1<br />kind: Secret<br />metadata:<br />  name: basic-auth<br />stringData:<br />  .htaccess: \|<br />    alice:$apr1$3zSE0Abt$IuETi4l5yO87MuOrbSE4V.<br />    bob:$apr1$Ukb5LgRD$EPY2lIfY.A54jzLELNIId/ |  |  |


#### AgentCSRFPolicy







_Appears in:_
- [AgentgatewayPolicyTraffic](#agentgatewaypolicytraffic)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `additionalOrigins` _string array_ | additionalOrigin specifies additional source origins that will be allowed in addition to the destination origin. The<br />`Origin` consists of a scheme and a host, with an optional port, and takes the form `<scheme>://<host>(:<port>)`. |  | MaxItems: 16 <br />MinItems: 1 <br /> |


#### AgentCorsPolicy







_Appears in:_
- [AgentgatewayPolicyTraffic](#agentgatewaypolicytraffic)



#### AgentDynamicForwardProxyBackend







_Appears in:_
- [AgentgatewayBackendSpec](#agentgatewaybackendspec)



#### AgentExtAuthBody







_Appears in:_
- [AgentExtAuthPolicy](#agentextauthpolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `maxSize` _integer_ | maxSize specifies how large in bytes the largest body that will be buffered and sent to the authorization server. If<br />the body size is larger than maxSize, then the request will be rejected with a response. |  | Minimum: 1 <br /> |


#### AgentExtAuthPolicy







_Appears in:_
- [AgentgatewayPolicyTraffic](#agentgatewaypolicytraffic)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `backendRef` _[BackendObjectReference](https://gateway-api.sigs.k8s.io/reference/spec/#backendobjectreference)_ | backendRef references the External Authorization server to reach.<br /><br />Supported types: Service and Backend. |  |  |
| `forwardBody` _[AgentExtAuthBody](#agentextauthbody)_ | forwardBody configures whether to include the HTTP body in the request. If enabled, the request body will be<br />buffered. |  |  |
| `contextExtensions` _object (keys:string, values:string)_ | contextExtensions specifies additional arbitrary key-value pairs to send to the authorization server. |  | MaxProperties: 64 <br /> |


#### AgentExtProcPolicy







_Appears in:_
- [AgentgatewayPolicyTraffic](#agentgatewaypolicytraffic)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `backendRef` _[BackendObjectReference](https://gateway-api.sigs.k8s.io/reference/spec/#backendobjectreference)_ | backendRef references the External Processor server to reach.<br />Supported types: Service and Backend. |  |  |


#### AgentHeaderName

_Underlying type:_ _string_

AgentHeaderName is the name of a header.

_Validation:_
- MaxLength: 256
- MinLength: 1
- Pattern: `^:?[A-Za-z0-9!#$%&'*+\-.^_\x60|~]+$`

_Appears in:_
- [AgentHeaderTransformation](#agentheadertransformation)
- [AgentTransform](#agenttransform)



#### AgentHeaderTransformation







_Appears in:_
- [AgentTransform](#agenttransform)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _[AgentHeaderName](#agentheadername)_ | the name of the header to add. |  | MaxLength: 256 <br />MinLength: 1 <br />Pattern: `^:?[A-Za-z0-9!#$%&'*+\-.^_\x60\|~]+$` <br /> |
| `value` _[CELExpression](#celexpression)_ | value is the CEL expression to apply to generate the output value for the header. |  | MaxLength: 16384 <br />MinLength: 1 <br /> |


#### AgentHostnameRewrite

_Underlying type:_ _string_





_Appears in:_
- [AgentHostnameRewriteConfig](#agenthostnamerewriteconfig)

| Field | Description |
| --- | --- |
| `Auto` |  |
| `None` |  |


#### AgentHostnameRewriteConfig







_Appears in:_
- [AgentgatewayPolicyTraffic](#agentgatewaypolicytraffic)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `mode` _[AgentHostnameRewrite](#agenthostnamerewrite)_ | mode sets the hostname rewrite mode.<br /><br />The following may be specified:<br />* Auto: automatically set the Host header based on the destination.<br />* None: do not rewrite the Host header. The original Host header will be passed through.<br /><br />This setting defaults to Auto when connecting to hostname-based Backend types, and None otherwise (for Service or<br />IP-based Backends). |  |  |


#### AgentJWKS







_Appears in:_
- [AgentJWTProvider](#agentjwtprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `remote` _[AgentRemoteJWKS](#agentremotejwks)_ | remote specifies how to reach the JSON Web Key Set from a remote address. |  |  |
| `inline` _string_ | inline specifies an inline JSON Web Key Set used validate the signature of the JWT. |  | MaxLength: 65536 <br />MinLength: 2 <br /> |


#### AgentJWTAuthentication







_Appears in:_
- [AgentgatewayPolicyTraffic](#agentgatewaypolicytraffic)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `mode` _[JWTAuthenticationMode](#jwtauthenticationmode)_ | validation mode for JWT authentication. | Strict | Enum: [Strict Optional Permissive] <br /> |
| `providers` _[AgentJWTProvider](#agentjwtprovider) array_ |  |  | MaxItems: 64 <br />MinItems: 1 <br /> |


#### AgentJWTProvider







_Appears in:_
- [AgentJWTAuthentication](#agentjwtauthentication)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `issuer` _string_ | issuer identifies the IdP that issued the JWT. This corresponds to the 'iss' claim (https://tools.ietf.org/html/rfc7519#section-4.1.1). |  |  |
| `audiences` _string array_ | audiences specifies the list of allowed audiences that are allowed access. This corresponds to the 'aud' claim (https://datatracker.ietf.org/doc/html/rfc7519#section-4.1.3).<br />If unset, any audience is allowed. |  | MaxItems: 64 <br />MinItems: 1 <br /> |
| `jwks` _[AgentJWKS](#agentjwks)_ | jwks defines the JSON Web Key Set used to validate the signature of the JWT. |  |  |


#### AgentLocalRateLimitPolicy



AgentLocalRateLimitPolicy represents a policy for local rate limiting.
It defines the configuration for rate limiting using a token bucket mechanism.



_Appears in:_
- [AgentRateLimit](#agentratelimit)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `requests` _integer_ | requests specifies the number of HTTP requests per unit of time that are allowed. Requests exceeding this limit will fail with<br />a 429 error. |  | Minimum: 1 <br /> |
| `tokens` _integer_ | tokens specifies the number of LLM tokens per unit of time that are allowed. Requests exceeding this limit will fail<br />with a 429 error.<br /><br />Both input and output tokens are counted. However, token counts are not known until the request completes. As a<br />result, token-based rate limits will apply to future requests only. |  | Minimum: 1 <br /> |
| `unit` _[LocalRateLimitUnit](#localratelimitunit)_ | unit specifies the unit of time that requests are limited based on. |  | Enum: [Seconds Minutes Hours] <br /> |
| `burst` _integer_ | burst specifies an allowance of requests above the request-per-unit that should be allowed within a short period of time. |  |  |


#### AgentLogTracingFields







_Appears in:_
- [AgentAccessLog](#agentaccesslog)
- [AgentTracing](#agenttracing)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `remove` _string array_ | remove lists the default fields that should be removed. For example, "http.method". |  | MaxItems: 32 <br />MinItems: 1 <br /> |
| `add` _[AgentAttributeAdd](#agentattributeadd) array_ | add specifies additional key-value pairs to be added to each entry.<br />The value is a CEL expression. If the CEL expression fails to evaluate, the pair will be excluded. |  | MinItems: 1 <br /> |


#### AgentRateLimit







_Appears in:_
- [AgentgatewayPolicyTraffic](#agentgatewaypolicytraffic)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `local` _[AgentLocalRateLimitPolicy](#agentlocalratelimitpolicy) array_ | Local defines a local rate limiting policy. |  | MaxItems: 16 <br />MinItems: 1 <br /> |
| `global` _[AgentRateLimitPolicy](#agentratelimitpolicy)_ | Global defines a global rate limiting policy using an external service. |  |  |


#### AgentRateLimitDescriptor







_Appears in:_
- [AgentRateLimitPolicy](#agentratelimitpolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `entries` _[AgentRateLimitDescriptorEntry](#agentratelimitdescriptorentry) array_ | entries are the individual components that make up this descriptor. |  | MaxItems: 16 <br />MinItems: 1 <br /> |
| `unit` _[RateLimitUnit](#ratelimitunit)_ | unit defines what to use as the cost function. If unspecified, Requests is used. |  | Enum: [Requests Tokens] <br /> |




#### AgentRateLimitPolicy







_Appears in:_
- [AgentRateLimit](#agentratelimit)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `backendRef` _[BackendObjectReference](https://gateway-api.sigs.k8s.io/reference/spec/#backendobjectreference)_ | backendRef references the Rate Limit server to reach.<br />Supported types: Service and Backend. |  |  |
| `domain` _string_ | domain specifies the domain under which this limit should apply.<br />This is an arbitrary string that enables a rate limit server to distinguish between different applications. |  |  |
| `descriptors` _[AgentRateLimitDescriptor](#agentratelimitdescriptor) array_ | Descriptors define the dimensions for rate limiting. These values are passed to the rate limit service which applies<br />configured limits based on them. Each descriptor represents a single rate limit rule with one or more entries. |  | MaxItems: 16 <br />MinItems: 1 <br /> |


#### AgentRemoteJWKS

_Underlying type:_ _struct_





_Appears in:_
- [AgentJWKS](#agentjwks)
- [MCPAuthentication](#mcpauthentication)





#### AgentStaticBackend







_Appears in:_
- [AgentgatewayBackendSpec](#agentgatewaybackendspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `host` _string_ | host to connect to. |  |  |
| `port` _integer_ | port to connect to. |  | Maximum: 65535 <br />Minimum: 1 <br /> |


#### AgentTimeouts







_Appears in:_
- [AgentgatewayPolicyTraffic](#agentgatewaypolicytraffic)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `request` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | request specifies a timeout for an individual request from the gateway to a backend. This covers the time from when<br />the request first starts being sent from the gateway to when the full response has been received from the backend. |  |  |


#### AgentTracing







_Appears in:_
- [AgentgatewayPolicyFrontend](#agentgatewaypolicyfrontend)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `backendRef` _[BackendObjectReference](https://gateway-api.sigs.k8s.io/reference/spec/#backendobjectreference)_ | backendRef references the OTLP server to reach.<br />Supported types: Service and Backend. |  |  |
| `protocol` _[TracingProtocol](#tracingprotocol)_ | protocol specifies the OTLP protocol variant to use. | HTTP | Enum: [HTTP GRPC] <br /> |
| `attributes` _[AgentLogTracingFields](#agentlogtracingfields)_ | attributes specifies customizations to the key-value pairs that are included in the trace |  |  |
| `randomSampling` _[CELExpression](#celexpression)_ | randomSampling is an expression to determine the amount of random sampling. Random sampling will initiate a new<br />trace span if the incoming request does not have a trace initiated already. This should evaluate to a float between<br />0.0-1.0, or a boolean (true/false) If unspecified, random sampling is disabled. |  | MaxLength: 16384 <br />MinLength: 1 <br /> |
| `clientSampling` _[CELExpression](#celexpression)_ | clientSampling is an expression to determine the amount of client sampling. Client sampling determines whether to<br />initiate a new trace span if the incoming request does have a trace already. This should evaluate to a float between<br />0.0-1.0, or a boolean (true/false) If unspecified, client sampling is 100% enabled. |  | MaxLength: 16384 <br />MinLength: 1 <br /> |


#### AgentTransform







_Appears in:_
- [AgentTransformationPolicy](#agenttransformationpolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `set` _[AgentHeaderTransformation](#agentheadertransformation) array_ | set is a list of headers and the value they should be set to. |  | MaxItems: 16 <br />MinItems: 1 <br /> |
| `add` _[AgentHeaderTransformation](#agentheadertransformation) array_ | add is a list of headers to add to the request and what that value should be set to. If there is already a header<br />with these values then append the value as an extra entry. |  | MaxItems: 16 <br />MinItems: 1 <br /> |
| `remove` _[AgentHeaderName](#agentheadername) array_ | Remove is a list of header names to remove from the request/response. |  | MaxItems: 16 <br />MaxLength: 256 <br />MinItems: 1 <br />MinLength: 1 <br />Pattern: `^:?[A-Za-z0-9!#$%&'*+\-.^_\x60\|~]+$` <br /> |
| `body` _[CELExpression](#celexpression)_ | body controls manipulation of the HTTP body. |  | MaxLength: 16384 <br />MinLength: 1 <br /> |


#### AgentTransformationPolicy







_Appears in:_
- [AgentgatewayPolicyTraffic](#agentgatewaypolicytraffic)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `request` _[AgentTransform](#agenttransform)_ | request is used to modify the request path. |  |  |
| `response` _[AgentTransform](#agenttransform)_ | response is used to modify the response path. |  |  |


#### Agentgateway



Agentgateway configures the agentgateway dataplane integration to be enabled if the `agentgateway` GatewayClass is used.



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
| `extraVolumeMounts` _[VolumeMount](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#volumemount-v1-core) array_ | Additional volume mounts to add to the container. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#volumemount-v1-core<br />for details. |  |  |


#### AgentgatewayBackend









| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `gateway.kgateway.dev/v1alpha1` | | |
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
| `static` _[AgentStaticBackend](#agentstaticbackend)_ | static represents a static hostname. |  |  |
| `ai` _[AIBackend](#aibackend)_ | ai represents a LLM backend. |  |  |
| `mcp` _[MCPBackend](#mcpbackend)_ | mcp represents an MCP backend |  |  |
| `dynamicForwardProxy` _[AgentDynamicForwardProxyBackend](#agentdynamicforwardproxybackend)_ | dynamicForwardProxy configures the proxy to dynamically send requests to the destination based on the incoming<br />request HTTP host header, or TLS SNI for TLS traffic.<br /><br />Note: this Backend type enables users to send trigger the proxy to send requests to arbitrary destinations. Proper<br />access controls must be put in place when using this backend type. |  |  |
| `policies` _[AgentgatewayPolicyBackendFull](#agentgatewaypolicybackendfull)_ | policies controls policies for communicating with this backend. Policies may also be set in AgentgatewayPolicy;<br />policies are merged on a field-level basis, with policies on the Backend (this field) taking precedence. |  |  |


#### AgentgatewayBackendStatus



AgentgatewayBackend defines the observed state of AgentgatewayBackend.



_Appears in:_
- [AgentgatewayBackend](#agentgatewaybackend)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `conditions` _[Condition](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#condition-v1-meta) array_ | Conditions is the list of conditions for the backend. |  | MaxItems: 8 <br /> |


#### AgentgatewayKeepalive



TCP Keepalive settings



_Appears in:_
- [BackendTCP](#backendtcp)
- [FrontendTCP](#frontendtcp)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `retries` _integer_ | retries specifies the maximum number of keep-alive probes to send before dropping the connection.<br />If unset, this defaults to 9. |  | Maximum: 64 <br />Minimum: 1 <br /> |
| `time` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | time specifies the number of seconds a connection needs to be idle before keep-alive probes start being sent.<br />If unset, this defaults to 180s. |  |  |
| `interval` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | interval specifies the number of seconds between keep-alive probes.<br />If unset, this defaults to 180s. |  |  |


#### AgentgatewayPolicy









| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `gateway.kgateway.dev/v1alpha1` | | |
| `kind` _string_ | `AgentgatewayPolicy` | | |
| `kind` _string_ | Kind is a string value representing the REST resource this object represents.<br />Servers may infer this from the endpoint the client submits requests to.<br />Cannot be updated.<br />In CamelCase.<br />More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds |  |  |
| `apiVersion` _string_ | APIVersion defines the versioned schema of this representation of an object.<br />Servers should convert recognized schemas to the latest internal value, and<br />may reject unrecognized values.<br />More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources |  |  |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[AgentgatewayPolicySpec](#agentgatewaypolicyspec)_ | spec defines the desired state of AgentgatewayPolicy. |  |  |
| `status` _[PolicyStatus](#policystatus)_ | status defines the current state of AgentgatewayPolicy. |  |  |


#### AgentgatewayPolicyBackendAI







_Appears in:_
- [NamedLLMProvider](#namedllmprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `ai` _[BackendAI](#backendai)_ | ai specifies settings for AI workloads. This is only applicable when connecting to a Backend of type 'ai'. |  |  |


#### AgentgatewayPolicyBackendFull







_Appears in:_
- [AgentgatewayBackendSpec](#agentgatewaybackendspec)
- [AgentgatewayPolicySpec](#agentgatewaypolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `ai` _[BackendAI](#backendai)_ | ai specifies settings for AI workloads. This is only applicable when connecting to a Backend of type 'ai'. |  |  |
| `mcp` _[BackendMCP](#backendmcp)_ | mcp specifies settings for MCP workloads. This is only applicable when connecting to a Backend of type 'mcp'. |  |  |


#### AgentgatewayPolicyBackendMCP







_Appears in:_
- [McpTarget](#mcptarget)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `mcp` _[BackendMCP](#backendmcp)_ | mcp specifies settings for MCP workloads. This is only applicable when connecting to a Backend of type 'mcp'. |  |  |


#### AgentgatewayPolicyBackendSimple

_Underlying type:_ _struct_





_Appears in:_
- [AgentgatewayPolicyBackendAI](#agentgatewaypolicybackendai)
- [AgentgatewayPolicyBackendFull](#agentgatewaypolicybackendfull)
- [AgentgatewayPolicyBackendMCP](#agentgatewaypolicybackendmcp)
- [OpenAIModeration](#openaimoderation)



#### AgentgatewayPolicyFrontend







_Appears in:_
- [AgentgatewayPolicySpec](#agentgatewaypolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `tcp` _[FrontendTCP](#frontendtcp)_ | tcp defines settings on managing incoming TCP connections. |  |  |
| `tls` _[FrontendTLS](#frontendtls)_ | tls defines settings on managing incoming TLS connections. |  |  |
| `http` _[FrontendHTTP](#frontendhttp)_ | http defines settings on managing incoming HTTP requests. |  |  |
| `accessLog` _[AgentAccessLog](#agentaccesslog)_ | AccessLoggingConfig contains access logging configuration |  |  |
| `tracing` _[AgentTracing](#agenttracing)_ | Tracing contains various settings for OpenTelemetry tracer.<br />TODO: not currently implemented |  |  |


#### AgentgatewayPolicySpec







_Appears in:_
- [AgentgatewayPolicy](#agentgatewaypolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `targetRefs` _[LocalPolicyTargetReferenceWithSectionName](#localpolicytargetreferencewithsectionname) array_ | targetRefs specifies the target resources by reference to attach the policy to. |  | MaxItems: 16 <br />MinItems: 1 <br /> |
| `targetSelectors` _[LocalPolicyTargetSelectorWithSectionName](#localpolicytargetselectorwithsectionname) array_ | targetSelectors specifies the target selectors to select resources to attach the policy to. |  | MaxItems: 16 <br />MinItems: 1 <br /> |
| `frontend` _[AgentgatewayPolicyFrontend](#agentgatewaypolicyfrontend)_ | frontend defines settings for how to handle incoming traffic.<br /><br />A frontend policy can only target a Gateway. Listener and ListenerSet are not valid targets.<br /><br />When multiple policies are selected for a given request, they are merged on a field-level basis, but not a deep<br />merge. For example, policy A sets 'tcp' and 'tls', and policy B sets 'tls', the effective policy would be 'tcp' from<br />policy A, and 'tls' from policy B. |  |  |
| `traffic` _[AgentgatewayPolicyTraffic](#agentgatewaypolicytraffic)_ | traffic defines settings for how process traffic.<br /><br />A traffic policy can target a Gateway (optionally, with a sectionName indicating the listener), ListenerSet, Route<br />(optionally, with a sectionName indicating the route rule).<br /><br />When multiple policies are selected for a given request, they are merged on a field-level basis, but not a deep<br />merge. Precedence is given to more precise policies: Gateway < Listener < Route < Route Rule. For example, policy A<br />sets 'timeouts' and 'retries', and policy B sets 'retries', the effective policy would be 'timeouts' from policy A,<br />and 'retries' from policy B. |  |  |
| `backend` _[AgentgatewayPolicyBackendFull](#agentgatewaypolicybackendfull)_ | backend defines settings for how to connect to destination backends.<br /><br />A backend policy can target a Gateway (optionally, with a sectionName indicating the listener), ListenerSet, Route<br />(optionally, with a sectionName indicating the route rule), or a Service/Backend (optionally, with a sectionName<br />indicating the port (for Service) or sub-backend (for Backend).<br /><br />Note that a backend policy applies when connecting to a specific destination backend. Targeting a higher level<br />resource, like Gateway, is just a way to easily apply a policy to a group of backends.<br /><br />When multiple policies are selected for a given request, they are merged on a field-level basis, but not a deep<br />merge. Precedence is given to more precise policies: Gateway < Listener < Route < Route Rule < Backend/Service. For<br />example, if a Gateway policy sets 'tcp' and 'tls', and a Backend policy sets 'tls', the effective policy would be<br />'tcp' from the Gateway, and 'tls' from the Backend. |  |  |


#### AgentgatewayPolicyTraffic







_Appears in:_
- [AgentgatewayPolicySpec](#agentgatewaypolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `phase` _[PolicyPhase](#policyphase)_ | The phase to apply the traffic policy to. If the phase is PreRouting, the targetRef must be a Gateway or a Listener.<br />PreRouting is typically used only when a policy needs to influence the routing decision.<br /><br />Even when using PostRouting mode, the policy can target the Gateway/Listener. This is a helper for applying the policy<br />to all routes under that Gateway/Listener, and follows the merging logic described above.<br /><br />Note: PreRouting and PostRouting rules do not merge together. These are independent execution phases. That is, all<br />PreRouting rules will merge and execute, then all PostRouting rules will merge and execute.<br /><br />If unset, this defaults to PostRouting. |  | Enum: [PreRouting PostRouting] <br /> |
| `transformation` _[AgentTransformationPolicy](#agenttransformationpolicy)_ | transformation is used to mutate and transform requests and responses<br />before forwarding them to the destination. |  |  |
| `extProc` _[AgentExtProcPolicy](#agentextprocpolicy)_ | extProc specifies the external processing configuration for the policy. |  |  |
| `extAuth` _[AgentExtAuthPolicy](#agentextauthpolicy)_ | extAuth specifies the external authentication configuration for the policy.<br />This controls what external server to send requests to for authentication. |  |  |
| `rateLimit` _[AgentRateLimit](#agentratelimit)_ | rateLimit specifies the rate limiting configuration for the policy.<br />This controls the rate at which requests are allowed to be processed. |  |  |
| `cors` _[AgentCorsPolicy](#agentcorspolicy)_ | cors specifies the CORS configuration for the policy. |  |  |
| `csrf` _[AgentCSRFPolicy](#agentcsrfpolicy)_ | csrf specifies the Cross-Site Request Forgery (CSRF) policy for this traffic policy.<br /><br />The CSRF policy has the following behavior:<br />* Safe methods (GET, HEAD, OPTIONS) are automatically allowed<br />* Requests without Sec-Fetch-Site or Origin headers are assumed to be same-origin or non-browser requests and are allowed.<br />* Otherwise, the Sec-Fetch-Site header is checked, with a fallback to comparing the Origin header to the Host header. |  |  |
| `headerModifiers` _[HeaderModifiers](#headermodifiers)_ | headerModifiers defines the policy to modify request and response headers. |  |  |
| `hostRewrite` _[AgentHostnameRewriteConfig](#agenthostnamerewriteconfig)_ | hostRewrite specifies how to rewrite the Host header for requests.<br /><br />If the HTTPRoute `urlRewrite` filter already specifies a host rewrite, this setting is ignored. |  | Enum: [Auto None] <br /> |
| `timeouts` _[AgentTimeouts](#agenttimeouts)_ | timeouts defines the timeouts for requests<br />It is applicable to HTTPRoutes and ignored for other targeted kinds. |  |  |
| `retry` _[Retry](#retry)_ | retry defines the policy for retrying requests. |  |  |
| `authorization` _[Authorization](#authorization)_ | authorization specifies the access rules based on roles and permissions.<br />If multiple authorization rules are applied across different policies (at the same, or different, attahcment points),<br />all rules are merged. |  |  |
| `jwtAuthentication` _[AgentJWTAuthentication](#agentjwtauthentication)_ | jwtAuthentication authenticates users based on JWT tokens. |  |  |
| `basicAuthentication` _[AgentBasicAuthentication](#agentbasicauthentication)_ | basicAuthentication authenticates users based on the "Basic" authentication scheme (RFC 7617), where a username and password<br />are encoded in the request. |  |  |
| `apiKeyAuthentication` _[AgentAPIKeyAuthentication](#agentapikeyauthentication)_ | apiKeyAuthentication authenticates users based on a configured API Key. |  |  |


#### AlwaysOnConfig

_Underlying type:_ _struct_

AlwaysOnConfig specified the AlwaysOn samplerc



_Appears in:_
- [Sampler](#sampler)



#### AnthropicConfig



AnthropicConfig settings for the [Anthropic](https://docs.anthropic.com/en/release-notes/api) LLM provider.



_Appears in:_
- [LLMProvider](#llmprovider)
- [NamedLLMProvider](#namedllmprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `model` _string_ | Optional: Override the model name, such as `gpt-4o-mini`.<br />If unset, the model name is taken from the request. |  |  |


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


#### Authorization



Authorization defines the configuration for role-based access control.



_Appears in:_
- [AgentgatewayPolicyTraffic](#agentgatewaypolicytraffic)
- [BackendMCP](#backendmcp)
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `policy` _[AuthorizationPolicy](#authorizationpolicy)_ | Policy specifies the Authorization rule to evaluate.<br />A policy matches when **any** of the conditions evaluates to true. |  |  |
| `action` _[AuthorizationPolicyAction](#authorizationpolicyaction)_ | Action defines whether the rule allows or denies the request if matched.<br />If unspecified, the default is "Allow". | Allow | Enum: [Allow Deny] <br /> |


#### AuthorizationPolicy



AuthorizationPolicy defines a single Authorization rule.



_Appears in:_
- [Authorization](#authorization)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `matchExpressions` _[CELExpression](#celexpression) array_ | MatchExpressions defines a set of conditions that must be satisfied for the rule to match.<br />These expression should be in the form of a Common Expression Language (CEL) expression. |  | MaxItems: 256 <br />MaxLength: 16384 <br />MinItems: 1 <br />MinLength: 1 <br /> |


#### AuthorizationPolicyAction

_Underlying type:_ _string_

AuthorizationPolicyAction defines the action to take when the RBACPolicies matches.



_Appears in:_
- [Authorization](#authorization)

| Field | Description |
| --- | --- |
| `Allow` | AuthorizationPolicyActionAllow defines the action to take when the RBACPolicies matches.<br /> |
| `Deny` | AuthorizationPolicyActionDeny denies the action to take when the RBACPolicies matches.<br /> |


#### AwsAuth



AwsAuth specifies the authentication method to use for the backend.



_Appears in:_
- [AwsBackend](#awsbackend)

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
- [LLMProvider](#llmprovider)
- [NamedLLMProvider](#namedllmprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `endpoint` _string_ | The endpoint for the Azure OpenAI API to use, such as `my-endpoint.openai.azure.com`.<br />If the scheme is included, it is stripped. |  | MinLength: 1 <br /> |
| `deploymentName` _string_ | The name of the Azure OpenAI model deployment to use.<br />For more information, see the [Azure OpenAI model docs](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models).<br />This is required if ApiVersion is not 'v1'. For v1, the model can be set in the request. |  | MinLength: 1 <br /> |
| `apiVersion` _string_ | The version of the Azure OpenAI API to use.<br />For more information, see the [Azure OpenAI API version reference](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#api-specs).<br />If unset, defaults to "v1" |  |  |


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






#### BackendAuthPassthrough







_Appears in:_
- [BackendAuth](#backendauth)



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
| `perConnectionBufferLimitBytes` _integer_ | Soft limit on the size of the cluster's connections read and write buffers.<br />If unspecified, an implementation-defined default is applied (1MiB). |  | Minimum: 0 <br /> |
| `tcpKeepalive` _[TCPKeepalive](#tcpkeepalive)_ | Configure OS-level TCP keepalive checks. |  |  |
| `commonHttpProtocolOptions` _[CommonHttpProtocolOptions](#commonhttpprotocoloptions)_ | Additional options when handling HTTP requests upstream, applicable to<br />both HTTP1 and HTTP2 requests. |  |  |
| `http1ProtocolOptions` _[Http1ProtocolOptions](#http1protocoloptions)_ | Additional options when handling HTTP1 requests upstream. |  |  |
| `http2ProtocolOptions` _[Http2ProtocolOptions](#http2protocoloptions)_ | Http2ProtocolOptions contains the options necessary to configure HTTP/2 backends.<br />Note: Http2ProtocolOptions can only be applied to HTTP/2 backends.<br />See [Envoy documentation](https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/transport_sockets/tls/v3/tls.proto#envoy-v3-api-msg-extensions-transport-sockets-tls-v3-sslconfig) for more details. |  |  |
| `tls` _[TLS](#tls)_ | TLS contains the options necessary to configure a backend to use TLS origination.<br />See [Envoy documentation](https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/transport_sockets/tls/v3/tls.proto#envoy-v3-api-msg-extensions-transport-sockets-tls-v3-sslconfig) for more details. |  |  |
| `loadBalancer` _[LoadBalancer](#loadbalancer)_ | LoadBalancer contains the options necessary to configure the load balancer. |  |  |
| `healthCheck` _[HealthCheck](#healthcheck)_ | HealthCheck contains the options necessary to configure the health check. |  |  |
| `outlierDetection` _[OutlierDetection](#outlierdetection)_ | OutlierDetection contains the options necessary to configure passive health checking. |  |  |
| `circuitBreakers` _[CircuitBreakers](#circuitbreakers)_ | CircuitBreakers contains the options necessary to configure circuit breaking.<br />See [Envoy documentation](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/circuit_breaking) for more details. |  |  |






#### BackendSpec



BackendSpec defines the desired state of Backend.



_Appears in:_
- [Backend](#backend)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `type` _[BackendType](#backendtype)_ | Type indicates the type of the backend to be used. |  | Enum: [AWS Static DynamicForwardProxy] <br /> |
| `aws` _[AwsBackend](#awsbackend)_ | Aws is the AWS backend configuration.<br />The Aws backend type is only supported with envoy-based gateways, it is not supported in agentgateway. |  |  |
| `static` _[StaticBackend](#staticbackend)_ | Static is the static backend configuration. |  |  |
| `dynamicForwardProxy` _[DynamicForwardProxyBackend](#dynamicforwardproxybackend)_ | DynamicForwardProxy is the dynamic forward proxy backend configuration. |  |  |


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
| `AWS` | BackendTypeAWS is the type for AWS backends.<br /> |
| `Static` | BackendTypeStatic is the type for static backends.<br /> |
| `DynamicForwardProxy` | BackendTypeDynamicForwardProxy is the type for dynamic forward proxy backends.<br /> |




#### BasicAuthenticationMode

_Underlying type:_ _string_



_Validation:_
- Enum: [Strict Optional]

_Appears in:_
- [AgentBasicAuthentication](#agentbasicauthentication)

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
| `value` _[InjaTemplate](#injatemplate)_ | Value is the template to apply to generate the output value for the body.<br />Only Inja templates are supported. |  |  |


#### Buffer







_Appears in:_
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `maxRequestSize` _[Quantity](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#quantity-resource-api)_ | MaxRequestSize sets the maximum size in bytes of a message body to buffer.<br />Requests exceeding this size will receive HTTP 413.<br />Example format: "1Mi", "512Ki", "1Gi" |  |  |
| `disable` _[PolicyDisable](#policydisable)_ | Disable the buffer filter.<br />Can be used to disable buffer policies applied at a higher level in the config hierarchy. |  |  |


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


#### CELExpression

_Underlying type:_ _string_

A Common Expression Language (CEL) expression. See https://agentgateway.dev/docs/reference/cel/ for more info.

_Validation:_
- MaxLength: 16384
- MinLength: 1

_Appears in:_
- [AgentAccessLog](#agentaccesslog)
- [AgentAttributeAdd](#agentattributeadd)
- [AgentHeaderTransformation](#agentheadertransformation)
- [AgentRateLimitDescriptorEntry](#agentratelimitdescriptorentry)
- [AgentTracing](#agenttracing)
- [AgentTransform](#agenttransform)
- [AuthorizationPolicy](#authorizationpolicy)



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


#### CircuitBreakers



CircuitBreakers contains the options to configure circuit breaker thresholds for the default priority.
See [Envoy documentation](https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/cluster/v3/circuit_breaker.proto) for more details.



_Appears in:_
- [BackendConfigPolicySpec](#backendconfigpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `maxConnections` _integer_ | MaxConnections is the maximum number of connections that will be made to<br />the upstream cluster. If not specified, defaults to 1024. |  | Minimum: 1 <br /> |
| `maxPendingRequests` _integer_ | MaxPendingRequests is the maximum number of pending requests that are<br />allowed to the upstream cluster. If not specified, defaults to 1024. |  | Minimum: 1 <br /> |
| `maxRequests` _integer_ | MaxRequests is the maximum number of parallel requests that are allowed<br />to the upstream cluster. If not specified, defaults to 1024. |  | Minimum: 1 <br /> |
| `maxRetries` _integer_ | MaxRetries is the maximum number of parallel retries that are allowed<br />to the upstream cluster. If not specified, defaults to 3. |  | Minimum: 0 <br /> |


#### CommonAccessLogGrpcService



Common configuration for gRPC access logs.
Ref: https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/access_loggers/grpc/v3/als.proto#envoy-v3-api-msg-extensions-access-loggers-grpc-v3-commongrpcaccesslogconfig



_Appears in:_
- [AccessLogGrpcService](#accessloggrpcservice)
- [OpenTelemetryAccessLogService](#opentelemetryaccesslogservice)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `backendRef` _[BackendRef](https://gateway-api.sigs.k8s.io/reference/spec/#backendref)_ | The backend gRPC service. Can be any type of supported backend (Kubernetes Service, kgateway Backend, etc..) |  |  |
| `authority` _string_ | The :authority header in the grpc request. If this field is not set, the authority header value will be cluster_name.<br />Note that this authority does not override the SNI. The SNI is provided by the transport socket of the cluster. |  |  |
| `maxReceiveMessageLength` _integer_ | Maximum gRPC message size that is allowed to be received. If a message over this limit is received, the gRPC stream is terminated with the RESOURCE_EXHAUSTED error.<br />Defaults to 0, which means unlimited. |  | Minimum: 1 <br /> |
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
| `backendRef` _[BackendRef](https://gateway-api.sigs.k8s.io/reference/spec/#backendref)_ | The backend gRPC service. Can be any type of supported backend (Kubernetes Service, kgateway Backend, etc..) |  |  |
| `authority` _string_ | The :authority header in the grpc request. If this field is not set, the authority header value will be cluster_name.<br />Note that this authority does not override the SNI. The SNI is provided by the transport socket of the cluster. |  |  |
| `maxReceiveMessageLength` _integer_ | Maximum gRPC message size that is allowed to be received. If a message over this limit is received, the gRPC stream is terminated with the RESOURCE_EXHAUSTED error.<br />Defaults to 0, which means unlimited. |  | Minimum: 1 <br /> |
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
| `maxHeadersCount` _integer_ | Specifies the maximum number of headers that the connection will accept.<br />If not specified, the default of 100 is used. Requests that exceed this limit will receive<br />a 431 response for HTTP/1.x and cause a stream reset for HTTP/2. |  | Minimum: 0 <br /> |
| `maxStreamDuration` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | Total duration to keep alive an HTTP request/response stream. If the time limit is reached the stream will be<br />reset independent of any other timeouts. If not specified, this value is not set. |  |  |
| `maxRequestsPerConnection` _integer_ | Maximum requests for a single upstream connection.<br />If set to 0 or unspecified, defaults to unlimited. |  | Minimum: 0 <br /> |


#### ComparisonFilter

_Underlying type:_ _struct_

ComparisonFilter represents a filter based on a comparison.
Based on: https://www.envoyproxy.io/docs/envoy/v1.33.0/api-v3/config/accesslog/v3/accesslog.proto#config-accesslog-v3-comparisonfilter



_Appears in:_
- [DurationFilter](#durationfilter)
- [StatusCodeFilter](#statuscodefilter)



#### Cookie







_Appears in:_
- [HashPolicy](#hashpolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ | Name of the cookie. |  | MinLength: 1 <br /> |
| `path` _string_ | Path is the name of the path for the cookie. |  |  |
| `ttl` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | TTL specifies the time to live of the cookie.<br />If specified, a cookie with the TTL will be generated if the cookie is not present.<br />If the TTL is present and zero, the generated cookie will be a session cookie. |  |  |
| `secure` _boolean_ | Secure specifies whether the cookie is secure.<br />If true, the cookie will only be sent over HTTPS. |  |  |
| `httpOnly` _boolean_ | HttpOnly specifies whether the cookie is HTTP only, i.e. not accessible to JavaScript. |  |  |
| `sameSite` _string_ | SameSite controls cross-site sending of cookies.<br />Supported values are Strict, Lax, and None. |  | Enum: [Strict Lax None] <br /> |


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

_Underlying type:_ _struct_

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
| `componentLogLevels` _object (keys:string, values:string)_ | Envoy log levels for specific components. The keys are component names and<br />the values are one of "trace", "debug", "info", "warn", "error",<br />"critical", or "off", e.g.<br /><br />	```yaml<br />	componentLogLevels:<br />	  upstream: debug<br />	  connection: trace<br />	```<br /><br />These will be converted to the `--component-log-level` Envoy argument<br />value. See<br />https://www.envoyproxy.io/docs/envoy/latest/start/quick-start/run-envoy#debugging-envoy<br />for more information.<br /><br />Note: the keys and values cannot be empty, but they are not otherwise validated. |  |  |


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
| `extraVolumeMounts` _[VolumeMount](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#volumemount-v1-core) array_ | Additional volume mounts to add to the container. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#volumemount-v1-core<br />for details. |  |  |


#### EnvoyHealthCheck



EnvoyHealthCheck represents configuration for Envoy's health check filter.
The filter will be configured in No pass through mode, and will only match requests with the specified path.



_Appears in:_
- [HTTPListenerPolicySpec](#httplistenerpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `path` _string_ | Path defines the exact path that will be matched for health check requests. |  | MaxLength: 2048 <br />Pattern: `^/[-a-zA-Z0-9@:%.+~#?&/=_]+$` <br /> |


#### ExtAuthBufferSettings



ExtAuthBufferSettings configures how the request body should be buffered.



_Appears in:_
- [ExtAuthPolicy](#extauthpolicy)
- [ExtAuthProvider](#extauthprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `maxRequestBytes` _integer_ | MaxRequestBytes sets the maximum size of a message body to buffer.<br />Requests exceeding this size will receive HTTP 413 and not be sent to the auth service. |  | Minimum: 1 <br /> |
| `allowPartialMessage` _boolean_ | AllowPartialMessage determines if partial messages should be allowed.<br />When true, requests will be sent to the auth service even if they exceed maxRequestBytes.<br />The default behavior is false. | false |  |
| `packAsBytes` _boolean_ | PackAsBytes determines if the body should be sent as raw bytes.<br />When true, the body is sent as raw bytes in the raw_body field.<br />When false, the body is sent as UTF-8 string in the body field.<br />The default behavior is false. | false |  |


#### ExtAuthPolicy



ExtAuthPolicy configures external authentication/authorization for a route.
This policy will determine the ext auth server to use and how to talk to it.
Note that most of these fields are passed along as is to Envoy.
For more details on particular fields please see the Envoy ExtAuth documentation.
https://raw.githubusercontent.com/envoyproxy/envoy/f910f4abea24904aff04ec33a00147184ea7cffa/api/envoy/extensions/filters/http/ext_authz/v3/ext_authz.proto



_Appears in:_
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `extensionRef` _[NamespacedObjectReference](#namespacedobjectreference)_ | ExtensionRef references the GatewayExtension that should be used for auth. |  |  |
| `withRequestBody` _[ExtAuthBufferSettings](#extauthbuffersettings)_ | WithRequestBody allows the request body to be buffered and sent to the auth service.<br />Warning buffering has implications for streaming and therefore performance. |  |  |
| `contextExtensions` _object (keys:string, values:string)_ | Additional context for the auth service. |  |  |
| `disable` _[PolicyDisable](#policydisable)_ | Disable all external auth filters.<br />Can be used to disable external auth policies applied at a higher level in the config hierarchy. |  |  |


#### ExtAuthProvider



ExtAuthProvider defines the configuration for an ExtAuth provider.



_Appears in:_
- [GatewayExtensionSpec](#gatewayextensionspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `grpcService` _[ExtGrpcService](#extgrpcservice)_ | GrpcService is the GRPC service that will handle the auth. |  |  |
| `failOpen` _boolean_ | FailOpen determines if requests are allowed when the ext auth service is unavailable.<br />Defaults to false, meaning requests will be denied if the ext auth service is unavailable. | false |  |
| `clearRouteCache` _boolean_ | ClearRouteCache determines if the route cache should be cleared to allow the<br />external authentication service to correctly affect routing decisions. | false |  |
| `withRequestBody` _[ExtAuthBufferSettings](#extauthbuffersettings)_ | WithRequestBody allows the request body to be buffered and sent to the auth service.<br />Warning: buffering has implications for streaming and therefore performance. |  |  |
| `statusOnError` _integer_ | StatusOnError sets the HTTP status response code that is returned to the client when the<br />auth server returns an error or cannot be reached. Must be in the range of 100-511 inclusive.<br />The default matches the deny response code of 403 Forbidden. | 403 | Maximum: 511 <br />Minimum: 100 <br /> |
| `statPrefix` _string_ | StatPrefix is an optional prefix to include when emitting stats from the extauthz filter,<br />enabling different instances of the filter to have unique stats. |  | MinLength: 1 <br /> |


#### ExtGrpcService



ExtGrpcService defines the GRPC service that will handle the processing.



_Appears in:_
- [ExtAuthProvider](#extauthprovider)
- [ExtProcProvider](#extprocprovider)
- [RateLimitProvider](#ratelimitprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `backendRef` _[BackendRef](https://gateway-api.sigs.k8s.io/reference/spec/#backendref)_ | BackendRef references the backend GRPC service. |  |  |
| `authority` _string_ | Authority is the authority header to use for the GRPC service. |  |  |
| `requestTimeout` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | RequestTimeout is the timeout for the gRPC request. This is the timeout for a specific request. |  |  |
| `retry` _[GRPCRetryPolicy](#grpcretrypolicy)_ | Retry specifies the retry policy for gRPC streams associated with the service. |  |  |


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
| `failOpen` _boolean_ | FailOpen determines if requests are allowed when the ext proc service is unavailable.<br />Defaults to true, meaning requests are allowed upstream even if the ext proc service is unavailable. | true |  |
| `processingMode` _[ProcessingMode](#processingmode)_ | ProcessingMode defines how the filter should interact with the request/response streams. |  |  |
| `messageTimeout` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | MessageTimeout is the timeout for each message sent to the external processing server. |  |  |
| `maxMessageTimeout` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | MaxMessageTimeout specifies the upper bound of override_message_timeout that may be sent from the external processing server.<br />The default value 0, which effectively disables the override_message_timeout API. |  |  |
| `statPrefix` _string_ | StatPrefix is an optional prefix to include when emitting stats from the extproc filter,<br />enabling different instances of the filter to have unique stats. |  | MinLength: 1 <br /> |
| `routeCacheAction` _[ExtProcRouteCacheAction](#extprocroutecacheaction)_ | RouteCacheAction describes the route cache action to be taken when an<br />external processor response is received in response to request headers.<br />The default behavior is "FromResponse" which will only clear the route cache when<br />an external processing response has the clear_route_cache field set. | FromResponse | Enum: [FromResponse Clear Retain] <br /> |
| `metadataOptions` _[MetadataOptions](#metadataoptions)_ | MetadataOptions allows configuring metadata namespaces to forwarded or received from the external<br />processing server. |  |  |


#### ExtProcRouteCacheAction

_Underlying type:_ _string_





_Appears in:_
- [ExtProcProvider](#extprocprovider)

| Field | Description |
| --- | --- |
| `FromResponse` | RouteCacheActionFromResponse is the default behavior, which clears the route cache only<br />when the clear_route_cache field is set in an external processor response.<br /> |
| `Clear` | RouteCacheActionClear always clears the route cache irrespective of the<br />clear_route_cache field in the external processor response.<br /> |
| `Retain` | RouteCacheActionRetain never clears the route cache irrespective of the<br />clear_route_cache field in the external processor response.<br /> |


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


#### FrontendHTTP







_Appears in:_
- [AgentgatewayPolicyFrontend](#agentgatewaypolicyfrontend)

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
- [AgentgatewayPolicyFrontend](#agentgatewaypolicyfrontend)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `keepalive` _[AgentgatewayKeepalive](#agentgatewaykeepalive)_ | keepalive defines settings for enabling TCP keepalives on the connection. |  |  |


#### FrontendTLS







_Appears in:_
- [AgentgatewayPolicyFrontend](#agentgatewaypolicyfrontend)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `handshakeTimeout` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | handshakeTimeout specifies the deadline for a TLS handshake to complete.<br />If unset, this defaults to 15s. |  |  |
| `alpnProtocols` _string_ | alpnProtocols sets the Application Level Protocol Negotiation (ALPN) value to use in the TLS handshake.<br /><br />If not present, defaults to ["h2", "http/1.1"]. |  | MaxItems: 16 <br />MinItems: 1 <br /> |


#### GRPCRetryBackoff







_Appears in:_
- [GRPCRetryPolicy](#grpcretrypolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `baseInterval` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | BaseInterval specifies the base interval used with a fully jittered exponential back-off between retries. |  |  |
| `maxInterval` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | MaxInterval specifies the maximum interval between retry attempts.<br />Defaults to 10 times the BaseInterval if not set. |  |  |


#### GRPCRetryPolicy







_Appears in:_
- [ExtGrpcService](#extgrpcservice)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `attempts` _integer_ | Attempts specifies the number of retry attempts for a request.<br />Defaults to 1 attempt if not set.<br />A value of 0 effectively disables retries. | 1 | Minimum: 0 <br /> |
| `backoff` _[GRPCRetryBackoff](#grpcretrybackoff)_ | Backoff specifies the retry backoff strategy.<br />If not set, a default backoff with a base interval of 1000ms is used. The default max interval is 10 times the base interval. |  |  |


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
| `type` _[GatewayExtensionType](#gatewayextensiontype)_ | Deprecated: Setting this field has no effect.<br />Type indicates the type of the GatewayExtension to be used. |  | Enum: [ExtAuth ExtProc RateLimit JWTProviders] <br /> |
| `extAuth` _[ExtAuthProvider](#extauthprovider)_ | ExtAuth configuration for ExtAuth extension type. |  |  |
| `extProc` _[ExtProcProvider](#extprocprovider)_ | ExtProc configuration for ExtProc extension type. |  |  |
| `rateLimit` _[RateLimitProvider](#ratelimitprovider)_ | RateLimit configuration for RateLimit extension type. |  |  |
| `jwtProviders` _[NamedJWTProvider](#namedjwtprovider) array_ | JWTProviders configures named JWT providers.<br />If multiple providers are specified for a given JWT policy,<br />the providers will be `OR`-ed together and will allow validation to any of the providers. |  | MaxItems: 32 <br /> |


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
| `JWTProviders` | GatewayExtensionTypeJWTProvider is the type for the JWT Provider extensions<br /> |


#### GatewayParameters



A GatewayParameters contains configuration that is used to dynamically
provision kgateway's data plane (Envoy or agentgateway proxy instance), based on a
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
- [LLMProvider](#llmprovider)
- [NamedLLMProvider](#namedllmprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `model` _string_ | Optional: Override the model name, such as `gemini-2.5-pro`.<br />If unset, the model name is taken from the request. |  |  |


#### GracefulShutdownSpec







_Appears in:_
- [Pod](#pod)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `enabled` _boolean_ | Enable grace period before shutdown to finish current requests while Envoy health checks fail to e.g. notify external load balancers. *NOTE:* This will not have any effect if you have not defined health checks via the health check filter |  |  |
| `sleepTimeSeconds` _integer_ | Time (in seconds) for the preStop hook to wait before allowing Envoy to terminate |  | Maximum: 3.1536e+07 <br />Minimum: 0 <br /> |




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


#### HTTPVersion

_Underlying type:_ _string_





_Appears in:_
- [BackendHTTP](#backendhttp)

| Field | Description |
| --- | --- |
| `HTTP1` |  |
| `HTTP2` |  |


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







_Appears in:_
- [HashPolicy](#hashpolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ | Name is the name of the header to use as a component of the hash key. |  | MinLength: 1 <br /> |


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
- [AgentgatewayPolicyTraffic](#agentgatewaypolicytraffic)
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `request` _[HTTPHeaderFilter](#httpheaderfilter)_ | Request modifies request headers. |  |  |
| `response` _[HTTPHeaderFilter](#httpheaderfilter)_ | Response modifies response headers. |  |  |


#### HeaderName

_Underlying type:_ _string_





_Appears in:_
- [HeaderTransformation](#headertransformation)



#### HeaderSource



HeaderSource configures how to retrieve a JWT from a header



_Appears in:_
- [JWTTokenSource](#jwttokensource)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `header` _string_ | Header is the name of the header. for example, "Authorization" |  | MaxLength: 2048 <br />MinLength: 1 <br /> |
| `prefix` _string_ | Prefix before the token. for example, "Bearer " |  | MaxLength: 2048 <br />MinLength: 1 <br /> |


#### HeaderTransformation







_Appears in:_
- [Transform](#transform)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _[HeaderName](#headername)_ | Name is the name of the header to interact with. |  |  |
| `value` _[InjaTemplate](#injatemplate)_ | Value is the Inja template to apply to generate the output value for the header. |  |  |


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







_Appears in:_
- [BackendConfigPolicySpec](#backendconfigpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `timeout` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | Timeout is time to wait for a health check response. If the timeout is reached the<br />health check attempt will be considered a failure. |  |  |
| `interval` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | Interval is the time between health checks. |  |  |
| `unhealthyThreshold` _integer_ | UnhealthyThreshold is the number of consecutive failed health checks that will be considered<br />unhealthy.<br />Note that for HTTP health checks, if a host responds with a code not in ExpectedStatuses or RetriableStatuses,<br />this threshold is ignored and the host is considered immediately unhealthy. |  | Minimum: 0 <br /> |
| `healthyThreshold` _integer_ | HealthyThreshold is the number of healthy health checks required before a host is marked<br />healthy. Note that during startup, only a single successful health check is<br />required to mark a host healthy. |  | Minimum: 0 <br /> |
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
- [StaticBackend](#staticbackend)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `host` _string_ | Host is the host name to use for the backend. |  | MinLength: 1 <br /> |
| `port` _integer_ | Port is the port to use for the backend. |  |  |


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
| `maxConcurrentStreams` _integer_ | The maximum number of concurrent streams that the connection can have. |  | Minimum: 0 <br /> |
| `overrideStreamErrorOnInvalidHttpMessage` _boolean_ | Allows invalid HTTP messaging and headers. When disabled (default), then<br />the whole HTTP/2 connection is terminated upon receiving invalid HEADERS frame.<br />When enabled, only the offending stream is terminated. |  |  |


#### Image



A container image. See https://kubernetes.io/docs/concepts/containers/images
for details.



_Appears in:_
- [Agentgateway](#agentgateway)
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



#### InsecureTLSMode

_Underlying type:_ _string_





_Appears in:_
- [BackendTLS](#backendtls)

| Field | Description |
| --- | --- |
| `All` | InsecureTLSModeInsecure disables all TLS verification<br /> |
| `Hostname` | InsecureTLSModeHostname enables verifying the CA certificate, but disables verification of the hostname/SAN.<br />Note this is still, generally, very "insecure" as the name suggests.<br /> |


#### IstioContainer



IstioContainer configures the container running the istio-proxy.



_Appears in:_
- [IstioIntegration](#istiointegration)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `image` _[Image](#image)_ | The container image. See<br />https://kubernetes.io/docs/concepts/containers/images<br />for details. |  |  |
| `securityContext` _[SecurityContext](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#securitycontext-v1-core)_ | The security context for this container. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#securitycontext-v1-core<br />for details. |  |  |
| `resources` _[ResourceRequirements](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#resourcerequirements-v1-core)_ | The compute resources required by this container. See<br />https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/<br />for details. |  |  |
| `logLevel` _string_ | Log level for istio-proxy. Options include "info", "debug", "warning", and "error".<br />Default level is info Default is "warning". |  |  |
| `istioDiscoveryAddress` _string_ | The address of the istio discovery service. Defaults to "istiod.istio-system.svc:15012". |  |  |
| `istioMetaMeshId` _string_ | The mesh id of the istio mesh. Defaults to "cluster.local". |  |  |
| `istioMetaClusterId` _string_ | The cluster id of the istio cluster. Defaults to "Kubernetes". |  |  |


#### IstioIntegration



IstioIntegration configures the Istio integration settings used by kgateway's data plane



_Appears in:_
- [KubernetesProxyConfig](#kubernetesproxyconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `istioProxyContainer` _[IstioContainer](#istiocontainer)_ | Configuration for the container running istio-proxy.<br />Note that if Istio integration is not enabled, the istio container will not be injected<br />into the gateway proxy deployment. |  |  |
| `customSidecars` _[Container](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#container-v1-core) array_ | do not use slice of pointers: https://github.com/kubernetes/code-generator/issues/166<br />Override the default Istio sidecar in gateway-proxy with a custom container. |  |  |


#### JWKS



JWKS (JSON Web Key Set) configures the source for the JWKS
Exactly one of LocalJWKS or RemoteJWKS must be specified.



_Appears in:_
- [JWTProvider](#jwtprovider)
- [NamedJWTProvider](#namedjwtprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `local` _[LocalJWKS](#localjwks)_ | LocalJWKS configures getting the public keys to validate the JWT from a Kubernetes configmap,<br />or inline (raw string) JWKS. |  |  |
| `remote` _[RemoteJWKS](#remotejwks)_ | RemoteJWKS configures getting the public keys to validate the JWT from a remote JWKS server. |  |  |


#### JWTAuthentication



JWTAuthentication defines the providers used to configure JWT authentication



_Appears in:_
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `extensionRef` _[NamespacedObjectReference](#namespacedobjectreference)_ | ExtensionRef references a GatewayExtension that provides the jwt providers |  |  |
| `disable` _[PolicyDisable](#policydisable)_ | Disable all JWT filters.<br />Can be used to disable JWT policies applied at a higher level in the config hierarchy. |  |  |


#### JWTAuthenticationMode

_Underlying type:_ _string_



_Validation:_
- Enum: [Strict Optional Permissive]

_Appears in:_
- [AgentJWTAuthentication](#agentjwtauthentication)

| Field | Description |
| --- | --- |
| `Strict` | A valid token, issued by a configured issuer, must be present.<br />This is the default option.<br /> |
| `Optional` | If a token exists, validate it.<br />Warning: this allows requests without a JWT token!<br /> |
| `Permissive` | Requests are never rejected. This is useful for usage of claims in later steps (authorization, logging, etc).<br />Warning: this allows requests without a JWT token!<br /> |


#### JWTClaimToHeader



JWTClaimToHeader allows copying verified claims to headers sent upstream



_Appears in:_
- [JWTProvider](#jwtprovider)
- [NamedJWTProvider](#namedjwtprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ | Name is the JWT claim name, for example, "sub". |  | MaxLength: 2048 <br />MinLength: 1 <br /> |
| `header` _string_ | Header is the header the claim will be copied to, for example, "x-sub". |  | MaxLength: 2048 <br />MinLength: 1 <br /> |


#### JWTProvider



JWTProvider configures the JWT Provider
If multiple providers are specified for a given JWT policy, the providers will be `OR`-ed together and will allow validation to any of the providers.



_Appears in:_
- [NamedJWTProvider](#namedjwtprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `issuer` _string_ | Issuer of the JWT. the 'iss' claim of the JWT must match this. |  | MaxLength: 2048 <br /> |
| `audiences` _string array_ | Audiences is the list of audiences to be used for the JWT provider.<br />If specified an incoming JWT must have an 'aud' claim, and it must be in this list.<br />If not specified, the audiences will not be checked in the token. |  | MaxItems: 32 <br />MinItems: 1 <br /> |
| `tokenSource` _[JWTTokenSource](#jwttokensource)_ | TokenSource configures where to find the JWT of the current provider. |  |  |
| `claimsToHeaders` _[JWTClaimToHeader](#jwtclaimtoheader) array_ | ClaimsToHeaders is the list of claims to headers to be used for the JWT provider.<br />Optionally set the claims from the JWT payload that you want to extract and add as headers<br />to the request before the request is forwarded to the upstream destination.<br />Note: if ClaimsToHeaders is set, the Envoy route cache will be cleared.<br />This allows the JWT filter to correctly affect routing decisions. |  | MaxItems: 32 <br />MinItems: 1 <br /> |
| `jwks` _[JWKS](#jwks)_ | JWKS is the source for the JSON Web Keys to be used to validate the JWT. |  |  |
| `forwardToken` _boolean_ | ForwardToken configures if the JWT token is forwarded to the upstream backend.<br />If true, the header containing the token will be forwarded upstream.<br />If false or not set, the header containing the token will be removed. |  |  |


#### JWTTokenSource



JWTTokenSource configures the source for the JWTToken
Exactly one of HeaderSource or QueryParameter must be specified.



_Appears in:_
- [JWTProvider](#jwtprovider)
- [NamedJWTProvider](#namedjwtprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `header` _[HeaderSource](#headersource)_ | HeaderSource configures retrieving token from a header |  |  |
| `queryParameter` _string_ | QueryParameter configures retrieving token from the query parameter |  |  |




#### KubernetesProxyConfig



KubernetesProxyConfig configures the set of Kubernetes resources that will be provisioned
for a given Gateway.



_Appears in:_
- [GatewayParametersSpec](#gatewayparametersspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `deployment` _[ProxyDeployment](#proxydeployment)_ | Use a Kubernetes deployment as the proxy workload type. Currently, this is the only<br />supported workload type. |  |  |
| `envoyContainer` _[EnvoyContainer](#envoycontainer)_ | Configuration for the container running Envoy.<br />If agentgateway is enabled, the EnvoyContainer values will be ignored. |  |  |
| `sdsContainer` _[SdsContainer](#sdscontainer)_ | Configuration for the container running the Secret Discovery Service (SDS). |  |  |
| `podTemplate` _[Pod](#pod)_ | Configuration for the pods that will be created. |  |  |
| `service` _[Service](#service)_ | Configuration for the Kubernetes Service that exposes the proxy over<br />the network. |  |  |
| `serviceAccount` _[ServiceAccount](#serviceaccount)_ | Configuration for the Kubernetes ServiceAccount used by the proxy pods. |  |  |
| `istio` _[IstioIntegration](#istiointegration)_ | Configuration for the Istio integration. |  |  |
| `stats` _[StatsConfig](#statsconfig)_ | Configuration for the stats server. |  |  |
| `agentgateway` _[Agentgateway](#agentgateway)_ | Configure the agentgateway integration. If agentgateway is disabled, the<br />EnvoyContainer values will be used by default to configure the data<br />plane proxy. |  |  |
| `omitDefaultSecurityContext` _boolean_ | OmitDefaultSecurityContext is used to control whether or not<br />`securityContext` fields should be rendered for the various generated<br />Deployments/Containers that are dynamically provisioned by the deployer.<br /><br />When set to true, no `securityContexts` will be provided and will left<br />to the user/platform to be provided.<br /><br />This should be enabled on platforms such as Red Hat OpenShift where the<br />`securityContext` will be dynamically added to enforce the appropriate<br />level of security. |  |  |


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


#### ListenerPolicy



ListenerPolicy is used for configuring Envoy listener-level settings that apply to all protocol types (HTTP, HTTPS, TCP, TLS).
These policies can only target `Gateway` objects.





| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `gateway.kgateway.dev/v1alpha1` | | |
| `kind` _string_ | `ListenerPolicy` | | |
| `kind` _string_ | Kind is a string value representing the REST resource this object represents.<br />Servers may infer this from the endpoint the client submits requests to.<br />Cannot be updated.<br />In CamelCase.<br />More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds |  |  |
| `apiVersion` _string_ | APIVersion defines the versioned schema of this representation of an object.<br />Servers should convert recognized schemas to the latest internal value, and<br />may reject unrecognized values.<br />More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources |  |  |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[ListenerPolicySpec](#listenerpolicyspec)_ |  |  |  |
| `status` _[PolicyStatus](#policystatus)_ |  |  |  |


#### ListenerPolicySpec



ListenerPolicySpec defines the desired state of a listener policy.



_Appears in:_
- [ListenerPolicy](#listenerpolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `targetRefs` _[LocalPolicyTargetReference](#localpolicytargetreference) array_ | TargetRefs specifies the target resources by reference to attach the policy to.<br />Only supports `Gateway` resources |  | MaxItems: 16 <br />MinItems: 1 <br /> |
| `targetSelectors` _[LocalPolicyTargetSelector](#localpolicytargetselector) array_ | TargetSelectors specifies the target selectors to select `Gateway` resources to attach the policy to. |  |  |
| `proxyProtocol` _[ProxyProtocolConfig](#proxyprotocolconfig)_ | ProxyProtocol configures the PROXY protocol listener filter.<br />When set, Envoy will expect connections to include the PROXY protocol header.<br />This is commonly used when kgateway is behind a load balancer that preserves client IP information.<br />See here for more information: https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/filters/listener/proxy_protocol/v3/proxy_protocol.proto |  |  |


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
| `choiceCount` _integer_ | How many choices to take into account.<br />Defaults to 2. | 2 |  |
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
| `minimumRingSize` _integer_ | MinimumRingSize is the minimum size of the ring. |  | Minimum: 0 <br /> |
| `maximumRingSize` _integer_ | MaximumRingSize is the maximum size of the ring. |  | Minimum: 0 <br /> |
| `useHostnameForHashing` _boolean_ | UseHostnameForHashing specifies whether to use the hostname instead of the resolved IP address for hashing.<br />Defaults to false. |  |  |
| `hashPolicies` _[HashPolicy](#hashpolicy) array_ | HashPolicies specifies the hash policies for hashing load balancers (RingHash, Maglev). |  | MaxItems: 16 <br />MinItems: 1 <br /> |


#### LoadBalancerRoundRobinConfig



LoadBalancerRoundRobinConfig configures the round robin load balancer type.



_Appears in:_
- [LoadBalancer](#loadbalancer)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `slowStart` _[SlowStart](#slowstart)_ | SlowStart configures the slow start configuration for the load balancer. |  |  |


#### LocalJWKS



LocalJWKS configures getting the public keys to validate the JWT from a Kubernetes ConfigMap,
or inline (raw string) JWKS.



_Appears in:_
- [JWKS](#jwks)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `inline` _string_ | Inline is the JWKS as the raw, inline JWKS string<br />This can be an individual key, a key set or a pem block public key |  | MaxLength: 16384 <br />MinLength: 1 <br /> |
| `configMapRef` _[LocalObjectReference](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#localobjectreference-v1-core)_ | ConfigMapRef configures storing the JWK in a Kubernetes ConfigMap in the same namespace as the GatewayExtension.<br />The ConfigMap must have a data key named 'jwks' that contains the JWKS. |  |  |


#### LocalPolicyTargetReference



Select the object to attach the policy by Group, Kind, and Name.
The object must be in the same namespace as the policy.
You can target only one object at a time.



_Appears in:_
- [BackendConfigPolicySpec](#backendconfigpolicyspec)
- [HTTPListenerPolicySpec](#httplistenerpolicyspec)
- [ListenerPolicySpec](#listenerpolicyspec)
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
- [AgentgatewayPolicySpec](#agentgatewaypolicyspec)
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `group` _[Group](#group)_ | The API group of the target resource.<br />For Kubernetes Gateway API resources, the group is `gateway.networking.k8s.io`. |  |  |
| `kind` _[Kind](#kind)_ | The API kind of the target resource,<br />such as Gateway or HTTPRoute. |  |  |
| `name` _[ObjectName](#objectname)_ | The name of the target resource. |  |  |
| `sectionName` _[SectionName](#sectionname)_ | The section name of the target resource. |  |  |


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
- [ListenerPolicySpec](#listenerpolicyspec)
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
- [AgentgatewayPolicySpec](#agentgatewaypolicyspec)
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `group` _[Group](#group)_ | The API group of the target resource.<br />For Kubernetes Gateway API resources, the group is `gateway.networking.k8s.io`. |  |  |
| `kind` _[Kind](#kind)_ | The API kind of the target resource,<br />such as Gateway or HTTPRoute. |  |  |
| `matchLabels` _object (keys:string, values:string)_ | Label selector to select the target resource. |  |  |
| `sectionName` _[SectionName](#sectionname)_ | The section name of the target resource. |  |  |


#### LocalRateLimitPolicy



LocalRateLimitPolicy represents a policy for local rate limiting.
It defines the configuration for rate limiting using a token bucket mechanism.



_Appears in:_
- [RateLimit](#ratelimit)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `tokenBucket` _[TokenBucket](#tokenbucket)_ | TokenBucket represents the configuration for a token bucket local rate-limiting mechanism.<br />It defines the parameters for controlling the rate at which requests are allowed. |  |  |


#### LocalRateLimitUnit

_Underlying type:_ _string_





_Appears in:_
- [AgentLocalRateLimitPolicy](#agentlocalratelimitpolicy)

| Field | Description |
| --- | --- |
| `Seconds` |  |
| `Minutes` |  |
| `Hours` |  |


#### LocalityType

_Underlying type:_ _string_





_Appears in:_
- [LoadBalancer](#loadbalancer)

| Field | Description |
| --- | --- |
| `WeightedLb` | https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/locality_weight#locality-weighted-load-balancing<br />Locality weighted load balancing enables weighting assignments across different zones and geographical locations by using explicit weights.<br />This field is required to enable locality weighted load balancing.<br /> |


#### MCPAuthentication







_Appears in:_
- [BackendMCP](#backendmcp)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `resourceMetadata` _object (keys:string, values:[JSON](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#json-v1-apiextensions-k8s-io))_ | ResourceMetadata defines the metadata to use for MCP resources. |  |  |
| `provider` _[McpIDP](#mcpidp)_ | McpIDP specifies the identity provider to use for authentication |  | Enum: [Auth0 Keycloak] <br /> |
| `issuer` _string_ | Issuer identifies the IdP that issued the JWT. This corresponds to the 'iss' claim (https://tools.ietf.org/html/rfc7519#section-4.1.1). |  |  |
| `audiences` _string array_ | audiences specify the list of allowed audiences that are allowed access. This corresponds to the 'aud' claim (https://datatracker.ietf.org/doc/html/rfc7519#section-4.1.3).<br />If unset, any audience is allowed. |  | MaxItems: 64 <br />MinItems: 1 <br /> |
| `jwks` _[AgentRemoteJWKS](#agentremotejwks)_ | jwks defines the remote JSON Web Key used to validate the signature of the JWT. |  |  |


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
| `policies` _[AgentgatewayPolicyBackendMCP](#agentgatewaypolicybackendmcp)_ | policies controls policies for communicating with this backend. Policies may also be set in AgentgatewayPolicy, or<br />in the top level AgentgatewayBackend. Policies are merged on a field-level basis, with order: AgentgatewayPolicy <<br />AgentgatewayBackend < AgentgatewayBackend MCP (this field). |  |  |


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


#### MetadataNamespaces



MetadataNamespaces configures which metadata namespaces to use.
See [envoy docs](https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/filters/http/ext_proc/v3/ext_proc.proto#envoy-v3-api-msg-extensions-filters-http-ext-proc-v3-metadataoptions-metadatanamespaces)
for specifics.



_Appears in:_
- [MetadataOptions](#metadataoptions)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `typed` _string array_ |  |  | MinItems: 1 <br /> |
| `untyped` _string array_ |  |  | MinItems: 1 <br /> |


#### MetadataOptions



MetadataOptions allows configuring metadata namespaces to forward or receive from the external
processing server.



_Appears in:_
- [ExtProcProvider](#extprocprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `forwarding` _[MetadataNamespaces](#metadatanamespaces)_ | Forwarding defines the typed or untyped dynamic metadata namespaces to forward to the external processing server. |  |  |


#### MetadataPathSegment

_Underlying type:_ _struct_

Specifies a segment in a path for retrieving values from Metadata.



_Appears in:_
- [MetadataKey](#metadatakey)



#### NamedJWTProvider



NamedJWTProvider is a named JWT provider entry.



_Appears in:_
- [GatewayExtensionSpec](#gatewayextensionspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ | Name is the unique name of the JWT provider. |  | MaxLength: 253 <br />MinLength: 1 <br /> |
| `issuer` _string_ | Issuer of the JWT. the 'iss' claim of the JWT must match this. |  | MaxLength: 2048 <br /> |
| `audiences` _string array_ | Audiences is the list of audiences to be used for the JWT provider.<br />If specified an incoming JWT must have an 'aud' claim, and it must be in this list.<br />If not specified, the audiences will not be checked in the token. |  | MaxItems: 32 <br />MinItems: 1 <br /> |
| `tokenSource` _[JWTTokenSource](#jwttokensource)_ | TokenSource configures where to find the JWT of the current provider. |  |  |
| `claimsToHeaders` _[JWTClaimToHeader](#jwtclaimtoheader) array_ | ClaimsToHeaders is the list of claims to headers to be used for the JWT provider.<br />Optionally set the claims from the JWT payload that you want to extract and add as headers<br />to the request before the request is forwarded to the upstream destination.<br />Note: if ClaimsToHeaders is set, the Envoy route cache will be cleared.<br />This allows the JWT filter to correctly affect routing decisions. |  | MaxItems: 32 <br />MinItems: 1 <br /> |
| `jwks` _[JWKS](#jwks)_ | JWKS is the source for the JSON Web Keys to be used to validate the JWT. |  |  |
| `forwardToken` _boolean_ | ForwardToken configures if the JWT token is forwarded to the upstream backend.<br />If true, the header containing the token will be forwarded upstream.<br />If false or not set, the header containing the token will be removed. |  |  |


#### NamedLLMProvider







_Appears in:_
- [PriorityGroup](#prioritygroup)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _[SectionName](#sectionname)_ | Name of the provider. Policies can target this provider by name. |  |  |
| `policies` _[AgentgatewayPolicyBackendAI](#agentgatewaypolicybackendai)_ | policies controls policies for communicating with this backend. Policies may also be set in AgentgatewayPolicy, or<br />in the top level AgentgatewayBackend. policies are merged on a field-level basis, with order: AgentgatewayPolicy <<br />AgentgatewayBackend < AgentgatewayBackend LLM provider (this field). |  |  |
| `openai` _[OpenAIConfig](#openaiconfig)_ | OpenAI provider |  |  |
| `azureopenai` _[AzureOpenAIConfig](#azureopenaiconfig)_ | Azure OpenAI provider |  |  |
| `anthropic` _[AnthropicConfig](#anthropicconfig)_ | Anthropic provider |  |  |
| `gemini` _[GeminiConfig](#geminiconfig)_ | Gemini provider |  |  |
| `vertexai` _[VertexAIConfig](#vertexaiconfig)_ | Vertex AI provider |  |  |
| `bedrock` _[BedrockConfig](#bedrockconfig)_ | Bedrock provider |  |  |
| `host` _string_ | Host specifies the hostname to send the requests to.<br />If not specified, the default hostname for the provider is used. |  |  |
| `port` _integer_ | Port specifies the port to send the requests to. |  | Maximum: 65535 <br />Minimum: 1 <br /> |
| `path` _string_ | Path specifies the URL path to use for the LLM provider API requests.<br />This is useful when you need to route requests to a different API endpoint while maintaining<br />compatibility with the original provider's API structure.<br />If not specified, the default path for the provider is used. |  |  |


#### NamespacedObjectReference



Select the object by Name and Namespace.
You can target only one object at a time.



_Appears in:_
- [ExtAuthPolicy](#extauthpolicy)
- [ExtProcPolicy](#extprocpolicy)
- [JWTAuthentication](#jwtauthentication)
- [RateLimitPolicy](#ratelimitpolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _[ObjectName](#objectname)_ | The name of the target resource. |  |  |
| `namespace` _[Namespace](#namespace)_ | The namespace of the target resource.<br />If not set, defaults to the namespace of the parent object. |  | MaxLength: 63 <br />MinLength: 1 <br />Pattern: `^[a-z0-9]([-a-z0-9]*[a-z0-9])?$` <br /> |




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
| `policies` _[AgentgatewayPolicyBackendSimple](#agentgatewaypolicybackendsimple)_ | policies controls policies for communicating with OpenAI. |  |  |


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







_Appears in:_
- [BackendConfigPolicySpec](#backendconfigpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `consecutive5xx` _integer_ | The number of consecutive server-side error responses (for HTTP traffic,<br />5xx responses; for TCP traffic, connection failures; etc.) before an<br />ejection occurs. Defaults to 5. If this is zero, consecutive 5xx passive<br />health checks will be disabled. In the future, other types of passive<br />health checking might be added, but none will be enabled by default. | 5 | Minimum: 0 <br /> |
| `interval` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | The time interval between ejection analysis sweeps. This can result in<br />both new ejections as well as hosts being returned to service. Defaults<br />to 10s. | 10s |  |
| `baseEjectionTime` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | The base time that a host is ejected for. The real time is equal to the<br />base time multiplied by the number of times the host has been ejected.<br />Defaults to 30s. | 30s |  |
| `maxEjectionPercent` _integer_ | The maximum % of an upstream cluster that can be ejected due to outlier<br />detection. Defaults to 10%. | 10 | Maximum: 100 <br />Minimum: 0 <br /> |


#### Pod



Configuration for a Kubernetes Pod template.



_Appears in:_
- [KubernetesProxyConfig](#kubernetesproxyconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `extraLabels` _object (keys:string, values:string)_ | Additional labels to add to the Pod object metadata.<br />If the same label is present on `Gateway.spec.infrastructure.labels`, the `Gateway` takes precedence. |  |  |
| `extraAnnotations` _object (keys:string, values:string)_ | Additional annotations to add to the Pod object metadata.<br />If the same annotation is present on `Gateway.spec.infrastructure.annotations`, the `Gateway` takes precedence. |  |  |
| `securityContext` _[PodSecurityContext](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#podsecuritycontext-v1-core)_ | The pod security context. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#podsecuritycontext-v1-core<br />for details. |  |  |
| `imagePullSecrets` _[LocalObjectReference](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#localobjectreference-v1-core) array_ | An optional list of references to secrets in the same namespace to use for<br />pulling any of the images used by this Pod spec. See<br />https://kubernetes.io/docs/concepts/containers/images/#specifying-imagepullsecrets-on-a-pod<br />for details. |  |  |
| `nodeSelector` _object (keys:string, values:string)_ | A selector which must be true for the pod to fit on a node. See<br />https://kubernetes.io/docs/concepts/configuration/assign-pod-node/ for<br />details. |  |  |
| `affinity` _[Affinity](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#affinity-v1-core)_ | If specified, the pod's scheduling constraints. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#affinity-v1-core<br />for details. |  |  |
| `tolerations` _[Toleration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#toleration-v1-core) array_ | do not use slice of pointers: https://github.com/kubernetes/code-generator/issues/166<br />If specified, the pod's tolerations. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#toleration-v1-core<br />for details. |  |  |
| `gracefulShutdown` _[GracefulShutdownSpec](#gracefulshutdownspec)_ | If specified, the pod's graceful shutdown spec. |  |  |
| `terminationGracePeriodSeconds` _integer_ | If specified, the pod's termination grace period in seconds. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#pod-v1-core<br />for details |  | Maximum: 3.1536e+07 <br />Minimum: 0 <br /> |
| `startupProbe` _[Probe](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#probe-v1-core)_ | If specified, the pod's startup probe. A probe of container startup readiness.<br />Container will be only be added to service endpoints if the probe succeeds. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#probe-v1-core<br />for details. |  |  |
| `readinessProbe` _[Probe](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#probe-v1-core)_ | If specified, the pod's readiness probe. Periodic probe of container service readiness.<br />Container will be removed from service endpoints if the probe fails. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#probe-v1-core<br />for details. |  |  |
| `livenessProbe` _[Probe](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#probe-v1-core)_ | If specified, the pod's liveness probe. Periodic probe of container service readiness.<br />Container will be restarted if the probe fails. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#probe-v1-core<br />for details. |  |  |
| `topologySpreadConstraints` _[TopologySpreadConstraint](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#topologyspreadconstraint-v1-core) array_ | If specified, the pod's topology spread constraints. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#topologyspreadconstraint-v1-core<br />for details. |  |  |
| `extraVolumes` _[Volume](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#volume-v1-core) array_ | Additional volumes to add to the pod. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#volume-v1-core<br />for details. |  |  |
| `priorityClassName` _string_ | If specified, the pod's PriorityClass. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#podspec-v1-core<br />for details |  |  |


#### PolicyAncestorStatus







_Appears in:_
- [PolicyStatus](#policystatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `ancestorRef` _[ParentReference](https://gateway-api.sigs.k8s.io/reference/spec/#parentreference)_ | AncestorRef corresponds with a ParentRef in the spec that this<br />PolicyAncestorStatus struct describes the status of. |  |  |
| `controllerName` _string_ | ControllerName is a domain/path string that indicates the name of the<br />controller that wrote this status. This corresponds with the<br />controllerName field on GatewayClass.<br /><br />Example: "example.net/gateway-controller".<br /><br />The format of this field is DOMAIN "/" PATH, where DOMAIN and PATH are<br />valid Kubernetes names<br />(https://kubernetes.io/docs/concepts/overview/working-with-objects/names/#names).<br /><br />Controllers MUST populate this field when writing status. Controllers should ensure that<br />entries to status populated with their ControllerName are cleaned up when they are no<br />longer necessary. |  |  |
| `conditions` _[Condition](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#condition-v1-meta) array_ | Conditions describes the status of the Policy with respect to the given Ancestor. |  | MaxItems: 8 <br />MinItems: 1 <br /> |






#### PolicyDisable



PolicyDisable is used to disable a policy.



_Appears in:_
- [Buffer](#buffer)
- [CorsPolicy](#corspolicy)
- [ExtAuthPolicy](#extauthpolicy)
- [ExtProcPolicy](#extprocpolicy)
- [JWTAuthentication](#jwtauthentication)



#### PolicyPhase

_Underlying type:_ _string_



_Validation:_
- Enum: [PreRouting PostRouting]

_Appears in:_
- [AgentgatewayPolicyTraffic](#agentgatewaypolicytraffic)

| Field | Description |
| --- | --- |
| `PreRouting` |  |
| `PostRouting` |  |




#### Port







_Appears in:_
- [Service](#service)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `port` _integer_ | The port number to match on the Gateway |  | Maximum: 65535 <br />Minimum: 1 <br /> |
| `nodePort` _integer_ | The NodePort to be used for the service. If not specified, a random port<br />will be assigned by the Kubernetes API server. |  | Maximum: 65535 <br />Minimum: 1 <br /> |


#### PriorityGroup







_Appears in:_
- [AIBackend](#aibackend)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `providers` _[NamedLLMProvider](#namedllmprovider) array_ | providers specifies a list of LLM providers within this group. Each provider is treated equally in terms of priority,<br />with automatic weighting based on health. |  | MaxItems: 32 <br />MinItems: 1 <br /> |


#### ProcessingMode



ProcessingMode defines how the filter should interact with the request/response streams



_Appears in:_
- [ExtProcPolicy](#extprocpolicy)
- [ExtProcProvider](#extprocprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `requestHeaderMode` _string_ | RequestHeaderMode determines how to handle the request headers | SEND | Enum: [DEFAULT SEND SKIP] <br /> |
| `responseHeaderMode` _string_ | ResponseHeaderMode determines how to handle the response headers | SEND | Enum: [DEFAULT SEND SKIP] <br /> |
| `requestBodyMode` _string_ | RequestBodyMode determines how to handle the request body | NONE | Enum: [NONE STREAMED BUFFERED BUFFERED_PARTIAL FULL_DUPLEX_STREAMED] <br /> |
| `responseBodyMode` _string_ | ResponseBodyMode determines how to handle the response body | NONE | Enum: [NONE STREAMED BUFFERED BUFFERED_PARTIAL FULL_DUPLEX_STREAMED] <br /> |
| `requestTrailerMode` _string_ | RequestTrailerMode determines how to handle the request trailers | SKIP | Enum: [DEFAULT SEND SKIP] <br /> |
| `responseTrailerMode` _string_ | ResponseTrailerMode determines how to handle the response trailers | SKIP | Enum: [DEFAULT SEND SKIP] <br /> |


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


#### ProxyDeployment



ProxyDeployment configures the Proxy deployment in Kubernetes.



_Appears in:_
- [KubernetesProxyConfig](#kubernetesproxyconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `replicas` _integer_ | The number of desired pods.<br />If omitted, behavior will be managed by the K8s control plane, and will default to 1.<br />If you are using an HPA, make sure to not explicitly define this.<br />K8s reference: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#replicas |  | Minimum: 0 <br /> |
| `strategy` _[DeploymentStrategy](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#deploymentstrategy-v1-apps)_ | The deployment strategy to use to replace existing pods with new<br />ones. The Kubernetes default is a RollingUpdate with 25% maxUnavailable,<br />25% maxSurge.<br /><br />E.g., to recreate pods, minimizing resources for the rollout but causing downtime:<br />strategy:<br />  type: Recreate<br />E.g., to roll out as a RollingUpdate but with non-default parameters:<br />strategy:<br />  type: RollingUpdate<br />  rollingUpdate:<br />    maxSurge: 100% |  |  |


#### ProxyProtocolConfig



ProxyProtocolConfig configures the PROXY protocol listener filter.
The presence of this configuration enables PROXY protocol support.



_Appears in:_
- [ListenerPolicySpec](#listenerpolicyspec)



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
| `failOpen` _boolean_ | FailOpen determines if requests are limited when the rate limit service is unavailable.<br />Defaults to true, meaning requests are allowed upstream and not limited if the rate limit service is unavailable. | true |  |
| `timeout` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | Timeout provides an optional timeout value for requests to the rate limit service.<br />For rate limiting, prefer using this timeout rather than setting the generic `timeout` on the `GrpcService`.<br />See [envoy issue](https://github.com/envoyproxy/envoy/issues/20070) for more info. | 100ms |  |
| `xRateLimitHeaders` _[XRateLimitHeadersStandard](#xratelimitheadersstandard)_ | XRateLimitHeaders configures the standard version to use for X-RateLimit headers emitted.<br />See [envoy docs](https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/filters/http/ratelimit/v3/rate_limit.proto#envoy-v3-api-field-extensions-filters-http-ratelimit-v3-ratelimit-enable-x-ratelimit-headers) for more info.<br />Disabled by default. | Off | Enum: [Off DraftVersion03] <br /> |




#### Regex



Regex configures the regular expression (regex) matching for prompt guards and data masking.



_Appears in:_
- [PromptguardRequest](#promptguardrequest)
- [PromptguardResponse](#promptguardresponse)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `matches` _string array_ | A list of regex patterns to match against the request or response.<br />Matches and built-ins are additive. |  |  |
| `builtins` _[BuiltIn](#builtin) array_ | A list of built-in regex patterns to match against the request or response.<br />Matches and built-ins are additive. |  | Enum: [SSN CREDIT_CARD PHONE_NUMBER EMAIL] <br /> |
| `action` _[Action](#action)_ | The action to take if a regex pattern is matched in a request or response.<br />This setting applies only to request matches. PromptguardResponse matches are always masked by default.<br />Defaults to `MASK`. | MASK |  |


#### RemoteJWKS







_Appears in:_
- [JWKS](#jwks)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `url` _string_ | URL is the URL of the remote JWKS server, it must be a full FQDN with protocol, host and path.<br />For example, https://example.com/keys |  | MaxLength: 2048 <br />MinLength: 1 <br /> |
| `backendRef` _[BackendObjectReference](https://gateway-api.sigs.k8s.io/reference/spec/#backendobjectreference)_ | BackendRef is reference to the backend of the JWKS server. |  |  |
| `cacheDuration` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | Duration after which the cached JWKS expires.<br />If unspecified, the default cache duration is 5 minutes. |  |  |


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
- [AgentgatewayPolicyTraffic](#agentgatewaypolicytraffic)
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
| `numRetries` _integer_ | Specifies the allowed number of retries. Defaults to 1. |  | Minimum: 1 <br /> |


#### RouteType

_Underlying type:_ _string_

RouteType specifies how the AI gateway should process incoming requests
based on the URL path and the API format expected.

_Validation:_
- Enum: [completions messages models passthrough responses anthropic_token_count]

_Appears in:_
- [BackendAI](#backendai)

| Field | Description |
| --- | --- |
| `completions` | RouteTypeCompletions processes OpenAI /v1/chat/completions format requests<br /> |
| `messages` | RouteTypeMessages processes Anthropic /v1/messages format requests<br /> |
| `models` | RouteTypeModels handles /v1/models endpoint (returns available models)<br /> |
| `passthrough` | RouteTypePassthrough sends requests to upstream as-is without LLM processing<br /> |
| `responses` | RouteTypeResponses processes OpenAI /v1/responses format requests<br /> |
| `anthropic_token_count` | RouteTypeAnthropicTokenCount processes Anthropic /v1/messages/count_tokens format requests<br /> |


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


#### SecretSelector







_Appears in:_
- [AgentAPIKeyAuthentication](#agentapikeyauthentication)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `matchLabels` _object (keys:string, values:string)_ | Label selector to select the target resource. |  |  |


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
| `extraLabels` _object (keys:string, values:string)_ | Additional labels to add to the Service object metadata.<br />If the same label is present on `Gateway.spec.infrastructure.labels`, the `Gateway` takes precedence. |  |  |
| `extraAnnotations` _object (keys:string, values:string)_ | Additional annotations to add to the Service object metadata.<br />If the same annotation is present on `Gateway.spec.infrastructure.annotations`, the `Gateway` takes precedence. |  |  |
| `ports` _[Port](#port) array_ | Additional configuration for the service ports.<br />The actual port numbers are specified in the Gateway resource. |  |  |
| `externalTrafficPolicy` _string_ | ExternalTrafficPolicy defines the external traffic policy for the service.<br />Valid values are Cluster and Local. Default value is Cluster. |  |  |


#### ServiceAccount







_Appears in:_
- [KubernetesProxyConfig](#kubernetesproxyconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `extraLabels` _object (keys:string, values:string)_ | Additional labels to add to the ServiceAccount object metadata. |  |  |
| `extraAnnotations` _object (keys:string, values:string)_ | Additional annotations to add to the ServiceAccount object metadata.<br />If the same annotation is present on `Gateway.spec.infrastructure.annotations`, the `Gateway` takes precedence. |  |  |


#### SlowStart







_Appears in:_
- [LoadBalancerLeastRequestConfig](#loadbalancerleastrequestconfig)
- [LoadBalancerRoundRobinConfig](#loadbalancerroundrobinconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `window` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | Represents the size of slow start window.<br />If set, the newly created host remains in slow start mode starting from its creation time<br />for the duration of slow start window. |  |  |
| `aggression` _string_ | This parameter controls the speed of traffic increase over the slow start window. Defaults to 1.0,<br />so that endpoint would get linearly increasing amount of traffic.<br />When increasing the value for this parameter, the speed of traffic ramp-up increases non-linearly.<br />The value of aggression parameter should be greater than 0.0.<br />By tuning the parameter, is possible to achieve polynomial or exponential shape of ramp-up curve.<br /><br />During slow start window, effective weight of an endpoint would be scaled with time factor and aggression:<br />`new_weight = weight * max(min_weight_percent, time_factor ^ (1 / aggression))`,<br />where `time_factor=(time_since_start_seconds / slow_start_time_seconds)`.<br /><br />As time progresses, more and more traffic would be sent to endpoint, which is in slow start window.<br />Once host exits slow start, time_factor and aggression no longer affect its weight. |  |  |
| `minWeightPercent` _integer_ | Minimum weight percentage of an endpoint during slow start. |  | Maximum: 100 <br />Minimum: 0 <br /> |


#### SourceIP







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
| `matcher` _[StatsMatcher](#statsmatcher)_ | Matcher configures inclusion or exclusion lists for Envoy stats.<br />Only one of inclusionList or exclusionList may be set.<br />If unset, Envoy's default stats emission behavior applies. |  | MaxProperties: 1 <br />MinProperties: 1 <br /> |


#### StatsMatcher



StatsMatcher specifies either an inclusion or exclusion list for Envoy stats.
See Envoy's envoy.config.metrics.v3.StatsMatcher for details.

_Validation:_
- MaxProperties: 1
- MinProperties: 1

_Appears in:_
- [StatsConfig](#statsconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `inclusionList` _[StringMatcher](#stringmatcher) array_ | inclusionList specifies which stats to include, using string matchers. |  | MaxItems: 16 <br /> |
| `exclusionList` _[StringMatcher](#stringmatcher) array_ | exclusionList specifies which stats to exclude, using string matchers. |  | MaxItems: 16 <br /> |


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
- [StatsMatcher](#statsmatcher)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `exact` _string_ | The input string must match exactly the string specified here.<br />Example: abc matches the value abc |  |  |
| `prefix` _string_ | The input string must have the prefix specified here.<br />Note: empty prefix is not allowed, please use regex instead.<br />Example: abc matches the value abc.xyz |  |  |
| `suffix` _string_ | The input string must have the suffix specified here.<br />Note: empty prefix is not allowed, please use regex instead.<br />Example: abc matches the value xyz.abc |  |  |
| `contains` _string_ | The input string must contain the substring specified here.<br />Example: abc matches the value xyz.abc.def |  |  |
| `safeRegex` _string_ | The input string must match the Google RE2 regular expression specified here.<br />See https://github.com/google/re2/wiki/Syntax for the syntax. |  |  |
| `ignoreCase` _boolean_ | If true, indicates the exact/prefix/suffix/contains matching should be<br />case insensitive. This has no effect on the regex match.<br />For example, the matcher data will match both input string Data and data if this<br />option is set to true. |  |  |


#### TCPKeepalive



See [Envoy documentation](https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/core/v3/address.proto#envoy-v3-api-msg-config-core-v3-tcpkeepalive) for more details.



_Appears in:_
- [BackendConfigPolicySpec](#backendconfigpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `keepAliveProbes` _integer_ | Maximum number of keep-alive probes to send before dropping the connection. |  | Minimum: 0 <br /> |
| `keepAliveTime` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | The number of seconds a connection needs to be idle before keep-alive probes start being sent. |  |  |
| `keepAliveInterval` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | The number of seconds between keep-alive probes. |  |  |


#### TLS







_Appears in:_
- [BackendConfigPolicySpec](#backendconfigpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `secretRef` _[LocalObjectReference](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#localobjectreference-v1-core)_ | Reference to the TLS secret containing the certificate, key, and optionally the root CA. |  |  |
| `files` _[TLSFiles](#tlsfiles)_ | File paths to certificates local to the proxy. |  |  |
| `wellKnownCACertificates` _[WellKnownCACertificatesType](#wellknowncacertificatestype)_ | WellKnownCACertificates specifies whether to use a well-known set of CA<br />certificates for validating the backend's certificate chain. Currently,<br />only the system certificate pool is supported via SDS. |  |  |
| `insecureSkipVerify` _boolean_ | InsecureSkipVerify originates TLS but skips verification of the backend's certificate.<br />WARNING: This is an insecure option that should only be used if the risks are understood. |  |  |
| `sni` _string_ | The SNI domains that should be considered for TLS connection |  | MinLength: 1 <br /> |
| `verifySubjectAltNames` _string array_ | Verify that the Subject Alternative Name in the peer certificate is one of the specified values.<br />note that a root_ca must be provided if this option is used. |  |  |
| `parameters` _[TLSParameters](#tlsparameters)_ | General TLS parameters. See the [envoy docs](https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/transport_sockets/tls/v3/common.proto#extensions-transport-sockets-tls-v3-tlsparameters)<br />for more information on the meaning of these values. |  |  |
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


#### TLSParameters







_Appears in:_
- [TLS](#tls)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `minVersion` _[TLSVersion](#tlsversion)_ | Minimum TLS version. |  | Enum: [AUTO 1.0 1.1 1.2 1.3] <br /> |
| `maxVersion` _[TLSVersion](#tlsversion)_ | Maximum TLS version. |  | Enum: [AUTO 1.0 1.1 1.2 1.3] <br /> |
| `cipherSuites` _string array_ |  |  |  |
| `ecdhCurves` _string array_ |  |  |  |


#### TLSVersion

_Underlying type:_ _string_

TLSVersion defines the TLS version.

_Validation:_
- Enum: [AUTO 1.0 1.1 1.2 1.3]

_Appears in:_
- [TLSParameters](#tlsparameters)

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
| `maxPathTagLength` _integer_ | Maximum length of the request path to extract and include in the HttpUrl tag. Used to truncate lengthy request paths to meet the needs of a tracing backend. Default: 256 |  | Minimum: 1 <br /> |
| `attributes` _[CustomAttribute](#customattribute) array_ | A list of attributes with a unique name to create attributes for the active span. |  | MaxProperties: 2 <br />MinProperties: 1 <br /> |
| `spawnUpstreamSpan` _boolean_ | Create separate tracing span for each upstream request if true. Defaults to false<br />Link to envoy docs for more info |  |  |


#### TracingProtocol

_Underlying type:_ _string_





_Appears in:_
- [AgentTracing](#agenttracing)

| Field | Description |
| --- | --- |
| `HTTP` |  |
| `GRPC` |  |


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



_Appears in:_
- [TrafficPolicy](#trafficpolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `targetRefs` _[LocalPolicyTargetReferenceWithSectionName](#localpolicytargetreferencewithsectionname) array_ | TargetRefs specifies the target resources by reference to attach the policy to. |  | MaxItems: 16 <br />MinItems: 1 <br /> |
| `targetSelectors` _[LocalPolicyTargetSelectorWithSectionName](#localpolicytargetselectorwithsectionname) array_ | TargetSelectors specifies the target selectors to select resources to attach the policy to. |  |  |
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
| `rbac` _[Authorization](#authorization)_ | RBAC specifies the role-based access control configuration for the policy.<br />This defines the rules for authorization based on roles and permissions.<br />RBAC policies applied at different attachment points in the configuration<br />hierarchy are not cumulative, and only the most specific policy is enforced. This means an RBAC policy<br />attached to a route will override any RBAC policies applied to the gateway or listener. |  |  |
| `jwt` _[JWTAuthentication](#jwtauthentication)_ | JWT specifies the JWT authentication configuration for the policy.<br />This defines the JWT providers and their configurations. |  |  |


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
| `forwardHeaderMatches` _[HTTPHeaderMatch](#httpheadermatch) array_ | ForwardHeaderMatches defines a list of HTTP header matches that will be<br />used to select the headers to forward to the webhook.<br />Request headers are used when forwarding requests and response headers<br />are used when forwarding responses.<br />By default, no headers are forwarded. |  |  |


#### XRateLimitHeadersStandard

_Underlying type:_ _string_

XRateLimitHeadersStandard controls how XRateLimit headers will emitted.



_Appears in:_
- [RateLimitProvider](#ratelimitprovider)

| Field | Description |
| --- | --- |
| `Off` | XRateLimitHeaderOff disables emitting of XRateLimit headers.<br /> |
| `DraftVersion03` | XRateLimitHeaderDraftV03 outputs headers as described in [draft RFC version 03](https://tools.ietf.org/id/draft-polli-ratelimit-headers-03.html).<br /> |


