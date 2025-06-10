---
title: TCP listeners
weight: 10
---

The following guide deploys a sample TCP echo app, sets up a TCP listener on the gateway, and creates a [TCPRoute](https://gateway-api.sigs.k8s.io/guides/tcp) to the sample app.

{{% callout type="warning" %}}
{{< reuse "docs/versions/warn-experimental.md" >}}
{{% /callout %}}

## Before you begin

1. Follow the [Get started guide](/docs/quickstart) to install kgateway.

2. Install the experimental channel of the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} so that you can use TCPRoutes.

   ```shell
   kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.3.0/experimental-install.yaml
   ```

3. {{< reuse "docs/snippets/prereq-listenerset.md" >}}

   **ListenerSets**: {{< reuse "docs/versions/warn-2-1-only.md" >}} Also, you must install the experimental channel of the Kubernetes Gateway API at version 1.3 or later.

4. Deploy the sample TCP echo app.

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

{{< tabs items="Gateway listeners,ListenerSets (experimental)" >}}
{{% tab %}}
1. Create a Gateway resource with a TCP listener. 
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: tcp-gateway
     namespace: kgateway-system
     labels:
       app: tcp-echo
   spec:
     gatewayClassName: kgateway
     listeners:
     - protocol: TCP
       port: 8000
       name: tcp
       allowedRoutes:
         kinds:
         - kind: TCPRoute
   EOF
   ```

   {{< reuse "docs/snippets/review-table.md" >}}

   |Setting|Description|
   |--|--|
   |`spec.gatewayClassName`|The name of the Kubernetes gateway class that you want to use to configure the gateway. When you set up kgateway, a default gateway class is set up for you. To view the gateway class configuration, see [Gateway classes and types](docs/about/class-type/). |
   |`spec.listeners`|Configure the listeners for this gateway. In this example, you configure a TCP gateway that listens for incoming traffic on port 8000. The gateway can serve TCPRoutes from any namespace. |

{{% /tab %}}
{{% tab %}}

{{% callout type="warning" %}}
{{< reuse "docs/versions/warn-2-1-only.md" >}} Also, you must install the experimental channel of the Kubernetes Gateway API at version 1.3 or later.
{{% /callout %}}

1. Create a Gateway that enables the attachment of ListenerSets.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: tcp-gateway
     namespace: kgateway-system
     labels:
       app: tcp-echo
   spec:
     gatewayClassName: kgateway
     allowedListeners:
       namespaces:
         from: All
     listeners:
     - protocol: TCP
       port: 80
       name: generic-tcp
       allowedRoutes:
         kinds:
         - kind: TCPRoute
   EOF
   ```

   {{< reuse "docs/snippets/review-table.md" >}}

   |Setting|Description|
   |---|---|
   |`spec.gatewayClassName`|The name of the Kubernetes gateway class that you want to use to configure the gateway. When you set up kgateway, a default gateway class is set up for you. |
   |`spec.allowedListeners`|Enable the attachment of ListenerSets to this Gateway. The example allows listeners from any namespace.|
   |`spec.listeners`|{{< reuse "docs/snippets/generic-listener.md" >}} In this example, the generic listener is configured on port 80, which differs from port 8000 in the ListenerSet that you create later.|

2. Create a ListenerSet that configures a TCP listener for the Gateway.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.x-k8s.io/v1alpha1
   kind: XListenerSet
   metadata:
     name: my-tcp-listenerset
     namespace: kgateway-system
     labels:
       app: tcp-echo
   spec:
     parentRef:
       name: tcp-gateway
       namespace: kgateway-system
       kind: Gateway
       group: gateway.networking.k8s.io
     listeners:
     - protocol: TCP
       port: 8000
       name: tcp-listener-set
       allowedRoutes:
         kinds:
         - kind: TCPRoute
   EOF
   ```

   {{< reuse "docs/snippets/review-table.md" >}}

   |Setting|Description|
   |--|--|
   |`spec.parentRef`|The name of the Gateway to attach the ListenerSet to. |
   |`spec.listeners`|Configure the listeners for this ListenerSet. In this example, you configure a TCP listener for port 8000. The gateway can serve TCPRoutes from any namespace. |

{{% /tab %}}
{{< /tabs >}}

2. Check the status of the gateway to make sure that your configuration is accepted. Note that in the output, a `NoConflicts` status of `False` indicates that the gateway is accepted and does not conflict with other gateway configuration. 
   ```sh
   kubectl get gateway tcp-gateway -n kgateway-system -o yaml
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

3. Create a ReferenceGrant to allow TCPRoutes to reference the tcp-echo service.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1beta1
   kind: ReferenceGrant
   metadata:
     name: allow-tcp-route-to-echo
     namespace: default
   spec:
     from:
       - group: gateway.networking.k8s.io
         kind: TCPRoute
         namespace: kgateway-system
     to:
       - group: ""
         kind: Service
   EOF
   ```

## Create a TCPRoute

{{< tabs items="Gateway listeners,ListenerSets (experimental)" >}}
{{% tab %}}
```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.networking.k8s.io/v1alpha2
kind: TCPRoute
metadata:
  name: tcp-route-echo
  namespace: kgateway-system
  labels:
    app: tcp-echo
spec:
  parentRefs:
    - name: tcp-gateway
      namespace: kgateway-system
      sectionName: tcp
  rules:
    - backendRefs:
        - name: tcp-echo
          namespace: default
          port: 1025
EOF
```
{{% /tab %}}
{{% tab %}}
```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.networking.k8s.io/v1alpha2
kind: TCPRoute
metadata:
  name: tcp-route-echo
  namespace: kgateway-system
  labels:
    app: tcp-echo
spec:
  parentRefs:
    - name: my-tcp-listenerset
      namespace: kgateway-system
      kind: XListenerSet
      group: gateway.networking.x-k8s.io
      sectionName: tcp-listener-set
  rules:
    - backendRefs:
        - name: tcp-echo
          namespace: default
          port: 1025
EOF
```
{{% /tab %}}
{{< /tabs >}}

5. Verify that the TCPRoute is applied successfully. 
   
   ```sh
   kubectl get tcproute/tcp-route-echo -n kgateway-system -o yaml
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
       controllerName: kgateway.dev/kgateway
       parentRef:
         group: gateway.networking.k8s.io
         kind: Gateway
         name: tcp-gateway
         namespace: kgateway-system
         sectionName: tcp
   ```

## Verify the TCP route {#verify-tcp-route}

Verify that the TCP route to the TCP echo app is working.

1. Get the external address of the gateway and save it in an environment variable.
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n kgateway-system tcp-gateway -o jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS   
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   kubectl port-forward deployment/tcp-gateway -n kgateway-system 8000:8000
   ```
   {{% /tab %}}
   {{< /tabs >}}

2. Send a TCP request to the external address of the TCP gateway on port 8000. You might use a tool such as telnet or netcat as in the following example.

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   nc $INGRESS_GW_ADDRESS 8000
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   nc localhost 8000
   ```
   {{% /tab %}}
   {{< /tabs >}} 

   The output is an open session for you to send more requests.

3. Enter any string to verify that the TCP echo service "echoes," returning the same string back.

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