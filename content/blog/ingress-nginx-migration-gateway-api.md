---
title: What Comes After Ingress NGINX? A Migration Guide to Gateway API
toc: false
author: Michael Levan
publishDate: 2026-01-27T10:00:00-00:00
excludeSearch: true
---
With the latest news of the Ingress NGINX Controller migration, thousands of engineers are attempting to figure out how they can migrate to Gateway API, the new standard for gateway traffic to various applications running within Kubernetes. Because teams could have hundreds or more Ingress manifests using the Controller, a method of turning those manifests into Gateway API core and implementation-specific objects is necessary.

In this blog post, you’ll learn a bit about the “why” behind the deprecation and how to migrate your Ingress NGINX configurations.

## Why The Deprecation?
When Kubernetes first came out, there was a need to show an example of how to manage ingress traffic. Because of that, Ingress NGINX was created. However, because of its breadth of usage and support across the various cloud providers, it ended up becoming a standard. Since the standard was created, there were still only a handful of people working on maintenance and new features around Ingress NGINX.

## Implementing Ingress2gateway Via Kgateway
With what you’ve learned so far throughout this blog post regarding the Ingress NGINX retirement, you may be thinking to yourself, “Alright, so how do I keep the lights on and remove the Controller?” 

The answer is by migrating to Gateway API. 

But because that would be incredibly cumbersome to do manually, you can use the Ingress2gateway migration tool. Since Gateway API was designed to be extensible, migrating most production use cases also requires implementation-specific objects. For example, migrating an Ingress with the `“nginx.ingress.kubernetes.io/auth-type: basic”` annotation requires an implementation-specific object such as kgateway’s TrafficPolicy.

> [!NOTE]
> Technically, you can keep the underlying Ingress object and change the ingressClassName. Why not just do that? Because the Kubernetes project is moving toward Gateway API. In short, there’s no reason to migrate to something that’s considered deprecated by the community. If you just rename the Ingress objects, you're creating more tech debt for yourself down the road when you eventually have to migrate.

In the next two sections, you’ll first deploy an object with Ingress NGINX into your Kubernetes cluster and then you’ll learn how to migrate it to **kgateway**, a [conformant Gateway API implementation](https://gateway-api.sigs.k8s.io/implementations/#kgateway).

## Using The Migration Tool
The first step is to download the migration tool. You can find the installation options for your Operating System in the [docs here]({{< relref "docs/envoy/latest/migrate/install/_index.md" >}}).

You can verify that the command works by running the build/binary, as in the following output.

```bash
./ingress2gateway
Convert Ingress manifests to Gateway API manifests

Usage:
  ingress2gateway [command]

Available Commands:
  completion  Generate the autocompletion script for the specified shell
  help        Help about any command
  print       Prints Gateway API objects generated from ingress and provider-specific resources.
  version     Print the version number of ingress2gateway
```

With the binary, you can use the print command with the providers and emitter flags to do the following:

- Specify that you want the source to be the Ingress NGINX Controller.
- Choose what you want to migrate to (the "emitter"), which in this case is kgateway using the standard from Kubernetes Gateway API CRDs (kgateway is the current supported implementation in this downstream fork).
- Convert the source objects to Kubernetes Gateway API objects that work with the chosen emitter.

For example, to print the Kubernetes objects that the conversion produces, run the following command.

```bash
./ingress2gateway print --providers=ingress-nginx --emitter=kgateway
```

Next, you’ll find three key use cases that many organizations deploy within production environments and how to convert them with ingress2gateway.

## Deploying Ingress NGINX Implementations

In this section, you'll cover three key scenarios that many production-level environments use:

1. TLS/SSL
2. Auth
3. CORS

The goal with the three test cases is to ensure that the ingress2gateway tool works as expected for various use cases depending on your environment.

### Deployment Setup

Deploy a test application, which is only a simple HTTP service. It runs in a Kubernetes Deployment and has a Kubernetes Service.

```bash
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-app
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api-app
  template:
    metadata:
      labels:
        app: api-app
    spec:
      containers:
      - name: httpbin
        image: kennethreitz/httpbin
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: api-service
  namespace: default
spec:
  selector:
    app: api-app
  ports:
  - port: 80
    targetPort: 80
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: admin-app
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: admin-app
  template:
    metadata:
      labels:
        app: admin-app
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: admin-service
  namespace: default
spec:
  selector:
    app: admin-app
  ports:
  - port: 80
    targetPort: 80
EOF
```

### Use Case 1: TLS/SSL
1. Create certs for testing.
   
   ```bash
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout tls.key -out tls.crt -subj "/CN=localhost/O=dev”
   ```

2. Create a new Kubernetes secret for TLS certs.
   
   ```bash
   kubectl create secret tls my-tls-cert \
     --cert=tls.crt \
     --key=tls.key
   ```

3. Apply the Ingress configuration.
   
   > [!NOTE]
   > Notice the annotation that specifies which control plane/gateway you’re switching to. The reason is to ensure that the Gateway object you’re planning on using is supported and works as expected—using the Kubernetes Gateway API CRDs allows you to stay as agnostic as possible.

   ```bash
   kubectl apply -f - <<EOF
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: tls-ingress
     namespace: default
     annotations:
       nginx.ingress.kubernetes.io/ssl-redirect: "true"
       nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
   spec:
     ingressClassName: nginx
     tls:
     - hosts:
       - api.example.com
       secretName: my-tls-cert
     rules:
     - host: api.example.com
       http:
         paths:
         - path: /
           pathType: Prefix
           backend:
             service:
               name: api-service
               port:
                 number: 80
   EOF
   ```

4. Run the ingress2gateway tool. You should see output similar to the following.

   ```bash
   ./ingress2gateway print --providers=ingress-nginx --emitter=kgateway
   ```

   ```yaml
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     annotations:
       gateway.networking.k8s.io/generator: ingress2gateway-v0.3.0
     name: nginx
     namespace: default
   spec:
     gatewayClassName: kgateway
     listeners:
     - hostname: api.example.com
       name: api-example-com-http
       port: 80
       protocol: HTTP
     - hostname: api.example.com
       name: api-example-com-https
       port: 443
       protocol: HTTPS
       tls:
         certificateRefs:
         - group: null
           kind: null
           name: my-tls-cert
   status:
     parents: []
   ---
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     annotations:
       gateway.networking.k8s.io/generator: ingress2gateway-v0.3.0
     name: tls-ingress-api-example-com-https
     namespace: default
   spec:
     hostnames:
     - api.example.com
     parentRefs:
     - name: nginx
       sectionName: api-example-com-https
     rules:
     - backendRefs:
       - name: api-service
         port: 80
       matches:
       - path:
           type: PathPrefix
           value: /
   status:
     parents: []
   ---
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     annotations:
       gateway.networking.k8s.io/generator: ingress2gateway-v0.3.0
     name: tls-ingress-api-example-com-http-redirect
     namespace: default
   spec:
     hostnames:
     - api.example.com
     parentRefs:
     - name: nginx
       sectionName: api-example-com-http
     rules:
     - filters:
       - requestRedirect:
           scheme: https
           statusCode: 301
         type: RequestRedirect
       matches:
       - path:
           type: PathPrefix
           value: /
   ```

### Functional Tests

1. Apply the new objects that were printed above.

   ```bash
   ./ingress2gateway print --providers=ingress-nginx --emitter=kgateway | kubectl apply -f -
   ```

2. Verify the Gateway is accepted.

   ```bash
   kubectl get gateway nginx -o jsonpath='{.status.conditions[?(@.type=="Accepted")].status}'
   ```

3. Ensure that the HTTP Routes are attached.

   ```bash
   kubectl get httproute -o jsonpath='{range .items[*]}{.metadata.name}: {.status.parents[0].conditions[?(@.type=="Accepted")].status}{"\n"}{end}'
   ```

4. Get the IP address of the Gateway.

   ```bash
   GATEWAY_IP=$(kubectl get gateway nginx -o jsonpath='{.status.addresses[0].value}') echo $GATEWAY_IP
   ```

5. Test the HTTP redirect (should return a 301).

   ```bash
   curl -I --resolve api.example.com:80:$GATEWAY_IP http://api.example.com/
   ```

6. Test the HTTPS route.

   ```bash
   curl -k --resolve api.example.com:443:$GATEWAY_IP https://api.example.com/
   ```

| Test | Result |
|------|--------|
| Gateway accepted | True |
| HTTPRoutes attached | Both True |
| HTTP redirect | 301 to https://api.example.com/ |
| HTTPS route | Returns httpbin.org page from backend |


## Use Case 2: Auth
1. Create a username and password (the secret is stored in a Kubernetes secret).

   ```bash
   htpasswd -c auth admin
   kubectl create secret generic basic-auth --from-file=auth
   ```

2. Apply the Ingress configuration.

   ```bash
   kubectl apply -f - <<EOF
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: auth-ingress
     namespace: default
     annotations:
       nginx.ingress.kubernetes.io/auth-type: basic
       nginx.ingress.kubernetes.io/auth-secret: basic-auth
       nginx.ingress.kubernetes.io/auth-secret-type: auth-file
   spec:
     ingressClassName: nginx
     rules:
     - host: admin.example.com
       http:
         paths:
         - path: /
           pathType: Prefix
           backend:
             service:
               name: admin-service
               port:
                 number: 80
   EOF
   ```

3. Use the ingress2gateway tool to convert it.

   ```bash
   ./ingress2gateway print --providers=ingress-nginx --emitter=kgateway
   ```

   You should see output similar to the following.

   ```yaml
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     annotations:
       gateway.networking.k8s.io/generator: ingress2gateway-v0.3.0
     name: nginx
     namespace: default
   spec:
     gatewayClassName: kgateway
     listeners:
     - hostname: admin.example.com
       name: admin-example-com-http
       port: 80
       protocol: HTTP
   status: {}
   ---
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     annotations:
       gateway.networking.k8s.io/generator: ingress2gateway-v0.3.0
     name: auth-ingress-admin-example-com
     namespace: default
   spec:
     hostnames:
     - admin.example.com
     parentRefs:
     - name: nginx
     rules:
     - backendRefs:
       - name: admin-service
         port: 80
       matches:
       - path:
           type: PathPrefix
           value: /
   status:
     parents: []
   ---
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: TrafficPolicy
   metadata:
     name: auth-ingress
     namespace: default
   spec:
     basicAuth:
       secretRef:
         key: auth
         name: basic-auth
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: auth-ingress-admin-example-com
   ```

### Functional Tests
1. Create a basic-auth secret.

   ```bash
   htpasswd -nbB admin testpass123 > /tmp/htpasswd
   kubectl create secret generic basic-auth --from-file=.htaccess=/tmp/htpasswd -n default
   ```

2. Apply the new converted objects.

   ```bash
   ./ingress2gateway print --providers=ingress-nginx --emitter=kgateway | kubectl apply -f -
   ```

3. Verify the Gateway is accepted.

   ```bash
   kubectl get gateway nginx -o jsonpath='{.status.conditions[?(@.type=="Accepted")].status}'
   ```

4. Ensure the HTTP route is attached.

   ```bash
   kubectl get httproute auth-ingress-admin-example-com -o jsonpath='{.status.parents[0].conditions[?(@.type=="Accepted")].status}'
   ```

5. Get the Gateway IP.

   ```bash
   GATEWAY_IP=$(kubectl get gateway nginx -o jsonpath='{.status.addresses[0].value}') echo $GATEWAY_IP
   ```

6. Test without auth. This should fail with a 401.

   ```bash
   curl -I --resolve admin.example.com:80:$GATEWAY_IP http://admin.example.com/
   ```

7. Test with auth.

   ```bash
   curl --resolve admin.example.com:80:$GATEWAY_IP -u "admin:testpass123" http://admin.example.com/
   ```


| Test | Result |
|------|--------|
| Gateway accepted | True |
| HTTPRoute attached | True |
| TrafficPolicy attached | True |
| Request without auth | 401 Unauthorized |
| Request with valid auth (admin:testpass123) | 200 OK |



## Use Case 3: CORS
1. Apply the Ingress configuration below.

   ```bash
   kubectl apply -f - <<EOF
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: cors-ingress
     namespace: default
     annotations:
       nginx.ingress.kubernetes.io/enable-cors: "true"
       nginx.ingress.kubernetes.io/cors-allow-origin: "https://app.example.com,https://dashboard.example.com"
       nginx.ingress.kubernetes.io/cors-allow-methods: "GET,POST,PUT,DELETE,OPTIONS"
       nginx.ingress.kubernetes.io/cors-allow-headers: "Authorization,Content-Type,X-Requested-With"
       nginx.ingress.kubernetes.io/cors-expose-headers: "X-Custom-Header,X-Request-ID"
       nginx.ingress.kubernetes.io/cors-allow-credentials: "true"
       nginx.ingress.kubernetes.io/cors-max-age: "7200"
   spec:
     ingressClassName: nginx
     rules:
     - host: api.example.com
       http:
         paths:
         - path: /v1
           pathType: Prefix
           backend:
             service:
               name: api-service
               port:
                 number: 80
   EOF
   ```

2. Run the `ingress2gateway` tool.

   ```bash
   ./ingress2gateway print --providers=ingress-nginx --emitter=kgateway
   ```

   You should see output similar to the following.

   ```yaml
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     annotations:
       gateway.networking.k8s.io/generator: ingress2gateway-v0.3.0
     name: nginx
     namespace: default
   spec:
     gatewayClassName: kgateway
     listeners:
     - hostname: admin.example.com
       name: admin-example-com-http
       port: 80
       protocol: HTTP
     - hostname: api.example.com
       name: api-example-com-http
       port: 80
       protocol: HTTP
   status: {}
   ---
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     annotations:
       gateway.networking.k8s.io/generator: ingress2gateway-v0.3.0
     name: auth-ingress-admin-example-com
     namespace: default
   spec:
     hostnames:
     - admin.example.com
     parentRefs:
     - name: nginx
     rules:
     - backendRefs:
       - name: admin-service
         port: 80
       matches:
       - path:
           type: PathPrefix
           value: /
   status:
     parents: []
   ---
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     annotations:
       gateway.networking.k8s.io/generator: ingress2gateway-dev
     name: cors-ingress-api-example-com
     namespace: default
   spec:
     hostnames:
     - api.example.com
     parentRefs:
     - name: nginx
     rules:
     - backendRefs:
       - name: api-service
         port: 80
       matches:
       - path:
           type: PathPrefix
           value: /v1
   status:
     parents: []
   ---
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: TrafficPolicy
   metadata:
     name: auth-ingress
     namespace: default
   spec:
     basicAuth:
       secretRef:
         key: auth
         name: basic-auth
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: auth-ingress-admin-example-com
   status:
     ancestors: null
   ---
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: TrafficPolicy
   metadata:
     name: cors-ingress
     namespace: default
   spec:
     cors:
       allowCredentials: true
       allowHeaders:
       - Authorization
       - Content-Type
       - X-Requested-With
       allowMethods:
       - GET
       - POST
       - PUT
       - DELETE
       - OPTIONS
       allowOrigins:
       - https://app.example.com
       - https://dashboard.example.com
       exposeHeaders:
       - X-Custom-Header
       - X-Request-ID
       maxAge: 7200
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: cors-ingress-api-example-com
   status:
     ancestors: null
   ```

### Functional Tests
1. Apply the new converted objects.

   ```bash
   ./ingress2gateway print --providers=ingress-nginx --emitter=kgateway | kubectl apply -f -
   ```

2. Verify the Gateway is accepted.

   ```bash
   kubectl get gateway nginx -o jsonpath='{.status.conditions[?(@.type=="Accepted")].status}'
   ```

3. Confirm the HTTP route is attached.

   ```bash
   kubectl get httproute cors-ingress-api-example-com -o jsonpath='{.status.parents[0].conditions[?(@.type=="Accepted")].status}'
   ```

4. Capture the Gateway IP.

   ```bash
   GATEWAY_IP=$(kubectl get gateway nginx -o jsonpath='{.status.addresses[0].value}') echo $GATEWAY_IP
   ```

5. Test the CORS preflight request. A 200 is expected.

   ```bash
   curl -I --resolve api.example.com:80:$GATEWAY_IP -X OPTIONS -H "Origin: https://app.example.com" -H "Access-Control-Request-Method: POST" -H "Access-Control-Request-Headers: Authorization,Content-Type" http://api.example.com/v1/
   ```

6. Test with a disallowed origin.

   ```bash
   curl -I --resolve api.example.com:80:$GATEWAY_IP -X OPTIONS -H "Origin: https://evil.example.com" -H "Access-Control-Request-Method: POST" http://api.example.com/v1/
   ```

7. Test with an allowed origin.

   ```bash
   curl -I --resolve api.example.com:80:$GATEWAY_IP -H "Origin: https://app.example.com" http://api.example.com/v1/
   ```

| Test | Result |
|------|--------|
| Gateway accepted | True |
| HTTPRoutes attached | Both True |
| Policies attached | Both True |

**CORS Tests**

| Test | Result |
|------|--------|
| Preflight with allowed origin (https://app.example.com) | 200 OK with correct CORS headers |
| Preflight with disallowed origin | Passed through to backend (see note below) |

**Basic Auth Tests**

| Test | Result |
|------|--------|
| Request without credentials | 401 Unauthorized |
| Request with valid credentials (admin:testpass123) | 200 OK |





## Conclusion
As with all technology stacks, new pieces of the puzzle get released and sometimes replace existing implementations. Because of the maintenance needs around Ingress NGINX—it was hard to troubleshoot, difficult to standardize across projects, and only a handful of people were working on it—the new standard, Kubernetes Gateway API, was released with the goal of being an agnostic CRD to work with any vendor and any gateway. The concern with that was there was no clear migration step as thousands of engineers were using Ingress NGINX, so a tool to move from that to the new Kubernetes Gateway API standard was necessary. The specifications in this tool (emitter design and initial implementation) have recently moved to the upstream ingress2gateway project as well. In this blog post, you learned how to perform the migration on an object using the Ingress NGINX Controller to the new Gateway API standard.

## Keep in Touch

If you have any questions or just want to learn more about kgateway, feel free to reach out to us on [in the `#kgateway` channel in the CNCF Slack](https://cloud-native.slack.com/archives/C080D3PJMS4) or [our community meetings](https://github.com/kgateway-dev/community/blob/main/README.md#community-meetings)! There is a vibrant, open-source community in both places with people eager to chat and learn.