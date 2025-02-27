---
title: TCP listeners
weight: 30
---

The following guide deploys a sample TCP echo app, sets up a TCP listener on the gateway, and creates a TCPRoute to the sample app.

{{% callout type="warning" %}}
TCPRoutes are an experimental feature in the [upstream Kubernetes Gateway API](https://gateway-api.sigs.k8s.io/guides/tcp), and are subject to change.
{{% /callout %}}

## Before you begin

1. Follow the [Get started guide](/docs/quickstart) to install {{% reuse "docs/snippets/product-name.md" %}}.

2. Install the experimental channel of the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} so that you can use TCPRoutes.

   ```shell
   kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.2.0/experimental-install.yaml
   ```

3. Deploy the sample TCP echo app.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: v1
   kind: Pod
   metadata:
     labels:
       app: tcp-echo
     name: tcp-echo
     namespace: default
   spec:
     containers:
     - image: soloio/tcp-echo:latest
       imagePullPolicy: IfNotPresent
       name: tcp-echo
     restartPolicy: Always
   ---
   apiVersion: v1
   kind: Service
   metadata:
     labels:
       app: tcp-echo
     name: tcp-echo
     namespace: default
   spec:
     ports:
     - name: http
       port: 1025
       protocol: TCP
       targetPort: 1025
     selector:
       app: tcp-echo
   EOF
   ```

## Set up the Gateway for TCP routes {#tcp-setup}

Create a TCP listener so that the gateway can route TCP traffic. In the following example, all TCP streams on port 8000 of the gateway are forwarded to port 1025 of the example TCP echo service.

1. Create a Gateway resource with a TCP listener. 
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: tcp-gateway
     namespace: gloo-system
     labels:
       app: tcp-echo
   spec:
     gatewayClassName: gloo-gateway
     listeners:
     - protocol: TCP
       port: 8000
       name: tcp
       allowedRoutes:
         kinds:
         - kind: TCPRoute
   EOF
   ```

   |Setting|Description|
   |--|--|
   |`spec.gatewayClassName`|The name of the Kubernetes gateway class that you want to use to configure the gateway. When you set up {{% reuse "docs/snippets/product-name.md" %}}, a default gateway class is set up for you. To view the gateway class configuration, see [Gateway classes and types](docs/about/class-type/). |
   |`spec.listeners`|Configure the listeners for this gateway. In this example, you configure a TCP gateway that listens for incoming traffic on port 8000. The gateway can serve TCPRoutes from any namespace. |

2. Check the status of the gateway to make sure that your configuration is accepted and no conflicts exist in your cluster. 
   
   ```sh
   kubectl get gateway tcp-gateway -n gloo-system -o yaml
   ```

   Example output:

   ```console
   status:
     addresses:
     - type: IPAddress
       value: ${INGRESS_GW_ADDRESS}
     conditions:
     - lastTransitionTime: "2024-11-20T16:01:25Z"
       message: ""
       observedGeneration: 2
       reason: Accepted
       status: "True"
       type: Accepted
     - lastTransitionTime: "2024-11-20T16:01:25Z"
       message: ""
       observedGeneration: 2
       reason: Programmed
       status: "True"
       type: Programmed
   ```

3. Create a TCPRoute resource for the TCP echo app that is served by the gateway that you created.
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1alpha2
   kind: TCPRoute
   metadata:
     name: tcp-route-echo
     namespace: gloo-system
     labels:
       app: tcp-echo
   spec:
     parentRefs:
       - name: tcp-gateway
         namespace: gloo-system
         sectionName: tcp
     rules:
       - backendRefs:
           - name: tcp-echo
             port: 1025
   EOF
   ```

4. Verify that the TCPRoute is applied successfully. 
   
   ```sh
   kubectl get tcproute/tcp-route-echo -n gloo-system -o yaml
   ```

   Example output:
   
   ```console
   status:
     parents:
     - conditions:
       - lastTransitionTime: "2024-11-21T16:22:52Z"
         message: ""
         observedGeneration: 1
         reason: Accepted
         status: "True"
         type: Accepted
       - lastTransitionTime: "2024-11-21T16:22:52Z"
         message: ""
         observedGeneration: 1
         reason: ResolvedRefs
         status: "True"
         type: ResolvedRefs
       controllerName: solo.io/gloo-gateway
       parentRef:
         group: gateway.networking.k8s.io
         kind: Gateway
         name: tcp-gateway
         sectionName: tcp
   ```

5. Get the external address of the gateway and save it in an environment variable.
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n gloo-system gloo-proxy-tcp-gateway -o jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS   
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   kubectl port-forward deployment/gloo-proxy-tcp-gateway -n gloo-system 8080:8080
   ```
   {{% /tab %}}
   {{< /tabs >}}

6. Send a TCP request to the external address of the TCP gateway on port 8000. You might use a tool such as telnet or netcat as in the following example.

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   nc -v $INGRESS_GW_ADDRESS 8000
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   nc -v localhost 8080
   ```
   {{% /tab %}}
   {{< /tabs >}} 

   Example output:

   ```console
   Connection to ${INGRESS_GW_ADDRESS} port 8000 [tcp/irdmi] succeeded!
   ```

7. Enter any string to verify that the TCP echo service "echoes," returning the same string back.

   ```console
   hello
   ```

   Example output:

   ```console
   hello
   hello
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```shell
kubectl delete -A gateways,tcproutes,pod,svc -l app=tcp-echo
```