Configure agentgateway with {{< reuse "docs/snippets/gatewayparameters.md" >}}.

{{< reuse "docs/snippets/gatewayparameters.md" >}} provide a way for you to pass configuration for special use cases, such as passing in raw upstream configuration from a YAML file.

## Before you begin

{{< reuse "docs/snippets/agentgateway-prereq.md" >}}

## Upstream configuration {#upstream-configuration}

In upstream agentgateway, you can manage [configuration](https://agentgateway.dev/docs/configuration/overview/) via a YAML or JSON file. The configuration features of agentgateway are captured in the [schema of the agentgateway codebase](https://github.com/agentgateway/agentgateway/tree/main/schema). 

Unlike in the upstream agentgateway project, you do not configure these features in a raw configuration file in {{< reuse "/docs/snippets/agw-kgw.md" >}}. Instead, you configure them in a Kubernetes Gateway API-native way as explained in the guides throughout this doc set. 

However, you still might want to pass in your upstream configuration file in {{< reuse "/docs/snippets/agw-kgw.md" >}}. This can be useful in the following use cases:

- Migrating from upstream to {{< reuse "/docs/snippets/agw-kgw.md" >}}. 
- Using a feature that is not yet exposed via the Kubernetes Gateway or {{< reuse "/docs/snippets/agw-kgw.md" >}} APIs.

### Step 1: Create agentgateway configuration {#agentgateway-configuration}

Use a ConfigMap to pass upstream configuration settings directly to the agentgateway proxy. 

1. Create a ConfigMap with your agentgateway configuration. This configuration defines the binds, listeners, routes, backends, and policies that you want agentgateway to use. The key must be named `config.yaml`. The following example sets up a simple direct response listener on port 3000 that returns a `200 OK` response with the body `"hello!"` for requests to the `/direct` path.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: agentgateway-config
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   data:
     config.yaml: |-
       binds:
       - port: 3000
         listeners:
         - protocol: HTTP
           routes:
           - name: direct-response
             matches:
             - path:
                 pathPrefix: /direct
             policies:
               directResponse:
                 body: "hello!"
                 status: 200
   EOF
   ```

2. Create a {{< reuse "docs/snippets/gatewayparameters.md" >}} resource that refers to your ConfigMap.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
   metadata:
     name: agentgateway-config
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     kube:
       agentgateway:
         enabled: true
         customConfigMapName: agentgateway-config
   EOF
   ```

3. Create a Gateway resource that sets up an agentgateway proxy that uses your {{< reuse "docs/snippets/gatewayparameters.md" >}}. Set the port to a dummy value like `3030` to avoid conflicts with the binds defined in your ConfigMap.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: agentgateway-config
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "docs/snippets/agw-gatewayclass.md" >}}
     infrastructure:
       parametersRef:
         name: agentgateway-config
         group: {{< reuse "docs/snippets/trafficpolicy-group.md" >}} 
         kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}       
     listeners:
       - name: http
         port: 3030
         protocol: HTTP
         allowedRoutes:
           namespaces:
             from: All
   EOF
   ```

### Step 2: Verify the configuration {#verify-configuration}

1. Describe the agentgateway pod. Verify that the pod is `Running` and that the `Mounts` section mounts the `/config` from the ConfigMap.

   ```bash
   kubectl describe pod -l app.kubernetes.io/name=agentgateway-config -n {{< reuse "docs/snippets/namespace.md" >}}
   ```

2. Check the pod logs to verify that agentgateway loaded the configuration from the ConfigMap, such as by searching for the port binding.

   ```bash
   kubectl logs -l app.kubernetes.io/name=agentgateway-config -n {{< reuse "docs/snippets/namespace.md" >}} | grep 3000
   ```
   
   Example output:

   ```
   2025-10-28T13:47:01.116095Z	info	proxy::gateway	started bind	bind="bind/3000"
   ```

3. Send a test request.

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
{{% tab tabName="Cloud Provider LoadBalancer" %}}
1. Get the external address of the gateway proxy and save it in an environment variable.
   
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n {{< reuse "docs/snippets/namespace.md" >}} agentgateway-config -o=jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS
   ```

2. Send a request along the `/direct` path to the agentgateway proxy. Use port 3000 as defined in your ConfigMap.
   
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:3000/direct
   ```
{{% /tab %}}
{{% tab tabName="Port-forward for local testing"%}}
1. Port-forward the `agentgateway-config` pod on port 3000 as defined in your ConfigMap.
   
   ```sh
   kubectl port-forward deployment/agentgateway-config -n {{< reuse "docs/snippets/namespace.md" >}} 3000:3000
   ```

2. Send a request to verify that you get back the expected response from your direct response configuration.
   
   ```sh
   curl -i localhost:3000/direct
   ```
{{% /tab %}}
   {{< /tabs >}}

   Example output:
   
   ```txt
   HTTP/1.1 200 OK
   content-length: 6
   date: Tue, 28 Oct 2025 14:13:48 GMT
   
   hello!
   ```

### Clean up

{{< reuse "docs/snippets/cleanup.md" >}}

```bash
kubectl delete Gateway agentgateway-config -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete {{< reuse "docs/snippets/gatewayparameters.md" >}} agentgateway-config -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete ConfigMap agentgateway-config -n {{< reuse "docs/snippets/namespace.md" >}}
```
