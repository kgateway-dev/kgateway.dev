Use Common Language Expressions (CEL) expressions to secure access to AI resources. 

## About CEL-based RBAC

Agentgateway proxies use CEL expressions to match requests or responses on specific parameters, such as a request header or source address. If the request matches the condition, it is allowed. Requests that do not match any of the conditions are denied. 

For an overview of supported CEL expressions, see the [agentgateway docs](https://agentgateway.dev/docs/reference/cel/).

## Before you begin

Set up an [agentgateway proxy]({{< link-hextra path="/agentgateway/setup" >}}). 

## Set up access to Gemini

Configure access to an LLM provider such as Gemini. You can use any other LLM provider, an MCP server, or an agent to try out CEL-based RBAC.

{{< reuse "docs/snippets/gemini-setup.md" >}} 

## Set up RBAC permissions

1. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} with your CEL rules. The following example allows requests with the `x-llm: gemini` header.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: rbac
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: google
     rbac:
       policy:
         matchExpressions:
           - "request.headers['x-llm'] == 'gemini'"
   EOF
   ```
   
2. Send a request to the LLM provider API without the `llm` header. Verify that the request is denied with a 403 HTTP response code. 

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}

   ````sh
   curl -vik "$INGRESS_GW_ADDRESS:8080/gemini" -H content-type:application/json  -d '{
     "model": "",
     "messages": [
      {"role": "user", "content": "Explain how AI works in simple terms."}
    ]
   }'
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vik "localhost:8080/gemini" -H content-type:application/json  -d '{
     "model": "",
     "messages": [
      {"role": "user", "content": "Explain how AI works in simple terms."}
    ]
   }'
   ````

   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```console{hl_lines=[11]}
   * upload completely sent off: 109 bytes
   < HTTP/1.1 403 Forbidden
   HTTP/1.1 403 Forbidden
   < content-type: text/plain
   content-type: text/plain
   < content-length: 20
   content-length: 20
   < 

   * Connection #0 to host localhost left intact
   authorization failed
   ```  
   
3. Send another request to the LLM provider. This time, you include the `llm` header. Verify that the request succeeds with a 200 HTTP response code. 

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}

   ```sh
   curl -vik "$INGRESS_GW_ADDRESS:8080/gemini" \
     -H "content-type: application/json" \
     -H "x-llm: gemini" -d '{
     "model": "",
     "messages": [
      {"role": "user", "content": "Explain how AI works in simple terms."}
    ]
   }'
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vik "localhost:8080/gemini" \
     -H "content-type: application/json" \
     -H "x-llm: gemini" -d '{
     "model": "",
     "messages": [
      {"role": "user", "content": "Explain how AI works in simple terms."}
    ]
   }'
   ````

   {{% /tab %}}
   {{< /tabs >}}
   

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```shell
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} -n {{< reuse "docs/snippets/namespace.md" >}} -l app=agentgateway
kubectl delete httproute google -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete backend google -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete secret google-secret -n {{< reuse "docs/snippets/namespace.md" >}}
```