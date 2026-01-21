Customize your agentgateway proxy with {{< reuse "docs/snippets/gatewayparameters.md" >}}.

## About customizing your proxy {#upstream-configuration}

In upstream agentgateway, you can manage [configuration](https://agentgateway.dev/docs/configuration/overview/) via a YAML or JSON file. The configuration features of agentgateway are captured in the [schema of the agentgateway codebase](https://github.com/agentgateway/agentgateway/tree/main/schema). 

Unlike in the upstream agentgateway project, you do not configure these features in a raw configuration file in the agentgateway proxy. Instead, you configure them in a Kubernetes Gateway API-native way as explained in the guides throughout this doc set. 

However, you still might want to pass in custom configuration to your agentgateway proxy. This can be useful in the following use cases:

- Migrating from upstream to {{< reuse "/docs/snippets/agw-kgw.md" >}}.
- Using a feature that is not yet exposed via the Kubernetes Gateway or {{< reuse "/docs/snippets/agw-kgw.md" >}} APIs.

{{< version include-if="2.2.x" >}}

You can choose between the following options to provide custom configuration to your agentgateway proxy.

* **Embed in {{< reuse "docs/snippets/gatewayparameters.md" >}} CRD directly (recommended)**: You can add your custom configuration to the {{< reuse "docs/snippets/gatewayparameters.md" >}} custom resource directly. This way, your configuration is validated when you apply the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource in your cluster. Keep in mind that not all upstream configuration options, such as `binds`, are currently supported in the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource. For supported options, see the [API reference]({{< link-hextra path="/reference/api/#agentgatewayparametersspec" >}}).
* **`rawConfig`**: For configuration that cannot be embedded into the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource directly, or if you prefer to pass in raw upstream configuration, you can use the `rawConfig` option in the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource instead. Note that configuration is not automatically validated. If configuration is malformatted or includes unsupported fields, the agentgateway proxy does not start. You can run `kubectl logs deploy/agentgateway-proxy -n agentgateway-system` to view the logs of the proxy and find more information about why the configuration could not be applied.
* **Overlays (strategic merge patch)**: For advanced customization of the Kubernetes resources that the control plane generates (such as Deployments, Services, ServiceAccounts), you can use overlays. Overlays use [Kubernetes strategic merge patch](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-api-machinery/strategic-merge-patch.md) semantics to modify the generated resources after they are rendered. See the [Overlays section](#overlays) for details and the [Overlays cookbook](#overlays-cookbook) for common recipes.

{{< /version >}}

## Before you begin

Set up an [agentgateway proxy]({{< link-hextra path="/agentgateway/setup/" >}}).

## Step 1: Create agentgateway configuration {#agentgateway-configuration}

{{< version include-if="2.1.x" >}}

Use a ConfigMap to pass upstream configuration settings directly to the agentgateway proxy.

1. Create a ConfigMap with your agentgateway configuration. This configuration defines the binds, listeners, routes, backends, and policies that you want agentgateway to use. The key must be named `config.yaml`. The following example sets up a simple direct response listener on port 3000 that returns a `200 OK` response with the body `"hello!"` for requests to the `/direct` path.

   ```yaml
   kubectl apply -f- <<'EOF'
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
   kubectl apply -f- <<'EOF'
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
   kubectl apply -f- <<'EOF'
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
{{< version include-if="2.2.x" >}}

Choose between the following options to provide your agentgateway configuration: 

* [Embed in {{< reuse "docs/snippets/gatewayparameters.md" >}}](#embed)
* [`rawConfig`](#rawconfig)

### Embed in {{< reuse "docs/snippets/gatewayparameters.md" >}} {#embed}

You can add your custom configuration to the {{< reuse "docs/snippets/gatewayparameters.md" >}} custom resource directly. This way, your configuration is validated when you apply the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource in your cluster. 

1. Create an {{< reuse "docs/snippets/gatewayparameters.md" >}} resource with your custom configuration. The following example changes the logging format from `text` to `json`. 
   ```yaml
   kubectl apply --server-side -f- <<'EOF'
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
   kubectl apply --server-side -f- <<'EOF'
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
         group: {{< reuse "docs/snippets/gatewayparam-group.md" >}}
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
   kubectl logs deployment/agentgateway-config -n {{< reuse "docs/snippets/namespace.md" >}}
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
   kubectl apply --server-side -f- <<'EOF'
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
   kubectl apply --server-side -f- <<'EOF'
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
         group: {{< reuse "docs/snippets/gatewayparam-group.md" >}}  
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
   kubectl logs deployment/agentgateway-config -n {{< reuse "docs/snippets/namespace.md" >}} | grep 3000
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


## Overlays (strategic merge patch) {#overlays}

Overlays let you customize the Kubernetes resources that the control plane generates for your agentgateway proxy. When you create a Gateway, the control plane generates resources like Deployments, Services, and ServiceAccounts. Overlays use [Kubernetes strategic merge patch (SMP)](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-api-machinery/strategic-merge-patch.md) semantics to modify these resources after they are rendered. For additional examples, see the [kubectl patch documentation](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/update-api-object-kubectl-patch/#use-a-strategic-merge-patch-to-update-a-deployment).

### Configs vs overlays {#configs-vs-overlays}

The {{< reuse "docs/snippets/gatewayparameters.md" >}} API provides two ways to customize your proxy:

| Approach | Validation | Stability | Use case |
|----------|------------|-----------|----------|
| **Configs** (e.g., `image`, `logging`, `resources`, `env`) | Validated by control plane when data plane is created or updated | Stable API contract | Common settings like image names, logging format, resource limits |
| **Overlays** (e.g., `deployment`, `service`) | Validated by Kubernetes when resources are created, not by the control plane | No stability guarantee | All Kubernetes customization not exposed through configs |

**Use configs when possible.** Configs are validated by the control plane when the data plane is created or updated, catching errors early. They also provide a stable API that won't break across upgrades.

**Use overlays for everything else.** Overlays give you full control over the generated Kubernetes resources, but they operate on internal implementation details that may change between versions.

### When to use overlays

Overlays are useful when you need to customize resources in ways that are not directly exposed through the {{< reuse "docs/snippets/gatewayparameters.md" >}} configs. Common use cases include:

- Adding image pull secrets to pull from private registries
- Removing default security contexts for platforms like OpenShift
- Adding custom labels, annotations, or environment variables
- Configuring pod scheduling (node selectors, affinities, tolerations)
- Setting up Horizontal Pod Autoscalers (HPA) or Pod Disruption Budgets (PDB)
- Mounting custom ConfigMaps or Secrets as volumes
- Configuring cloud provider-specific service annotations

{{< callout type="warning" >}}
**Upgrade risk:** Overlays modify the internal Kubernetes resources that the control plane generates. These resources are implementation details, not a stable API. Future upgrades may change the structure of these resources, which could cause your overlays to fail or behave unexpectedly. Test your overlays thoroughly after each upgrade.
{{< /callout >}}

### How overlays work

Overlays are applied **after** the control plane renders the base Kubernetes resources. The control plane:

1. Reads configs from your {{< reuse "docs/snippets/gatewayparameters.md" >}} (like `image`, `logging`, `resources`)
2. Generates the base resources (Deployment, Service, etc.)
3. Applies any overlays you specify using strategic merge patch semantics
4. Creates or updates the resources in the cluster

### Removing fields: null vs $patch: delete {#removing-fields}

Strategic merge patch provides two ways to remove fields:

| Method | Syntax | Apply mode required | Best for |
|--------|--------|---------------------|----------|
| `null` | `fieldName: null` | `kubectl apply --server-side` | Removing scalar values and simple objects |
| `$patch: delete` | `fieldName: { $patch: delete }` | Any apply mode | Removing objects when you can't use server-side apply |

**Using null (requires server-side apply):**

```yaml
spec:
  deployment:
    spec:
      template:
        spec:
          containers:
            - name: agentgateway
              # Removes the securityContext entirely
              securityContext: null
```

**Using $patch: delete (works with any apply mode):**

```yaml
spec:
  deployment:
    spec:
      template:
        spec:
          # Removes the pod-level securityContext
          securityContext:
            $patch: delete
```

{{< callout type="info" >}}
**Why null requires server-side apply:** Without server-side apply, Kubernetes strips null values from the CRD before storing it. Your {{< reuse "docs/snippets/gatewayparameters.md" >}} resource appears to save successfully, but the null values are silently dropped. Always use `kubectl apply --server-side` when your overlays contain null values.
{{< /callout >}}

### Overlay fields

You can overlay the following resource types in the {{< reuse "docs/snippets/gatewayparameters.md" >}} spec:

| Field | Resource Type | Description |
|-------|--------------|-------------|
| `deployment` | Deployment | The agentgateway proxy deployment |
| `service` | Service | The service exposing the proxy |
| `serviceAccount` | ServiceAccount | The service account for the proxy pods |
| `horizontalPodAutoscaler` | HorizontalPodAutoscaler | Created **only** when this overlay is specified |
| `podDisruptionBudget` | PodDisruptionBudget | Created **only** when this overlay is specified |

{{< callout type="info" >}}
**HPA and PDB are opt-in.** Unlike Deployment, Service, and ServiceAccount, the control plane does not create HPA or PDB resources by default. These resources are created only when you provide an overlay for them. This gives you full control over autoscaling and disruption policies.
{{< /callout >}}

## Overlays cookbook {#overlays-cookbook}

The following recipes demonstrate common overlay patterns. Each recipe shows a complete {{< reuse "docs/snippets/gatewayparameters.md" >}} resource that you can adapt to your needs.

### Change deployment replicas {#recipe-replicas}

Set a specific number of replicas for the agentgateway deployment.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: agentgateway-replicas
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  deployment:
    spec:
      replicas: 3
EOF
```

### Add image pull secrets {#recipe-image-pull-secrets}

Add image pull secrets to pull container images from private registries.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: agentgateway-pull-secrets
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  deployment:
    spec:
      template:
        spec:
          imagePullSecrets:
            - name: my-registry-secret
EOF
```

### Remove security context for OpenShift {#recipe-openshift}

OpenShift manages security contexts through Security Context Constraints (SCCs). Remove the default security context to allow OpenShift to assign appropriate values.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: agentgateway-openshift
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  deployment:
    spec:
      template:
        spec:
          # Delete pod-level securityContext using $patch: delete (works with any apply mode)
          securityContext:
            $patch: delete
          containers:
            - name: agentgateway
              # Delete container-level securityContext using null (requires server-side apply)
              securityContext: null
EOF
```

### Add environment variables {#recipe-env-vars}

Add custom environment variables to the agentgateway container. Use `null` to remove default environment variables.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: agentgateway-env
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  env:
    - name: MY_CUSTOM_VAR
      value: "my-value"
    - name: CONNECTION_MIN_TERMINATION_DEADLINE
      value: "500s"
    # Remove a default env var by setting value to null
    - name: RUST_BACKTRACE
      value: null
EOF
```

### Configure pod scheduling {#recipe-pod-scheduling}

Configure node selectors, affinities, tolerations, and topology spread constraints to control where agentgateway pods are scheduled.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: agentgateway-scheduling
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  deployment:
    spec:
      template:
        spec:
          nodeSelector:
            node-type: agent
            zone: us-west-1a
          affinity:
            nodeAffinity:
              requiredDuringSchedulingIgnoredDuringExecution:
                nodeSelectorTerms:
                  - matchExpressions:
                      - key: kubernetes.io/arch
                        operator: In
                        values:
                          - amd64
                          - arm64
          tolerations:
            - key: dedicated
              operator: Equal
              value: agent-gateway
              effect: NoSchedule
          topologySpreadConstraints:
            - maxSkew: 1
              topologyKey: kubernetes.io/hostname
              whenUnsatisfiable: DoNotSchedule
              labelSelector:
                matchLabels:
                  app: agentgateway
EOF
```

### Set up Horizontal Pod Autoscaler (HPA) {#recipe-hpa}

Configure automatic scaling based on CPU utilization. The HPA resource is only created when you specify this overlay.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: agentgateway-hpa
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  horizontalPodAutoscaler:
    metadata:
      labels:
        app: agentgateway
    spec:
      minReplicas: 2
      maxReplicas: 10
      metrics:
        - type: Resource
          resource:
            name: cpu
            target:
              type: Utilization
              averageUtilization: 80
EOF
```

### Set up Pod Disruption Budget (PDB) {#recipe-pdb}

Configure a Pod Disruption Budget to ensure availability during voluntary disruptions. The PDB resource is only created when you specify this overlay.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: agentgateway-pdb
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  podDisruptionBudget:
    metadata:
      labels:
        app: agentgateway
    spec:
      minAvailable: 1
EOF
```

### Mount custom ConfigMap as volume {#recipe-configmap-volume}

Mount a custom ConfigMap into the agentgateway container. This example replaces the default volumes and adds a custom config.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: agentgateway-custom-volume
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  deployment:
    spec:
      template:
        spec:
          volumes:
            - name: custom-config
              configMap:
                name: my-custom-config
          containers:
            - name: agentgateway
              volumeMounts:
                - name: custom-config
                  mountPath: /etc/custom-config
                  readOnly: true
EOF
```

### Add labels and annotations {#recipe-labels-annotations}

Add custom labels and annotations to deployments, pods, and services.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: agentgateway-labels
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  deployment:
    metadata:
      labels:
        environment: production
        team: platform
      annotations:
        description: "Production agentgateway proxy"
    spec:
      template:
        metadata:
          labels:
            environment: production
          annotations:
            prometheus.io/scrape: "true"
            prometheus.io/port: "15020"
  service:
    metadata:
      annotations:
        service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
EOF
```

### Customize service ports {#recipe-service-ports}

Replace the default service ports with custom port configurations.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: agentgateway-service-ports
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  service:
    spec:
      ports:
        - $patch: replace
        - name: http
          port: 80
          targetPort: 8080
          protocol: TCP
        - name: https
          port: 443
          targetPort: 8443
          protocol: TCP
EOF
```

### Set resource requests and limits {#recipe-resources}

Configure CPU and memory requests and limits for the agentgateway container.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: agentgateway-resources
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi
EOF
```

### Custom pod security context {#recipe-security-context}

Configure custom security settings for the pod and containers.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: agentgateway-security
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  deployment:
    spec:
      template:
        spec:
          securityContext:
            runAsUser: 1000
            runAsGroup: 2000
            fsGroup: 3000
EOF
```

### Remove a label with null {#recipe-remove-label}

Remove a default label by setting it to `null`. Remember to use server-side apply.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: agentgateway-remove-label
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  deployment:
    metadata:
      labels:
        # Remove the managed-by label
        app.kubernetes.io/managed-by: null
EOF
```

### Replace all volumes {#recipe-replace-volumes}

Use `$patch: replace` to completely replace a list instead of merging. Note that the `$patch` directive must be on its own list item.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: agentgateway-replace-volumes
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  deployment:
    spec:
      template:
        spec:
          volumes:
            - $patch: replace
            - name: custom-config
              configMap:
                name: my-custom-config
EOF
```

{{< callout type="warning" >}}
**Important:** Place `$patch: replace` as a separate list item before your actual items. If you include it in the same item as your config, you may end up with an empty list.
{{< /callout >}}

### Custom image (config) {#recipe-image}

Use the `image` config to specify a custom container image. This is a config, not an overlay, so it is validated at apply time.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: agentgateway-image
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  image:
    registry: my-registry.io
    repository: my-org/agentgateway
    tag: v2.0.0
    pullPolicy: Always
EOF
```

You can also pin to a specific digest for immutable deployments:

```yaml
spec:
  image:
    registry: my-registry.io
    repository: my-org/agentgateway
    digest: sha256:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890
```

### Shutdown configuration (config) {#recipe-shutdown}

Configure graceful shutdown timeouts using the `shutdown` config.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: agentgateway-shutdown
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  shutdown:
    min: 15
    max: 120
EOF
```

### Static IP for LoadBalancer {#recipe-static-ip}

Assign a static IP address to the LoadBalancer service.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: agentgateway-static-ip
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  service:
    spec:
      loadBalancerIP: 203.0.113.10
EOF
```

### GKE-specific service annotations {#recipe-gke}

Configure GKE-specific features like Regional Backend Services (RBS) and static IPs using service annotations.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: agentgateway-gke
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  service:
    metadata:
      annotations:
        # Enable Regional Backend Services for better load balancing
        cloud.google.com/l4-rbs: "enabled"
        # Use pre-reserved static IPs
        networking.gke.io/load-balancer-ip-addresses: "my-v4-ip,my-v6-ip"
        # Specify the subnet for internal load balancers
        networking.gke.io/load-balancer-subnet: "my-subnet"
EOF
```

### AWS EKS load balancer annotations {#recipe-aws-eks}

Configure AWS-specific load balancer features using service annotations.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: agentgateway-aws
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  service:
    metadata:
      annotations:
        # Use Network Load Balancer instead of Classic
        service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
        # Make it internal (no public IP)
        service.beta.kubernetes.io/aws-load-balancer-internal: "true"
        # Enable cross-zone load balancing
        service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled: "true"
        # Specify subnets
        service.beta.kubernetes.io/aws-load-balancer-subnets: "subnet-abc123,subnet-def456"
EOF
```

### Azure AKS load balancer annotations {#recipe-azure-aks}

Configure Azure-specific load balancer features using service annotations.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: agentgateway-azure
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  service:
    metadata:
      annotations:
        # Make it internal
        service.beta.kubernetes.io/azure-load-balancer-internal: "true"
        # Specify resource group for the load balancer
        service.beta.kubernetes.io/azure-load-balancer-resource-group: "my-resource-group"
EOF
```

### Delete security context with $patch: delete {#recipe-delete-security-context}

Use `$patch: delete` to remove security contexts without requiring server-side apply. This is useful when you cannot use server-side apply in your deployment pipeline.

```yaml
kubectl apply -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: agentgateway-delete-security
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  deployment:
    spec:
      template:
        spec:
          # Delete pod-level securityContext using $patch: delete
          securityContext:
            $patch: delete
          containers:
            - name: agentgateway
              # Delete container-level securityContext:
              securityContext:
                $patch: delete
EOF
```

### Add init containers {#recipe-init-containers}

Add init containers that run before the main agentgateway container starts.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: agentgateway-init
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  deployment:
    spec:
      template:
        spec:
          initContainers:
            - name: wait-for-config
              image: busybox:1.36
              command: ['sh', '-c', 'until [ -f /config/ready ]; do sleep 1; done']
              volumeMounts:
                - name: config-volume
                  mountPath: /config
EOF
```

### Add sidecar containers {#recipe-sidecar}

Add sidecar containers alongside the main agentgateway container.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: agentgateway-sidecar
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  deployment:
    spec:
      template:
        spec:
          containers:
            - name: agentgateway
              # This merges with the existing agentgateway container
            - name: log-shipper
              image: fluent/fluent-bit:latest
              volumeMounts:
                - name: logs
                  mountPath: /var/log/agentgateway
EOF
```

### ServiceAccount annotations for IAM {#recipe-sa-iam}

Add annotations to the ServiceAccount for cloud provider IAM integration (e.g., AWS IRSA, GKE Workload Identity).

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: agentgateway-iam
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  serviceAccount:
    metadata:
      annotations:
        # AWS IRSA
        eks.amazonaws.com/role-arn: "arn:aws:iam::123456789012:role/agentgateway-role"
        # Or GKE Workload Identity
        # iam.gke.io/gcp-service-account: "agentgateway@my-project.iam.gserviceaccount.com"
EOF
```

## Beyond the cookbook: discover-then-customize {#discover-workflow}

If the cookbook doesn't cover your use case, you can write custom overlays by inspecting the resources that the control plane generates. This workflow involves deploying a Gateway first, examining the generated resources, and then writing overlays to modify them.

**Step 1: Deploy a basic Gateway**

Create a Gateway without any overlays to see what resources the control plane generates:

```bash
kubectl apply -f- <<'EOF'
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: my-gateway
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  gatewayClassName: {{< reuse "docs/snippets/gatewayclass.md" >}}
  listeners:
    - name: http
      port: 8080
      protocol: HTTP
EOF
```

**Step 2: Inspect the generated resources**

Examine the Deployment, Service, and ServiceAccount that the control plane created:

```bash
# View the generated Deployment
kubectl get deployment my-gateway -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml

# View the generated Service
kubectl get service my-gateway -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml

# View the generated ServiceAccount
kubectl get serviceaccount my-gateway -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml
```

**Step 3: Write overlays to customize**

Now that you can see the actual resource structure, write overlays to modify the specific fields you need to change. Use the [cookbook recipes](#overlays-cookbook) as templates for your custom overlays.

## Troubleshooting overlays {#troubleshooting}

### Overlay not taking effect

**Symptoms:** You applied an overlay, but the generated resource doesn't reflect your changes.

**Possible causes:**

1. **Null values without server-side apply:** If your overlay uses `null` to remove a field, you must use `kubectl apply --server-side`. Without it, null values are silently stripped.

   ```bash
   # Wrong - null values are dropped
   kubectl apply -f my-params.yaml

   # Correct - null values are preserved
   kubectl apply --server-side -f my-params.yaml
   ```

2. **Wrong container name:** When modifying container settings, you must specify the correct container name (`agentgateway`) as the merge key.

   ```yaml
   # Wrong - missing container name, won't merge with existing container
   containers:
     - resources:
         limits:
           memory: 512Mi

   # Correct - includes container name as merge key
   containers:
     - name: agentgateway
       resources:
         limits:
           memory: 512Mi
   ```

3. **$patch: replace in wrong position:** When replacing a list, place `$patch: replace` as a separate list item.

   ```yaml
   # Wrong - will result in empty list
   volumes:
     - $patch: replace
       name: my-volume
       configMap:
         name: my-config

   # Correct - replace is separate item
   volumes:
     - $patch: replace
     - name: my-volume
       configMap:
         name: my-config
   ```

### Pod fails to start after overlay

**Symptoms:** The agentgateway pod enters CrashLoopBackOff or fails to schedule.

**Debugging steps:**

1. Check pod events:
   ```bash
   kubectl describe pod -l app.kubernetes.io/name=my-gateway -n {{< reuse "docs/snippets/namespace.md" >}}
   ```

2. Check container logs:
   ```bash
   kubectl logs deployment/my-gateway -n {{< reuse "docs/snippets/namespace.md" >}}
   ```

3. Verify the rendered Deployment:
   ```bash
   kubectl get deployment my-gateway -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml
   ```

### Verifying your overlay was stored correctly

Check that your {{< reuse "docs/snippets/gatewayparameters.md" >}} resource contains your overlay as expected:

```bash
kubectl get {{< reuse "docs/snippets/gatewayparameters.md" >}} my-params -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml
```

If you used null values without server-side apply, they will be missing from the stored resource.

{{< /version >}}
{{< version include-if="2.1.x" >}}

## Step 2: Verify the configuration {#verify-configuration}

1. Describe the agentgateway pod. Verify that the pod is `Running` and that the `Mounts` section mounts the `/config` from the ConfigMap.

   ```bash
   kubectl describe pod -l app.kubernetes.io/name=agentgateway-config -n {{< reuse "docs/snippets/namespace.md" >}}
   ```

2. Check the pod logs to verify that agentgateway loaded the configuration from the ConfigMap, such as by searching for the port binding.

   ```bash
   kubectl logs deployment/agentgateway-config -n {{< reuse "docs/snippets/namespace.md" >}} | grep 3000
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
kubectl delete {{< reuse "docs/snippets/gatewayparameters.md" >}} agentgateway-config -n {{< reuse "docs/snippets/namespace.md" >}}
{{< version include-if="2.1.x" >}}kubectl delete ConfigMap agentgateway-config -n {{< reuse "docs/snippets/namespace.md" >}}{{< /version >}}
```
