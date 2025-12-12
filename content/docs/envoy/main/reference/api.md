---
title: API reference
weight: 10
---

{{< reuse "/docs/snippets/api-ref-docs-intro.md" >}}

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
- [ListenerPolicy](#listenerpolicy)
- [TrafficPolicy](#trafficpolicy)



#### APIKeyAuthentication







_Appears in:_
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `keySources` _[APIKeySource](#apikeysource) array_ | keySources specifies the list of key sources to extract the API key from.<br />Key sources are processed in array order and the first one that successfully<br />extracts a key is used. Within each key source, if multiple types (header, query, cookie) are<br />specified, precedence is: header > query parameter > cookie.<br /><br />If empty, defaults to a single key source with header "api-key".<br /><br />Example:<br />  keySources:<br />  - header: "X-API-KEY"<br />  - query: "api_key"<br />  - header: "Authorization"<br />    query: "token"<br />    cookie: "auth_token"<br /><br />In this example, the system will:<br />1. First try header "X-API-KEY"<br />2. If not found, try query parameter "api_key"<br />3. If not found, try header "Authorization" (then query "token", then cookie "auth_token" within that key source) |  | MaxItems: 16 <br />MinItems: 0 <br /> |
| `forwardCredential` _boolean_ | forwardCredential controls whether the API key is included in the request sent to the upstream.<br />If false (default), the API key is removed from the request before sending to upstream.<br />If true, the API key is included in the request sent to upstream.<br />This applies to all configured key sources (header, query parameter, or cookie). |  |  |
| `clientIdHeader` _string_ | clientIdHeader specifies the header name to forward the authenticated client identifier.<br />If not specified, the client identifier will not be forwarded in any header.<br />Example: "x-client-id" |  |  |
| `secretRef` _[SecretObjectReference](#secretobjectreference)_ | secretRef references a Kubernetes secret storing a set of API Keys. If there are many keys, 'secretSelector' can be<br />used instead.<br /><br />Each entry in the Secret represents one API Key. The key is an arbitrary identifier.<br />The value is a string, representing the API Key.<br /><br />Example:<br /><br />apiVersion: v1<br />kind: Secret<br />metadata:<br />  name: api-key<br />stringData:<br />  client1: "k-123"<br />  client2: "k-456" |  |  |
| `secretSelector` _[LabelSelector](#labelselector)_ | secretSelector selects multiple secrets containing API Keys. If the same key is defined in multiple secrets, the<br />behavior is undefined.<br /><br />Each entry in the Secret represents one API Key. The key is an arbitrary identifier.<br />The value is a string, representing the API Key.<br /><br />Example:<br /><br />apiVersion: v1<br />kind: Secret<br />metadata:<br />  name: api-key<br />stringData:<br />  client1: "k-123"<br />  client2: "k-456" |  |  |


#### APIKeySource



APIKeySource defines where to extract the API key from within a single key source.
Within a single key source, if multiple types are specified, precedence is:
header > query parameter > cookie. The header is checked first, and only falls back
to query parameter if the header is not present, then to cookie if both header and query
are not present.



_Appears in:_
- [APIKeyAuthentication](#apikeyauthentication)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `header` _string_ | header specifies the name of the header that contains the API key. |  | MaxLength: 256 <br />MinLength: 1 <br /> |
| `query` _string_ | query specifies the name of the query parameter that contains the API key. |  | MaxLength: 256 <br />MinLength: 1 <br /> |
| `cookie` _string_ | cookie specifies the name of the cookie that contains the API key. |  | MaxLength: 256 <br />MinLength: 1 <br /> |


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
- [HTTPSettings](#httpsettings)

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


#### Agentgateway



Agentgateway is obsolete and retained only for backwards compatibility.  Use
the agentgateway.dev AgentgatewayParameters API to configure agentgateway
deployments.



_Appears in:_
- [KubernetesProxyConfig](#kubernetesproxyconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `enabled` _boolean_ | Obsolete: This field is no longer used. The agentgateway dataplane is<br />automatically enabled when the Gateway references a GatewayClass with<br />controllerName: agentgateway.dev/agentgateway. Use the AgentgatewayParameters<br />API to configure agentgateway deployments. Any values specified here are ignored. |  |  |
| `logLevel` _string_ | Log level for the agentgateway. Defaults to info.<br />Levels include "trace", "debug", "info", "error", "warn". See: https://docs.rs/tracing/latest/tracing/struct.Level.html |  |  |
| `image` _[Image](#image)_ | The agentgateway container image. See<br />https://kubernetes.io/docs/concepts/containers/images<br />for details.<br /><br />Default values, which may be overridden individually:<br /><br />	registry: ghcr.io/agentgateway<br />	repository: agentgateway<br />	tag: <agentgateway version><br />	pullPolicy: IfNotPresent |  |  |
| `securityContext` _[SecurityContext](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#securitycontext-v1-core)_ | The security context for this container. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#securitycontext-v1-core<br />for details. |  |  |
| `resources` _[ResourceRequirements](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#resourcerequirements-v1-core)_ | The compute resources required by this container. See<br />https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/<br />for details. |  |  |
| `env` _[EnvVar](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#envvar-v1-core) array_ | The container environment variables. |  |  |
| `extraVolumeMounts` _[VolumeMount](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#volumemount-v1-core) array_ | Additional volume mounts to add to the container. See<br />https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#volumemount-v1-core<br />for details. |  |  |




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


#### AuthorizationRequest



AuthorizationRequest configures the authorization request to the external service.



_Appears in:_
- [ExtHttpService](#exthttpservice)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `headersToAdd` _object (keys:string, values:string)_ | HeadersToAdd specifies additional headers to add to the authorization request.<br />These headers are sent to the authorization service in addition to the original request headers.<br />Client request headers with the same key will be overridden.<br />The keys are header names and values are envoy format specifiers, see https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/filters/http/ext_authz/v3/ext_authz.proto#envoy-v3-api-field-extensions-filters-http-ext-authz-v3-authorizationrequest-headers-to-add. |  |  |


#### AuthorizationResponse



AuthorizationResponse configures the authorization response from the external service.



_Appears in:_
- [ExtHttpService](#exthttpservice)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `headersToBackend` _string array_ | HeadersToBackend specifies which headers from the authorization response<br />should be forwarded to the upstream service when the request is authorized.<br />Common examples: ["x-current-user", "x-user-id", "x-auth-request-email"] |  |  |


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




#### BasicAuthPolicy



BasicAuthPolicy configures HTTP basic authentication using the Authorization header.
Basic authentication validates requests against username/password pairs provided either inline or via a Kubernetes secret.
The credentials must be in htpasswd SHA-1 format.



_Appears in:_
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `users` _string array_ | Users provides an inline list of username/password pairs in htpasswd format.<br />Each entry should be formatted as "username:hashed_password".<br />The only supported hash format is SHA-1<br /><br />Example entries:<br />  - "user1:\{SHA\}d95o2uzYI7q7tY7bHI4U1xBug7s=" |  | MaxItems: 256 <br />MinItems: 1 <br /> |
| `secretRef` _[SecretReference](#secretreference)_ | SecretRef references a Kubernetes secret containing htpasswd data.<br />The secret must contain username/password pairs in htpasswd format. |  |  |
| `disable` _[PolicyDisable](#policydisable)_ | Disable basic auth.<br />Can be used to disable basic auth policies applied at a higher level in the config hierarchy. |  |  |


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


#### CELFilter

_Underlying type:_ _struct_

CELFilter filters requests based on Common Expression Language (CEL).



_Appears in:_
- [FilterType](#filtertype)



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
| `additionalOrigins` _StringMatcher array_ | Specifies additional source origins that will be allowed in addition to the destination origin. |  | MaxItems: 16 <br /> |


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




#### Compression



Compression configures HTTP gzip compression and decompression behavior.



_Appears in:_
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `responseCompression` _[ResponseCompression](#responsecompression)_ | ResponseCompression controls response compression to the downstream.<br />If set, responses with the appropriate `Accept-Encoding` header with certain textual content types will be compressed using gzip.<br />The content-types that will be compressed are:<br />- `application/javascript`<br />- `application/json`<br />- `application/xhtml+xml`<br />- `image/svg+xml`<br />- `text/css`<br />- `text/html`<br />- `text/plain`<br />- `text/xml` |  |  |
| `requestDecompression` _[RequestDecompression](#requestdecompression)_ | RequestDecompression controls request decompression.<br />If set, gzip requests will be decompressed. |  |  |


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
- [HTTPSettings](#httpsettings)

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
| `grpcService` _[ExtGrpcService](#extgrpcservice)_ | GrpcService is the GRPC service that will handle the auth.<br />Mutually exclusive with HttpService. |  |  |
| `httpService` _[ExtHttpService](#exthttpservice)_ | HttpService is the HTTP service that will handle the auth.<br />Mutually exclusive with GrpcService. |  |  |
| `headersToForward` _string array_ | HeadersToForward specifies which headers from the client request should be<br />forwarded to the external authorization service.<br /><br />HTTP services by default have the following headers forwarded: Host, Method, Path, Content-Length, Authorization.<br /><br />If this field is omitted, gRPC services will have all client request headers forwarded,<br />while HTTP services will only receive the default headers described above.<br /><br />Common examples: ["cookie", "authorization", "x-forwarded-for"]<br />More info is available on the [Envoy docs](https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/filters/http/ext_authz/v3/ext_authz.proto#envoy-v3-api-field-extensions-filters-http-ext-authz-v3-extauthz-allowed-headers) |  |  |
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
| `retry` _[ExtSvcRetryPolicy](#extsvcretrypolicy)_ | Retry specifies the retry policy for gRPC streams associated with the service. |  |  |


#### ExtHttpService



ExtHttpService defines the HTTP service that will handle external authorization.



_Appears in:_
- [ExtAuthProvider](#extauthprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `backendRef` _[BackendRef](https://gateway-api.sigs.k8s.io/reference/spec/#backendref)_ | BackendRef references the backend HTTP service. |  |  |
| `pathPrefix` _string_ | PathPrefix specifies a prefix to the value of the authorization request's path header.<br />This allows customizing the path at which the authorization server expects to receive requests.<br />For example, if the authorization server expects requests at "/verify", set this to "/verify".<br />If not specified, the original request path is used. |  |  |
| `requestTimeout` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | RequestTimeout is the timeout for the HTTP request. Default timeout is 2 seconds. |  |  |
| `authorizationRequest` _[AuthorizationRequest](#authorizationrequest)_ | AuthorizationRequest configures the authorization request to the external service. |  |  |
| `authorizationResponse` _[AuthorizationResponse](#authorizationresponse)_ | AuthorizationResponse configures the authorization response from the external service. |  |  |
| `retry` _[ExtSvcRetryPolicy](#extsvcretrypolicy)_ | Retry specifies the retry policy for HTTP requests to the authorization service. |  |  |


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


#### ExtSvcRetryPolicy







_Appears in:_
- [ExtGrpcService](#extgrpcservice)
- [ExtHttpService](#exthttpservice)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `attempts` _integer_ | Attempts specifies the number of retry attempts for a request.<br />Defaults to 1 attempt if not set.<br />A value of 0 effectively disables retries. | 1 | Minimum: 0 <br /> |
| `backoff` _[RetryBackoff](#retrybackoff)_ | Backoff specifies the retry backoff strategy.<br />If not set, a default backoff with a base interval of 1000ms is used. The default max interval is 10 times the base interval. |  |  |


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
| `type` _[GatewayExtensionType](#gatewayextensiontype)_ | Deprecated: Setting this field has no effect.<br />Type indicates the type of the GatewayExtension to be used. |  | Enum: [ExtAuth ExtProc RateLimit JWT OAuth2] <br /> |
| `extAuth` _[ExtAuthProvider](#extauthprovider)_ | ExtAuth configuration for ExtAuth extension type. |  |  |
| `extProc` _[ExtProcProvider](#extprocprovider)_ | ExtProc configuration for ExtProc extension type. |  |  |
| `rateLimit` _[RateLimitProvider](#ratelimitprovider)_ | RateLimit configuration for RateLimit extension type. |  |  |
| `jwt` _[JWT](#jwt)_ | JWT configuration for JWT extension type. |  |  |
| `oauth2` _[OAuth2Provider](#oauth2provider)_ | OAuth2 configuration for OAuth2 extension type. |  |  |


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
| `JWT` | GatewayExtensionTypeJWT is the type for the JWT extensions<br /> |
| `OAuth2` | GatewayExtensionTypeOAuth2 is the type for OAuth2 extensions.<br /> |


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



#### GracefulShutdownSpec







_Appears in:_
- [Pod](#pod)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `enabled` _boolean_ | Enable grace period before shutdown to finish current requests while Envoy health checks fail to e.g. notify external load balancers. *NOTE:* This will not have any effect if you have not defined health checks via the health check filter |  |  |
| `sleepTimeSeconds` _integer_ | Time (in seconds) for the preStop hook to wait before allowing Envoy to terminate |  | Maximum: 3.1536e+07 <br />Minimum: 0 <br /> |




#### GrpcStatusFilter

_Underlying type:_ _[struct{Statuses []GrpcStatus "json:\"statuses,omitempty\""; Exclude *bool "json:\"exclude,omitempty\""}](#struct{statuses-[]grpcstatus-"json:\"statuses,omitempty\"";-exclude-*bool-"json:\"exclude,omitempty\""})_

GrpcStatusFilter filters gRPC requests based on their response status.
Based on: https://www.envoyproxy.io/docs/envoy/v1.33.0/api-v3/config/accesslog/v3/accesslog.proto#enum-config-accesslog-v3-grpcstatusfilter-status



_Appears in:_
- [FilterType](#filtertype)



#### HTTPListenerPolicy



HTTPListenerPolicy is intended to be used for configuring the Envoy `HttpConnectionManager` and any other config or policy
that should map 1-to-1 with a given HTTP listener, such as the Envoy health check HTTP filter.
Currently these policies can only be applied per `Gateway` but support for `Listener` attachment may be added in the future.
See https://github.com/kgateway-dev/kgateway/issues/11786 for more details.
Deprecated: Use the httpSettings field on ListenerPolicy instead.





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
| `earlyRequestHeaderModifier` _[HTTPHeaderFilter](#httpheaderfilter)_ | EarlyRequestHeaderModifier defines header modifications to be applied early in the request processing,<br />before route selection.<br />For example, if you use ExternalAuthz to add a header, you may want to remove it here, to make<br />sure it did not come from the client. |  |  |


#### HTTPSettings







_Appears in:_
- [HTTPListenerPolicySpec](#httplistenerpolicyspec)
- [ListenerConfig](#listenerconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
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
| `earlyRequestHeaderModifier` _[HTTPHeaderFilter](#httpheaderfilter)_ | EarlyRequestHeaderModifier defines header modifications to be applied early in the request processing,<br />before route selection.<br />For example, if you use ExternalAuthz to add a header, you may want to remove it here, to make<br />sure it did not come from the client. |  |  |


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

_Underlying type:_ _struct_

HeaderFilter filters requests based on headers.
Based on: https://www.envoyproxy.io/docs/envoy/v1.33.0/api-v3/config/accesslog/v3/accesslog.proto#config-accesslog-v3-headerfilter



_Appears in:_
- [FilterType](#filtertype)



#### HeaderName

_Underlying type:_ _string_





_Appears in:_
- [HeaderTransformation](#headertransformation)



#### HeaderSource

_Underlying type:_ _struct_

HeaderSource configures how to retrieve a JWT from a header



_Appears in:_
- [JWTTokenSource](#jwttokensource)



#### HeaderTransformation







_Appears in:_
- [Transform](#transform)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _[HeaderName](#headername)_ | Name is the name of the header to interact with. |  |  |
| `value` _[InjaTemplate](#injatemplate)_ | Value is the Inja template to apply to generate the output value for the header. |  |  |


#### HeaderValue

_Underlying type:_ _struct_

Header name/value pair.
Ref: https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/core/v3/base.proto#envoy-v3-api-msg-config-core-v3-headervalue



_Appears in:_
- [AccessLogGrpcService](#accessloggrpcservice)
- [CommonAccessLogGrpcService](#commonaccessloggrpcservice)
- [CommonGrpcService](#commongrpcservice)



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


#### HttpsUri

_Underlying type:_ _string_

HttpsUri specifies an HTTPS URI

_Validation:_
- Pattern: `^https://([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(:[0-9]{1,5})?(/[a-zA-Z0-9\-._~!$&'()*+,;=:@%]*)*/?(\?[a-zA-Z0-9\-._~!$&'()*+,;=:@%/?]*)?$`

_Appears in:_
- [OAuth2Provider](#oauth2provider)



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


#### JWT







_Appears in:_
- [GatewayExtensionSpec](#gatewayextensionspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `validationMode` _[ValidationMode](#validationmode)_ | ValidationMode configures how JWT validation behaves.<br />If unset or empty, Strict mode is used (JWT is required).<br />If set to AllowMissing, unauthenticated requests without a JWT are allowed through.<br />If using this mode, make sure to consider the security implications and<br />consider using an `RBAC` policy to enforce authorization. |  | Enum: [Strict AllowMissing] <br /> |
| `providers` _[NamedJWTProvider](#namedjwtprovider) array_ | Providers configures named JWT providers.<br />If multiple providers are specified for a given JWT policy,<br />the providers will be `OR`-ed together and will allow validation to any of the providers. |  | MaxItems: 32 <br /> |


#### JWTAuthentication



JWTAuthentication defines the providers used to configure JWT authentication



_Appears in:_
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `extensionRef` _[NamespacedObjectReference](#namespacedobjectreference)_ | ExtensionRef references a GatewayExtension that provides the jwt providers |  |  |
| `disable` _[PolicyDisable](#policydisable)_ | Disable all JWT filters.<br />Can be used to disable JWT policies applied at a higher level in the config hierarchy. |  |  |


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
| `envoyContainer` _[EnvoyContainer](#envoycontainer)_ | Configuration for the container running Envoy. |  |  |
| `sdsContainer` _[SdsContainer](#sdscontainer)_ | Configuration for the container running the Secret Discovery Service (SDS). |  |  |
| `podTemplate` _[Pod](#pod)_ | Configuration for the pods that will be created. |  |  |
| `service` _[Service](#service)_ | Configuration for the Kubernetes Service that exposes the proxy over<br />the network. |  |  |
| `serviceAccount` _[ServiceAccount](#serviceaccount)_ | Configuration for the Kubernetes ServiceAccount used by the proxy pods. |  |  |
| `istio` _[IstioIntegration](#istiointegration)_ | Configuration for the Istio integration. |  |  |
| `stats` _[StatsConfig](#statsconfig)_ | Configuration for the stats server. |  |  |
| `agentgateway` _[Agentgateway](#agentgateway)_ | Obsolete: This field is no longer used. Agentgateway configuration is now<br />determined automatically based on the GatewayClass controllerName<br />(agentgateway.dev/agentgateway). Use the AgentgatewayParameters API to<br />configure agentgateway deployments. Any values specified here are ignored. |  |  |
| `omitDefaultSecurityContext` _boolean_ | OmitDefaultSecurityContext is used to control whether or not<br />`securityContext` fields should be rendered for the various generated<br />Deployments/Containers that are dynamically provisioned by the deployer.<br /><br />When set to true, no `securityContexts` will be provided and will left<br />to the user/platform to be provided.<br /><br />This should be enabled on platforms such as Red Hat OpenShift where the<br />`securityContext` will be dynamically added to enforce the appropriate<br />level of security. |  |  |


#### LabelSelector



LabelSelector selects resources using label selectors.



_Appears in:_
- [APIKeyAuthentication](#apikeyauthentication)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `matchLabels` _object (keys:string, values:string)_ | Label selector to select the target resource. |  |  |


#### ListenerConfig







_Appears in:_
- [ListenerPolicySpec](#listenerpolicyspec)
- [ListenerPortConfig](#listenerportconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `proxyProtocol` _[ProxyProtocolConfig](#proxyprotocolconfig)_ | ProxyProtocol configures the PROXY protocol listener filter.<br />When set, Envoy will expect connections to include the PROXY protocol header.<br />This is commonly used when kgateway is behind a load balancer that preserves client IP information.<br />See here for more information: https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/filters/listener/proxy_protocol/v3/proxy_protocol.proto |  |  |
| `perConnectionBufferLimitBytes` _integer_ | PerConnectionBufferLimitBytes sets the per-connection buffer limit for all listeners on the gateway.<br />This controls the maximum size of read and write buffers for new connections.<br />When using Envoy as an edge proxy, configuring the listener buffer limit is important to guard against<br />potential attacks or misconfigured downstreams that could hog the proxy's resources.<br />If unspecified, an implementation-defined default is applied (1MiB).<br />See here for more information: https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/listener/v3/listener.proto#envoy-v3-api-field-config-listener-v3-listener-per-connection-buffer-limit-bytes |  | Minimum: 0 <br /> |
| `httpSettings` _[HTTPSettings](#httpsettings)_ | HTTPListenerPolicy is intended to be used for configuring the Envoy `HttpConnectionManager` and any other config or policy<br />that should map 1-to-1 with a given HTTP listener, such as the Envoy health check HTTP filter. |  |  |


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
| `default` _[ListenerConfig](#listenerconfig)_ | Default specifies default listener configuration for all Listeners, unless a per-port<br />configuration is defined. |  |  |
| `perPort` _[ListenerPortConfig](#listenerportconfig) array_ | Per port configuration allows overriding the listener config per port. Once set, this<br />configuration completely replaces the default configuration for all listeners handling traffic<br />that match this port. Unspecified fields in per-port configuration will not inherit values from default. |  | MaxItems: 64 <br /> |


#### ListenerPortConfig







_Appears in:_
- [ListenerPolicySpec](#listenerpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `port` _integer_ | The Port indicates the Port Number to which the Listener configuration will be<br />applied. This configuration will be applied to all Listeners handling<br />traffic that match this port. |  | Maximum: 65535 <br />Minimum: 1 <br /> |
| `listener` _[ListenerConfig](#listenerconfig)_ | Listener stores the configuration that will be applied to all Listeners handling<br />matching the given port. |  |  |


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




#### NamedJWTProvider



NamedJWTProvider is a named JWT provider entry.



_Appears in:_
- [JWT](#jwt)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ | Name is the unique name of the JWT provider. |  | MaxLength: 253 <br />MinLength: 1 <br /> |
| `issuer` _string_ | Issuer of the JWT. the 'iss' claim of the JWT must match this. |  | MaxLength: 2048 <br /> |
| `audiences` _string array_ | Audiences is the list of audiences to be used for the JWT provider.<br />If specified an incoming JWT must have an 'aud' claim, and it must be in this list.<br />If not specified, the audiences will not be checked in the token. |  | MaxItems: 32 <br />MinItems: 1 <br /> |
| `tokenSource` _[JWTTokenSource](#jwttokensource)_ | TokenSource configures where to find the JWT of the current provider. |  |  |
| `claimsToHeaders` _[JWTClaimToHeader](#jwtclaimtoheader) array_ | ClaimsToHeaders is the list of claims to headers to be used for the JWT provider.<br />Optionally set the claims from the JWT payload that you want to extract and add as headers<br />to the request before the request is forwarded to the upstream destination.<br />Note: if ClaimsToHeaders is set, the Envoy route cache will be cleared.<br />This allows the JWT filter to correctly affect routing decisions. |  | MaxItems: 32 <br />MinItems: 1 <br /> |
| `jwks` _[JWKS](#jwks)_ | JWKS is the source for the JSON Web Keys to be used to validate the JWT. |  |  |
| `forwardToken` _boolean_ | ForwardToken configures if the JWT token is forwarded to the upstream backend.<br />If true, the header containing the token will be forwarded upstream.<br />If false or not set, the header containing the token will be removed. |  |  |


#### OAuth2CookieConfig







_Appears in:_
- [OAuth2Provider](#oauth2provider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `domain` _string_ | CookieDomain specifies the domain to set on the access and ID token cookies.<br />If set, the cookies will be set for the specified domain and all its subdomains. This is useful when requests<br />to subdomains are not required to be re-authenticated after the user has logged into the parent domain.<br />If not set, the cookies will default to the host of the request, not including the subdomains. |  | MaxLength: 253 <br />MinLength: 1 <br />Pattern: `^[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9]))*$` <br /> |
| `names` _[OAuth2CookieNames](#oauth2cookienames)_ | Names specifies the names of the cookies used to store the tokens.<br />If not set, the default names will be used. |  |  |
| `sameSite` _[OAuth2CookieSameSite](#oauth2cookiesamesite)_ | SameSite specifies the SameSite attribute for the OAuth2 cookies.<br />If not set, the default is Lax. |  | Enum: [Lax Strict None] <br /> |


#### OAuth2CookieNames



OAuth2CookieNames specifies the names of the cookies used to store the tokens.



_Appears in:_
- [OAuth2CookieConfig](#oauth2cookieconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `accessToken` _string_ | AccessToken specifies the name of the cookie used to store the access token. |  | MinLength: 1 <br /> |
| `idToken` _string_ | IDToken specifies the name of the cookie used to store the ID token. |  | MinLength: 1 <br /> |


#### OAuth2CookieSameSite

_Underlying type:_ _string_

OAuth2CookieSameSite specifies the SameSite attribute for OAuth2 cookies

_Validation:_
- Enum: [Lax Strict None]

_Appears in:_
- [OAuth2CookieConfig](#oauth2cookieconfig)

| Field | Description |
| --- | --- |
| `Lax` | OAuth2CookieSameSiteLax specifies the Lax SameSite attribute for OAuth2 cookies<br /> |
| `Strict` | OAuth2CookieSameSiteStrict specifies the Strict SameSite attribute for OAuth2 cookies<br /> |
| `None` | OAuth2CookieSameSiteNone specifies the None SameSite attribute for OAuth2 cookies<br /> |


#### OAuth2Credentials



OAuth2Credentials specifies the Oauth2 client credentials.



_Appears in:_
- [OAuth2Provider](#oauth2provider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `clientID` _string_ | ClientID specifies the client ID issued to the client during the registration process.<br />Refer to https://datatracker.ietf.org/doc/html/rfc6749#section-2.3.1 for more details. |  | MinLength: 1 <br /> |
| `clientSecretRef` _[LocalObjectReference](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#localobjectreference-v1-core)_ | ClientSecretRef specifies a Secret that contains the client secret stored in the key 'client-secret'<br />to use in the authentication request to obtain the access token.<br />Refer to https://datatracker.ietf.org/doc/html/rfc6749#section-2.3.1 for more details. |  |  |


#### OAuth2DenyRedirectMatcher



OAuth2DenyRedirectMatcher specifies the matcher to match requests that should be denied redirects to the authorization endpoint.



_Appears in:_
- [OAuth2Provider](#oauth2provider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `headers` _HTTPHeaderMatch array_ | Headers specifies the list of HTTP headers to match on requests that should be denied redirects. |  | MaxItems: 16 <br />MinItems: 1 <br /> |


#### OAuth2Policy



OAuth2Policy specifies the OAuth2 policy to apply to requests.



_Appears in:_
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `extensionRef` _[NamespacedObjectReference](#namespacedobjectreference)_ | ExtensionRef specifies the GatewayExtension that should be used for OAuth2. |  |  |


#### OAuth2Provider



OAuth2Provider specifies the configuration for OAuth2 extension provider.



_Appears in:_
- [GatewayExtensionSpec](#gatewayextensionspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `backendRef` _[BackendRef](https://gateway-api.sigs.k8s.io/reference/spec/#backendref)_ | BackendRef specifies the Backend to use for the OAuth2 provider. |  |  |
| `authorizationEndpoint` _[HttpsUri](#httpsuri)_ | AuthorizationEndpoint specifies the endpoint to redirect to for authorization in response to unauthorized requests.<br />Refer to https://datatracker.ietf.org/doc/html/rfc6749#section-3.1 for more details. |  | Pattern: `^https://([a-zA-Z0-9]([a-zA-Z0-9\-]\{0,61\}[a-zA-Z0-9])?\.)*[a-zA-Z0-9]([a-zA-Z0-9\-]\{0,61\}[a-zA-Z0-9])?(:[0-9]\{1,5\})?(/[a-zA-Z0-9\-._~!$&'()*+,;=:@%]*)*/?(\?[a-zA-Z0-9\-._~!$&'()*+,;=:@%/?]*)?$` <br /> |
| `tokenEndpoint` _[HttpsUri](#httpsuri)_ | TokenEndpoint specifies the endpoint on the authorization server to retrieve the access token from.<br />Refer to https://datatracker.ietf.org/doc/html/rfc6749#section-3.2 for more details. |  | Pattern: `^https://([a-zA-Z0-9]([a-zA-Z0-9\-]\{0,61\}[a-zA-Z0-9])?\.)*[a-zA-Z0-9]([a-zA-Z0-9\-]\{0,61\}[a-zA-Z0-9])?(:[0-9]\{1,5\})?(/[a-zA-Z0-9\-._~!$&'()*+,;=:@%]*)*/?(\?[a-zA-Z0-9\-._~!$&'()*+,;=:@%/?]*)?$` <br /> |
| `redirectURI` _string_ | RedirectURI specifies the URL passed to the authorization endpoint.<br />Defaults to <request-scheme>://<host>/oauth2/redirect, where the URL scheme and host are derived from the original request.<br />Refer to https://datatracker.ietf.org/doc/html/rfc6749#section-3.1.2 for more details. |  |  |
| `logoutPath` _string_ | LogoutPath specifies the path to log out a user, clearing their credential cookies.<br />Defaults to /logout. | /logout | MinLength: 1 <br /> |
| `forwardAccessToken` _boolean_ | ForwardAccessToken specifies whether to forward the access token to the backend service.<br />If set to true, the token is forwarded over a cookie named BearerToken and is also set in the Authorization header.<br />Defaults to false. |  |  |
| `scopes` _string array_ | List of OAuth scopes to be claimed in the authentication request.<br />Defaults to "user" scope if not specified.<br />When using OpenID, the "openid" scope must be included.<br />Refer to https://datatracker.ietf.org/doc/html/rfc6749#section-3.3 for more details. |  |  |
| `credentials` _[OAuth2Credentials](#oauth2credentials)_ | Credentials specifies the Oauth2 client credentials to use for authentication. |  |  |
| `issuerURI` _string_ | IssuerURI specifies the OpenID provider's issuer URL to discover the OpenID provider's configuration.<br />The Issuer must be a URI RFC 3986 [RFC3986] with a scheme component that must be https, a host component,<br />and optionally, port and path components and no query or fragment components.<br />It discovers the authorizationEndpoint, tokenEndpoint, and endSessionEndpoint if specified in the discovery response.<br />Refer to https://openid.net/specs/openid-connect-discovery-1_0.html#ProviderConfig for more details.<br />Note that the OpenID provider configuration is cached and only refreshed periodically when the GatewayExtension object<br />is reprocessed. |  | Pattern: `^https://([a-zA-Z0-9]([a-zA-Z0-9\-]\{0,61\}[a-zA-Z0-9])?\.)*[a-zA-Z0-9]([a-zA-Z0-9\-]\{0,61\}[a-zA-Z0-9])?(:[0-9]\{1,5\})?(/[a-zA-Z0-9\-._~!$&'()*+,;=:@%]*)*/?$` <br /> |
| `endSessionEndpoint` _[HttpsUri](#httpsuri)_ | EndSessionEndpoint specifies the URL that redirects a user's browser to in order to initiate a single logout<br />across all applications and the OpenID provider. Users are directed to this endpoint when they access the logout path.<br />This should only be set when the OpenID provider supports RP-Initiated Logout and "openid" is included in the list of scopes.<br />Refer to https://openid.net/specs/openid-connect-rpinitiated-1_0.html#RPLogout for more details. |  | Pattern: `^https://([a-zA-Z0-9]([a-zA-Z0-9\-]\{0,61\}[a-zA-Z0-9])?\.)*[a-zA-Z0-9]([a-zA-Z0-9\-]\{0,61\}[a-zA-Z0-9])?(:[0-9]\{1,5\})?(/[a-zA-Z0-9\-._~!$&'()*+,;=:@%]*)*/?(\?[a-zA-Z0-9\-._~!$&'()*+,;=:@%/?]*)?$` <br /> |
| `cookies` _[OAuth2CookieConfig](#oauth2cookieconfig)_ | Cookies specifies the configuration for the OAuth2 cookies. |  |  |
| `denyRedirect` _[OAuth2DenyRedirectMatcher](#oauth2denyredirectmatcher)_ | DenyRedirectMatcher specifies the matcher to match requests that should be denied redirects to the authorization endpoint.<br />Matching requests will receive a 401 Unauthorized response instead of being redirected.<br />This is useful for AJAX requests where redirects should be avoided. |  |  |


#### Op

_Underlying type:_ _string_

Op represents comparison operators.

_Validation:_
- Enum: [EQ GE LE]

_Appears in:_
- [ComparisonFilter](#comparisonfilter)

| Field | Description |
| --- | --- |
| `EQ` |  |
| `GE` |  |
| `LE` |  |


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


#### PathRegexRewrite



PathRegexRewrite specifies how to rewrite the URL path.



_Appears in:_
- [URLRewrite](#urlrewrite)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `pattern` _string_ | Pattern is the regex pattern that matches the URL path.<br />The pattern must be a valid RE2 regular expression.<br />If the HTTPRoute uses a RegularExpression path match, this field can use capture groups<br />from that match. |  | MaxLength: 1024 <br />MinLength: 1 <br /> |
| `substitution` _string_ | Substitution is the replacement string for the matched pattern.<br />It can include backreferences to captured groups from the pattern (e.g., \1, \2)<br />or named groups (e.g., \g<name>). |  | MaxLength: 1024 <br />MinLength: 1 <br /> |


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


#### Port







_Appears in:_
- [Service](#service)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `port` _integer_ | The port number to match on the Gateway |  | Maximum: 65535 <br />Minimum: 1 <br /> |
| `nodePort` _integer_ | The NodePort to be used for the service. If not specified, a random port<br />will be assigned by the Kubernetes API server. |  | Maximum: 65535 <br />Minimum: 1 <br /> |


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
- [ListenerConfig](#listenerconfig)



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


#### RemoteJWKS







_Appears in:_
- [JWKS](#jwks)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `url` _string_ | URL is the URL of the remote JWKS server, it must be a full FQDN with protocol, host and path.<br />For example, https://example.com/keys |  | MaxLength: 2048 <br />MinLength: 1 <br /> |
| `backendRef` _[BackendObjectReference](https://gateway-api.sigs.k8s.io/reference/spec/#backendobjectreference)_ | BackendRef is reference to the backend of the JWKS server. |  |  |
| `cacheDuration` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | Duration after which the cached JWKS expires.<br />If unspecified, the default cache duration is 5 minutes. |  |  |


#### RequestDecompression



RequestDecompression enables request gzip decompression.



_Appears in:_
- [Compression](#compression)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `disable` _[PolicyDisable](#policydisable)_ | Disables decompression. |  |  |


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


#### ResponseCompression



ResponseCompression configures response compression.



_Appears in:_
- [Compression](#compression)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `disable` _[PolicyDisable](#policydisable)_ | Disables compression. |  |  |


#### ResponseFlagFilter

_Underlying type:_ _[struct{Flags []string "json:\"flags\""}](#struct{flags-[]string-"json:\"flags\""})_

ResponseFlagFilter filters based on response flags.
Based on: https://www.envoyproxy.io/docs/envoy/v1.33.0/api-v3/config/accesslog/v3/accesslog.proto#config-accesslog-v3-responseflagfilter



_Appears in:_
- [FilterType](#filtertype)



#### Retry



Retry defines the retry policy



_Appears in:_
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `retryOn` _[RetryOnCondition](#retryoncondition) array_ | RetryOn specifies the conditions under which a retry should be attempted. |  | Enum: [5xx gateway-error reset reset-before-request connect-failure envoy-ratelimited retriable-4xx refused-stream retriable-status-codes http3-post-connect-failure cancelled deadline-exceeded internal resource-exhausted unavailable] <br />MinItems: 1 <br /> |
| `attempts` _integer_ | Attempts specifies the number of retry attempts for a request.<br />Defaults to 1 attempt if not set.<br />A value of 0 effectively disables retries. | 1 | Minimum: 0 <br /> |
| `perTryTimeout` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | PerTryTimeout specifies the timeout per retry attempt (incliding the initial attempt).<br />If a global timeout is configured on a route, this timeout must be less than the global<br />route timeout.<br />It is specified as a sequence of decimal numbers, each with optional fraction and a unit suffix, such as "1s" or "500ms". |  |  |
| `statusCodes` _[HTTPRouteRetryStatusCode](#httprouteretrystatuscode) array_ | StatusCodes specifies the HTTP status codes in the range 400-599 that should be retried in addition<br />to the conditions specified in RetryOn. |  | Maximum: 599 <br />MinItems: 1 <br />Minimum: 400 <br /> |
| `backoffBaseInterval` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | BackoffBaseInterval specifies the base interval used with a fully jittered exponential back-off between retries.<br />Defaults to 25ms if not set.<br />Given a backoff base interval B and retry number N, the back-off for the retry is in the range [0, (2^N-1)*B].<br />The backoff interval is capped at a max of 10 times the base interval.<br />E.g., given a value of 25ms, the first retry will be delayed randomly by 0-24ms, the 2nd by 0-74ms,<br />the 3rd by 0-174ms, and so on, and capped to a max of 10 times the base interval (250ms). | 25ms |  |


#### RetryBackoff







_Appears in:_
- [ExtSvcRetryPolicy](#extsvcretrypolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `baseInterval` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | BaseInterval specifies the base interval used with a fully jittered exponential back-off between retries. |  |  |
| `maxInterval` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.31/#duration-v1-meta)_ | MaxInterval specifies the maximum interval between retry attempts.<br />Defaults to 10 times the BaseInterval if not set. |  |  |


#### RetryOnCondition

_Underlying type:_ _string_

RetryOnCondition specifies the condition under which retry takes place.

_Validation:_
- Enum: [5xx gateway-error reset reset-before-request connect-failure envoy-ratelimited retriable-4xx refused-stream retriable-status-codes http3-post-connect-failure cancelled deadline-exceeded internal resource-exhausted unavailable]

_Appears in:_
- [Retry](#retry)



#### RetryPolicy

_Underlying type:_ _struct_

Specifies the retry policy of remote data source when fetching fails.
Ref: https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/core/v3/base.proto#envoy-v3-api-msg-config-core-v3-retrypolicy



_Appears in:_
- [AccessLogGrpcService](#accessloggrpcservice)
- [CommonAccessLogGrpcService](#commonaccessloggrpcservice)
- [CommonGrpcService](#commongrpcservice)



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


#### SecretReference



SecretReference identifies a Kubernetes secret containing authentication data.



_Appears in:_
- [BasicAuthPolicy](#basicauthpolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _[ObjectName](#objectname)_ | Name of the secret containing htpasswd data. |  |  |
| `namespace` _[Namespace](#namespace)_ | Namespace of the secret. If not specified, defaults to the namespace of the TrafficPolicy.<br />Note that a secret in a different namespace requires a ReferenceGrant to be accessible. |  | MaxLength: 63 <br />MinLength: 1 <br />Pattern: `^[a-z0-9]([-a-z0-9]*[a-z0-9])?$` <br /> |
| `key` _string_ | Key in the secret that contains the htpasswd data.<br />Defaults to ".htpasswd" if not specified. | .htpasswd | MinLength: 1 <br /> |


#### SelfManagedGateway







_Appears in:_
- [GatewayParametersSpec](#gatewayparametersspec)



#### ServerHeaderTransformation

_Underlying type:_ _string_

ServerHeaderTransformation determines how the server header is transformed.



_Appears in:_
- [HTTPListenerPolicySpec](#httplistenerpolicyspec)
- [HTTPSettings](#httpsettings)

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
| `inclusionList` _StringMatcher array_ | inclusionList specifies which stats to include, using string matchers. |  | MaxItems: 16 <br /> |
| `exclusionList` _StringMatcher array_ | exclusionList specifies which stats to exclude, using string matchers. |  | MaxItems: 16 <br /> |


#### StatusCodeFilter

_Underlying type:_ _[ComparisonFilter](#comparisonfilter)_

StatusCodeFilter filters based on HTTP status code.
Based on: https://www.envoyproxy.io/docs/envoy/v1.33.0/api-v3/config/accesslog/v3/accesslog.proto#envoy-v3-api-msg-config-accesslog-v3-statuscodefilter



_Appears in:_
- [FilterType](#filtertype)



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
- [HTTPSettings](#httpsettings)

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
| `targetRefs` _LocalPolicyTargetReferenceWithSectionName array_ | TargetRefs specifies the target resources by reference to attach the policy to. |  | MaxItems: 16 <br />MinItems: 1 <br /> |
| `targetSelectors` _LocalPolicyTargetSelectorWithSectionName array_ | TargetSelectors specifies the target selectors to select resources to attach the policy to. |  |  |
| `transformation` _[TransformationPolicy](#transformationpolicy)_ | Transformation is used to mutate and transform requests and responses<br />before forwarding them to the destination. |  |  |
| `extProc` _[ExtProcPolicy](#extprocpolicy)_ | ExtProc specifies the external processing configuration for the policy. |  |  |
| `extAuth` _[ExtAuthPolicy](#extauthpolicy)_ | ExtAuth specifies the external authentication configuration for the policy.<br />This controls what external server to send requests to for authentication. |  |  |
| `rateLimit` _[RateLimit](#ratelimit)_ | RateLimit specifies the rate limiting configuration for the policy.<br />This controls the rate at which requests are allowed to be processed. |  |  |
| `cors` _[CorsPolicy](#corspolicy)_ | Cors specifies the CORS configuration for the policy. |  |  |
| `csrf` _[CSRFPolicy](#csrfpolicy)_ | Csrf specifies the Cross-Site Request Forgery (CSRF) policy for this traffic policy. |  |  |
| `headerModifiers` _[HeaderModifiers](#headermodifiers)_ | HeaderModifiers defines the policy to modify request and response headers. |  |  |
| `autoHostRewrite` _boolean_ | AutoHostRewrite rewrites the Host header to the DNS name of the selected upstream.<br />NOTE: This field is only honored for HTTPRoute targets.<br />NOTE: If `autoHostRewrite` is set on a route that also has a [URLRewrite filter](https://gateway-api.sigs.k8s.io/reference/spec/#httpurlrewritefilter)<br />configured to override the `hostname`, the `hostname` value will be used and `autoHostRewrite` will be ignored. |  |  |
| `buffer` _[Buffer](#buffer)_ | Buffer can be used to set the maximum request size that will be buffered.<br />Requests exceeding this size will return a 413 response. |  |  |
| `timeouts` _[Timeouts](#timeouts)_ | Timeouts defines the timeouts for requests<br />It is applicable to HTTPRoutes and ignored for other targeted kinds. |  |  |
| `retry` _[Retry](#retry)_ | Retry defines the policy for retrying requests.<br />It is applicable to HTTPRoutes, Gateway listeners and XListenerSets, and ignored for other targeted kinds. |  |  |
| `rbac` _[Authorization](#authorization)_ | RBAC specifies the role-based access control configuration for the policy.<br />This defines the rules for authorization based on roles and permissions.<br />RBAC policies applied at different attachment points in the configuration<br />hierarchy are not cumulative, and only the most specific policy is enforced. This means an RBAC policy<br />attached to a route will override any RBAC policies applied to the gateway or listener. |  |  |
| `jwt` _[JWTAuthentication](#jwtauthentication)_ | JWT specifies the JWT authentication configuration for the policy.<br />This defines the JWT providers and their configurations. |  |  |
| `urlRewrite` _[URLRewrite](#urlrewrite)_ | UrlRewrite specifies URL rewrite rules for matching requests.<br />NOTE: This field is only honored for HTTPRoute targets. |  |  |
| `compression` _[Compression](#compression)_ | Compression configures response compression (per-route) and request/response<br />decompression (listener-level insertion triggered by route enable).<br />The response compression configuration is only honored for HTTPRoute targets. |  |  |
| `basicAuth` _[BasicAuthPolicy](#basicauthpolicy)_ | BasicAuth specifies the HTTP basic authentication configuration for the policy.<br />This controls authentication using username/password credentials in the Authorization header. |  |  |
| `apiKeyAuthentication` _[APIKeyAuthentication](#apikeyauthentication)_ | APIKeyAuthentication authenticates users based on a configured API Key. |  |  |
| `oauth2` _[OAuth2Policy](#oauth2policy)_ | OAuth2 specifies the configuration to use for OAuth2/OIDC.<br />Note: the OAuth2 filter does not protect against Cross-Site-Request-Forgery attacks on domains with cached<br />authentication (in the form of cookies). It is recommended to pair this with the CSRF policy to prevent<br />malicious social engineering. |  |  |


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


#### URLRewrite



URLRewrite specifies URL rewrite rules using regular expressions.
This allows more flexible and advanced path rewriting based on regex patterns.



_Appears in:_
- [TrafficPolicySpec](#trafficpolicyspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `pathRegex` _[PathRegexRewrite](#pathregexrewrite)_ | Path specifies the path rewrite configuration. |  |  |


#### UpgradeConfig



UpgradeConfig represents configuration for HTTP upgrades.



_Appears in:_
- [HTTPListenerPolicySpec](#httplistenerpolicyspec)
- [HTTPSettings](#httpsettings)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `enabledUpgrades` _string array_ | List of upgrade types to enable (e.g. "websocket", "CONNECT", etc.) |  | MinItems: 1 <br /> |


#### ValidationMode

_Underlying type:_ _string_





_Appears in:_
- [JWT](#jwt)

| Field | Description |
| --- | --- |
| `Strict` | A valid token, issued by a configured issuer, must be present.<br />This is the default option.<br /> |
| `AllowMissing` | If a token exists, validate it.<br />Warning: this allows requests without a JWT token.<br /> |


#### XRateLimitHeadersStandard

_Underlying type:_ _string_

XRateLimitHeadersStandard controls how XRateLimit headers will emitted.



_Appears in:_
- [RateLimitProvider](#ratelimitprovider)

| Field | Description |
| --- | --- |
| `Off` | XRateLimitHeaderOff disables emitting of XRateLimit headers.<br /> |
| `DraftVersion03` | XRateLimitHeaderDraftV03 outputs headers as described in [draft RFC version 03](https://tools.ietf.org/id/draft-polli-ratelimit-headers-03.html).<br /> |


