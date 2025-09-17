Dynamically resolve upstream hosts at request time.

{{< callout >}}
{{< reuse "docs/snippets/proxy-kgateway.md" >}}
{{< /callout >}}

## About Dynamic Forward Proxy

Dynamic Forward Proxy (DFP) is a filter in Envoy that allows a gateway proxy to act as a generic HTTP(S) forward proxy without the need to preconfigure all possible upstream hosts. Instead, the DFP dynamically resolves the upstream host at request time by using DNS. 

DFPs are especially useful in highly dynamic environments where services come up and down frequently. Such churn makes it hard for a service registry to list all available endpoints at a given time. With DFP, you do not need to have pre-defined destinations. This approach gives you more flexibility to resolve endpoints as the request comes in. 
	
Another common use case for DFPs is to control and monitor all egress traffic. For example, you can apply policies, such as rate limiting, authentication, authorization, and access logging. You can also easily access metrics for the egress traffic that is routed through the forward proxy. 

DFPs are configured in a Backend resource and an HTTPRoute that routes traffic to the DFP Backend. If a request reaches the gateway proxy, the proxy extracts the host header value from the request and uses DNS to resolve the host to an IP address. Then, the request is forwarded to the resolved IP address.

### Considerations

DFPs offer great flexibility for defining routing patterns for your upstream hosts. However, consider the following downsides when using a DFP:

* You cannot configure failover or client-side load balancing policies for DFP-configured routes because no pre-defined upstream hosts exist that determine the desired upstream service.
* DNS resolution is done at runtime, which can have performance implications. If Envoy detects a new domain name, Envoy pauses the request and synchronously resolves this domain to get the IP address of the endpoint. Then, Envoy caches the IP address locally. 


## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up a Dynamic Forward Proxy

1. Create a Backend for the Dynamic Forward Proxy. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     name: dfp-backend
     namespace: httpbin
   spec:
     type: DynamicForwardProxy
     dynamicForwardProxy: {}
   EOF
   ```

2. Create an HTTPRoute that routes incoming traffic to the DFP Backend. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     namespace: httpbin
     name: dfp-httproute
   spec:
     parentRefs:
       - name: http
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     rules:
       - backendRefs:
           - name: dfp-backend
             group: gateway.kgateway.dev
             kind: Backend
   EOF
   ```

3. Send a request to a hostname of your choice, such as `httpbin.org`. Verify that your gateway proxy successfully resolves the `httpbin.org` host and returns its welcome page.
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080 -H "host: httpbin.org" 
   ```
   {{% /tab %}}
   {{% tab tabName="Port forward for local testing" %}}
   ```sh
   curl -vik http://localhost:8080 -H "host: httpbin.org"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```console
   * Request completely sent off
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   ...
   <!DOCTYPE html>
   <html lang="en">

   <head>
        <meta charset="UTF-8">
        <title>httpbin.org</title>
        <link href="https://fonts.googleapis.com/css?family=Open+Sans:400,700|Source+Code+Pro:300,600|Titillium+Web:400,600,700"
            rel="stylesheet">
        <link rel="stylesheet" type="text/css" href="/flasgger_static/swagger-ui.css">
        <link rel="icon" type="image/png" href="/static/favicon.ico" sizes="64x64 32x32 16x16" />
        <style>
   ...
   ```
   
## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

1. Remove the DFP Backend. 
   ```sh
   kubectl delete backend dfp-backend -n httpbin
   ```

2. Remove the HTTPRoute. 
   ```sh
   kubectl delete httproute dfp-httproute -n httpbin
   ```




