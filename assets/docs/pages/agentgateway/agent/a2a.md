With {{< reuse "docs/snippets/agentgateway.md" >}}, you can route to agent-to-agent (A2A) servers and expose their tools securely.

## Before you begin

{{< reuse "docs/snippets/agentgateway-prereq.md" >}}

<!-- Steps to build image locally from kgateway repo
## Step 1: Deploy an A2A server {#a2a-server}

Deploy an A2A server that you want agentgateway to proxy traffic to.

1. Clone the [kgateway](https://github.com/kgateway-dev/kgateway) repository.

   ```sh
   git clone https://github.com/kgateway-dev/kgateway.git
   ```

2. From the root directory, build the sample A2A server.

   ```sh
   VERSION={{< reuse "docs/versions/patch-dev.md" >}} make test-a2a-agent-docker
   ```

3. Load the image into your cluster. The following `make` command assumes that you are using a local Kind cluster.

   ```sh
   CLUSTER_NAME=<your-cluster-name> VERSION={{< reuse "docs/versions/patch-dev.md" >}} make kind-load-test-a2a-agent
   ```

4. Deploy the A2A server. Notice that the Service uses the `appProtocol: kgateway.dev/a2a` setting. This way, kgateway configures the agentgateway proxy to use  the A2A protocol.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: a2a-agent
     labels:
       app: a2a-agent
   spec:
     selector:
       matchLabels:
         app: a2a-agent
     template:
       metadata:
         labels:
           app: a2a-agent
       spec:
         containers:
           - name: a2a-agent
             image: ghcr.io/kgateway-dev/test-a2a-agent:{{< reuse "docs/versions/patch-dev.md" >}}
             ports:
               - containerPort: 9090
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: a2a-agent
   spec:
     selector:
       app: a2a-agent
     type: ClusterIP
     ports:
       - protocol: TCP
         port: 9090
         targetPort: 9090
         appProtocol: kgateway.dev/a2a
   EOF
   ```
-->

## Step 1: Deploy an A2A server {#a2a-server}

Deploy an A2A server that you want {{< reuse "docs/snippets/agentgateway.md" >}} to proxy traffic to. Notice that the Service uses the `appProtocol: kgateway.dev/a2a` setting. This way, {{< reuse "docs/snippets/kgateway.md" >}} configures the {{< reuse "docs/snippets/agentgateway.md" >}} proxy to use the A2A protocol.

```yaml
kubectl apply -f- <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: a2a-agent
  labels:
    app: a2a-agent
spec:
  selector:
    matchLabels:
      app: a2a-agent
  template:
    metadata:
      labels:
        app: a2a-agent
    spec:
      containers:
        - name: a2a-agent
          image: gcr.io/solo-public/docs/test-a2a-agent:latest
          ports:
            - containerPort: 9090
---
apiVersion: v1
kind: Service
metadata:
  name: a2a-agent
spec:
  selector:
    app: a2a-agent
  type: ClusterIP
  ports:
    - protocol: TCP
      port: 9090
      targetPort: 9090
      appProtocol: kgateway.dev/a2a
EOF
```

## Step 2: Route with agentgateway {#agentgateway}

Route to the A2A server with {{< reuse "docs/snippets/agentgateway.md" >}}.

1. Create a Gateway resource that uses the `{{< reuse "docs/snippets/agw-gatewayclass.md" >}}` GatewayClass. Kgateway automatically creates an {{< reuse "docs/snippets/agentgateway.md" >}} proxy for you.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: agentgateway
   spec:
     gatewayClassName: {{< reuse "/docs/snippets/agw-gatewayclass.md" >}}
     listeners:
     - protocol: HTTP
       port: 80
       name: http
   EOF
   ```

2. Verify that the Gateway is created successfully. You can also review the external address that is assigned to the Gateway. Note that depending on your environment it might take a few minutes for the load balancer service to be assigned an external address. If you are using a local Kind cluster without a load balancer such as `metallb`, you might not have an external address.

   ```sh
   kubectl get gateway agentgateway
   ```

   Example output: 
   
   ```txt
   NAME           CLASS          ADDRESS                                  PROGRAMMED   AGE
   agentgateway   agentgateway   1234567890.us-east-2.elb.amazonaws.com   True         93s
   ```

3. Create an HTTPRoute resource that routes incoming traffic to the A2A server.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: a2a
   spec:
     parentRefs:
       - name: agentgateway
     rules:
       - backendRefs:
           - name: a2a-agent
             port: 9090
   EOF
   ```

## Step 3: Verify the connection {#verify}

1. Get the agentgateway address.
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get gateway agentgateway -o=jsonpath="{.status.addresses[0].value}")
   echo $INGRESS_GW_ADDRESS
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing"%}}
   ```sh
   kubectl port-forward deployment/agentgateway 8080:80
   ```
   {{% /tab %}}
   {{< /tabs >}}

2. As a user, send a request to the A2A server. As an assistant, the agent echoes back the message that you sent.

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -X POST http://$INGRESS_GW_ADDRESS/ \
     -H "Content-Type: application/json" \
       -v \
       -d '{
     "jsonrpc": "2.0",
     "id": "1",
     "method": "tasks/send",
     "params": {
       "id": "1",
       "message": {
         "role": "user",
         "parts": [
           {
             "type": "text",
             "text": "hello gateway!"
           }
         ]
       }
     }
     }'
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing"%}}
   ```sh
   curl -X POST http://localhost:8080/ \
     -H "Content-Type: application/json" \
       -v \
       -d '{
     "jsonrpc": "2.0",
     "id": "1",
     "method": "tasks/send",
     "params": {
       "id": "1",
       "message": {
         "role": "user",
         "parts": [
           {
             "type": "text",
             "text": "hello gateway!"
           }
         ]
       }
     }
     }'
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:

   ```json
   {
     "jsonrpc": "2.0",
     "id": "1",
     "result": {
       "id": "1",
       "message": {
         "role": "assistant",
         "parts": [
           {
             "type": "text",
             "text": "hello gateway!"
           }
         ]
       }
     }
   }
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete Deployment a2a-agent
kubectl delete Service a2a-agent
kubectl delete Gateway agentgateway
kubectl delete HTTPRoute a2a
```