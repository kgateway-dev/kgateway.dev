Customize your agentgateway proxy with {{< reuse "docs/snippets/gatewayparameters.md" >}}.

## About customizing your proxy {#upstream-configuration}

In upstream agentgateway, you can manage [configuration](https://agentgateway.dev/docs/configuration/overview/) via a YAML or JSON file. The configuration features of agentgateway are captured in the [schema of the agentgateway codebase](https://github.com/agentgateway/agentgateway/tree/main/schema). 

Unlike in the upstream agentgateway project, you do not configure these features in a raw configuration file in the agentgateway proxy. Instead, you configure them in a Kubernetes Gateway API-native way as explained in the guides throughout this doc set. 

However, you still might want to pass in custom configuration to your agentgateway proxy. This can be useful in the following use cases:

- Migrating from upstream to {{< reuse "/docs/snippets/agw-kgw.md" >}}. 
- Using a feature that is not yet exposed via the Kubernetes Gateway or {{< reuse "/docs/snippets/agw-kgw.md" >}} APIs.

{{< version exclude-if="2.1.x" >}}

You can choose between the following options to provide custom configuration to your agentgateway proxy. 

* **Embed in {{< reuse "docs/snippets/gatewayparameters.md" >}} CRD directly (recommended)**: You can add your custom configuration to the {{< reuse "docs/snippets/gatewayparameters.md" >}} custom resource directly. This way, your configuration is validated when you apply the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource in your cluster. Keep in mind that not all upstream configuration options, such as `binds` are currently supported in the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource. For supported options, see the [API reference]({{< link-hextra path="/reference/api/#agentgatewayparametersspec" >}}). 
* **`rawConfig`**: For configuration that cannot be embedded into the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource directly, or if you prefer to pass in raw upstream configuration, you can use the `rawConfig` option in the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource instead. Note that configuration is not automatically validated. If configuration is malformatted or includes unsupported fields, the agentgateway proxy does not start. You can run `kubectl logs deploy/agentgateway-proxy -n agentgateway-system` to view the logs of the proxy and find more information about why the configuration could not be applied. 

{{< /version >}}

## Before you begin

{{< reuse "docs/snippets/agentgateway-prereq.md" >}}

## Step 1: Create agentgateway configuration {#agentgateway-configuration}

{{< version include-if="2.1.x" >}}

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

3. Create a Gateway resource for your agentgateway proxy that uses the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource. Set the port to a dummy value like `3030` to avoid conflicts with the binds defined in your {{< reuse "docs/snippets/gatewayparameters.md" >}}

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: agentgateway-config
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "docs/snippets/gatewayclass.md" >}}
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
  
{{< /version >}} 
{{< version exclude-if="2.1.x" >}}

Choose between the following options to provide your agentgateway configuration: 

* [Embed in {{< reuse "docs/snippets/gatewayparameters.md" >}}](#embed)
* [`rawConfig`](#rawconfig)

### Embed in {{< reuse "docs/snippets/gatewayparameters.md" >}} {#embed}

You can add your custom configuration to the {{< reuse "docs/snippets/gatewayparameters.md" >}} custom resource directly. This way, your configuration is validated when you apply the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource in your cluster. 

1. Create an {{< reuse "docs/snippets/gatewayparameters.md" >}} resource with your custom configuration. The following example changes the logging format from `text` to `json`. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
   metadata:
     name: agentgateway-config
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     logging:
        format: json
   EOF
   ```

2. Create a Gateway resource that sets up an agentgateway proxy that uses your {{< reuse "docs/snippets/gatewayparameters.md" >}}. 

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: agentgateway-config
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "docs/snippets/gatewayclass.md" >}}
     infrastructure:
       parametersRef:
         name: agentgateway-config
         group: agentgateway.dev
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

3. Check the pod logs to verify that the agentgateway logs are displayed in JSON format. 
   ```sh
   kubectl logs -l app.kubernetes.io/name=agentgateway-config -n agentgateway-system
   ```

   Example output: 
   ```
   {"level":"info","time":"2025-12-16T15:58:18.245219Z","scope":"agent_core::readiness","message":"Task 'agentgateway' complete (2.378042ms), still awaiting 1 tasks"}
   {"level":"info","time":"2025-12-16T15:58:18.245221Z","scope":"agentgateway::management::hyper_helpers","message":"listener established","address":"127.0.0.1:15000","component":"admin"}
   {"level":"info","time":"2025-12-16T15:58:18.245231Z","scope":"agentgateway::management::hyper_helpers","message":"listener established","address":"[::]:15020","component":"stats"}
   {"level":"info","time":"2025-12-16T15:58:18.248025Z","scope":"agent_xds::client","message":"Stream established","xds":{"id":1}}
   {"level":"info","time":"2025-12-16T15:58:18.248081Z","scope":"agent_xds::client","message":"received response","type_url":"type.googleapis.com/agentgateway.dev.workload.Address","size":44,"removes":0,"xds":{"id":1}}
   ```

### `rawConfig`

Use the `rawConfig` option to pass in raw upstream configuration to your agentgateway proxy. Note that the configuration is not automatically validated. If configuration is malformatted or includes unsupported fields, the agentgateway proxy does not start. You can run `kubectl logs deploy/agentgateway-proxy -n agentgateway-system` to view the logs of the proxy and find more information about why the configuration could not be applied. 

1. Create an {{< reuse "docs/snippets/gatewayparameters.md" >}} resource with your custom configuration. The following example sets up a simple direct response listener on port 3000 that returns a `200 OK` response with the body `"hello!"` for requests to the `/direct` path.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
   metadata:
     name: agentgateway-config
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     rawConfig:
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

2. Create a Gateway resource that sets up an agentgateway proxy that uses your {{< reuse "docs/snippets/gatewayparameters.md" >}}. Set the port to a dummy value like `3030` to avoid conflicts with the binds defined in your {{< reuse "docs/snippets/gatewayparameters.md" >}} resource.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: agentgateway-config
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "docs/snippets/gatewayclass.md" >}}
     infrastructure:
       parametersRef:
         name: agentgateway-config
         group: agentgateway.dev
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

3. Check the pod logs to verify that agentgateway loaded the configuration from the ConfigMap, such as by searching for the port binding.

   ```bash
   kubectl logs -l app.kubernetes.io/name=agentgateway-config -n {{< reuse "docs/snippets/namespace.md" >}} | grep 3000
   ```
   
   Example output:

   ```
   2025-10-28T13:47:01.116095Z	info	proxy::gateway	started bind	bind="bind/3000"
   ```

4. Send a test request.

   * **Cloud Provider LoadBalancer**:
     1. Get the external address of the gateway proxy and save it in an environment variable.
   
     ```sh
     export INGRESS_GW_ADDRESS=$(kubectl get svc -n {{< reuse "docs/snippets/namespace.md" >}} agentgateway-config -o=jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
     echo $INGRESS_GW_ADDRESS
     ```

     2. Send a request along the `/direct` path to the agentgateway proxy through port 3000. 
        ```sh
        curl -i http://$INGRESS_GW_ADDRESS:3000/direct
        ```
   * **Port-forward for local testing**
     1. Port-forward the `agentgateway-config` pod on port 3000.
        ```sh
        kubectl port-forward deployment/agentgateway-config -n {{< reuse "docs/snippets/namespace.md" >}} 3000:3000
        ```

     2. Send a request to verify that you get back the expected response from your direct response configuration.
        ```sh
        curl -i localhost:3000/direct
        ```

   Example output:
   
   ```txt
   HTTP/1.1 200 OK
   content-length: 6
   date: Tue, 28 Oct 2025 14:13:48 GMT
   
   hello!
   ```

{{< /version>}}
{{< version include-if="2.1.x" >}}

## Step 2: Verify the configuration {#verify-configuration}

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

   * **Cloud Provider LoadBalancer**:
     1. Get the external address of the gateway proxy and save it in an environment variable. 
        ```sh
        export INGRESS_GW_ADDRESS=$(kubectl get svc -n {{< reuse "docs/snippets/namespace.md" >}} agentgateway-config -o=jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
        echo $INGRESS_GW_ADDRESS
        ```

     2. Send a request along the `/direct` path to the agentgateway proxy. Use port 3000 as defined in your ConfigMap.
        ```sh
        curl -i http://$INGRESS_GW_ADDRESS:3000/direct
        ```
   * **Port-forward for local testing**
     1. Port-forward the `agentgateway-config` pod on port 3000 as defined in your ConfigMap.
   
        ```sh
        kubectl port-forward deployment/agentgateway-config -n {{< reuse "docs/snippets/namespace.md" >}} 3000:3000
        ```

     2. Send a request to verify that you get back the expected response from your direct response configuration.
   
        ```sh
        curl -i localhost:3000/direct
        ```

   Example output:
   
   ```txt
   HTTP/1.1 200 OK
   content-length: 6
   date: Tue, 28 Oct 2025 14:13:48 GMT
   
   hello!
   ```

{{< /version >}}

## Clean up

{{< reuse "docs/snippets/cleanup.md" >}}

```bash
kubectl delete Gateway agentgateway-config -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete {{< reuse "docs/snippets/gatewayparameters.md" >}} agentgateway-config -n {{< reuse "docs/snippets/namespace.md" >}} {{< version exclude-if="2.2.x" >}}
kubectl delete ConfigMap agentgateway-config -n {{< reuse "docs/snippets/namespace.md" >}} {{< /version >}}
```
