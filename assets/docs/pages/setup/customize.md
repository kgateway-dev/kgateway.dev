The configuration that is used to spin up a gateway proxy is stored in several custom resources, including {{< reuse "docs/snippets/gatewayparameters.md" >}}, and a gateway proxy template. By default, {{< reuse "docs/snippets/kgateway.md" >}} creates these resources for you during the installation so that you can spin up gateway proxies with the [default proxy configuration]({{< link-hextra path="/setup/default/" >}}). You have the following options to change the default configuration for your gateway proxies: 

| Option | Description | 
| -- | -- | 
| Create your own {{< reuse "docs/snippets/gatewayparameters.md" >}} resource (recommended) | To adjust the settings on the gateway proxy, you can create your own {{< reuse "docs/snippets/gatewayparameters.md" >}} resource. This approach allows you to spin up gateway proxies with different configurations. Keep in mind that you must maintain the {{< reuse "docs/snippets/gatewayparameters.md" >}} resources that you created manually. The values in these resources are not automatically updated during upgrades.  | 
| Change default proxy settings | You can change some of the values for the default gateway proxy updating the values in the {{< reuse "docs/snippets/kgateway.md" >}} Helm chart. The values that you set in your Helm chart are automatically rolled out to the gateway proxies.  |
| Create self-managed gateways with custom proxy templates | {{< reuse "docs/snippets/byo-gateway.md" >}} | 

## Customize the gateway proxy 

The example in this guide uses the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource to change settings on the gateway proxy. To find other customization examples, see the [Gateway customization guides]({{< link-hextra path="/setup/customize/" >}}).

1. Create a {{< reuse "docs/snippets/gatewayparameters.md" >}} resource to add any custom settings to the gateway. The following example makes the following changes: 
   
   * The Envoy log level is set to `debug` (default value: `info`).
   * The Kubernetes service type is changed to NodePort (default value: `LoadBalancer`). 
   * The `gateway: custom` label is added to the gateway proxy service that exposes the proxy (default value: `gloo=kube-gateway`).
   * The `externalTrafficPolicy` is set to `Local` to preserve the original client IP address.
   * The `gateway: custom` label is added to the gateway proxy pod (default value: `gloo=kube-gateway` ). 
   * The security context of the gateway proxy is changed to use the 50000 as the supplemental group ID and user ID (default values: `10101` ). 

   For other settings, see the [API docs]({{< link-hextra path="/reference/api/#gatewayparametersspec" >}}) or check out the [Gateway customization guides]({{< link-hextra path="/setup/customize/" >}}).
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
   metadata:
     name: custom-gw-params
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     kube: 
       envoyContainer:
         bootstrap:
           logLevel: debug       
       service:
         type: NodePort
         extraLabels: 
           gateway: custom
         externalTrafficPolicy: Local
       podTemplate: 
         extraLabels:
           gateway: custom
         securityContext: 
           fsGroup: 50000
           runAsUser: 50000
   EOF
   ```

2. Create a Gateway resource that references your custom {{< reuse "docs/snippets/gatewayparameters.md" >}}. 
   ```yaml
   kubectl apply -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: custom
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "docs/snippets/gatewayclass.md" >}}
     infrastructure:
       parametersRef:
         name: custom-gw-params
         group: {{< reuse "docs/snippets/trafficpolicy-group.md" >}}
         kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}       
     listeners:
     - protocol: HTTP
       port: 80
       name: http
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

3. Verify that a pod is created for your gateway proxy and that it has the pod settings that you defined in the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource. 

   ```sh
   kubectl get pods -l app.kubernetes.io/name=custom -n {{< reuse "docs/snippets/namespace.md" >}}   -o yaml
   ```

   If the pod does not come up, try running `kubectl get events -n kgateway-system` to see if the Kubernetes API server logged any failures. If no events are logged, ensure that the `kgateway` GatewayClass is present in your cluster and that the Gateway resource shows an `Accepted` status. 

   Example output:

   ```yaml {linenos=table,hl_lines=[13,20,21,22],linenostart=1,filename="gateway-pod.yaml"}
   apiVersion: v1
   kind: Pod
   metadata:
     annotations:
       prometheus.io/path: /metrics
       prometheus.io/port: "9091"
       prometheus.io/scrape: "true"
     creationTimestamp: "2024-08-07T19:47:27Z"
     generateName: custom-7d9bf46f96-
     labels:
       app.kubernetes.io/instance: custom
       app.kubernetes.io/name: custom
       gateway: custom
       gateway.networking.k8s.io/gateway-name: custom
       kgateway: kube-gateway
   ...
     priority: 0
     restartPolicy: Always
     schedulerName: default-scheduler
     securityContext:
       fsGroup: 50000
       runAsUser: 50000
   ...
   ```

4. Get the details of the service that exposes the gateway proxy. Verify that the service is of type NodePort and that the extra label was added to the service. 

   ```sh
   kubectl get service custom -n kgateway-system -o yaml
   ```

   Example output: 

   ```yaml {linenos=table,hl_lines=[10,36],linenostart=1,filename="gateway-service.yaml"}
   apiVersion: v1
   kind: Service
   metadata:
     creationTimestamp: "2024-08-07T19:47:27Z"
     labels:
       app.kubernetes.io/instance: custom
       app.kubernetes.io/managed-by: Helm
       app.kubernetes.io/name: custom
       app.kubernetes.io/version: kgateway-proxy-v{{< reuse "docs/versions/n-patch.md" >}}
       gateway: custom
       gateway.networking.k8s.io/gateway-name: custom
       kgateway: kube-gateway
       helm.sh/chart: kgateway-proxy-v{{< reuse "docs/versions/n-patch.md" >}}
     name: custom
     namespace: kgateway-system
     ownerReferences:
     - apiVersion: gateway.networking.k8s.io/v1
       controller: true
       kind: Gateway
       name: custom
       uid: d29417ba-60f9-410c-a023-283b250f3d57
     resourceVersion: "7371789"
     uid: 67945b5f-e55f-42bb-b5f2-c35932659831
   spec:
     ports:
     - name: http
       nodePort: 30579
       port: 80
       protocol: TCP
       targetPort: 8080
     selector:
       app.kubernetes.io/instance: custom
       app.kubernetes.io/name: custom
       gateway.networking.k8s.io/gateway-name: custom
     sessionAffinity: None
     type: NodePort
   ```

## Configs vs overlays {#configs-vs-overlays}

The {{< reuse "docs/snippets/gatewayparameters.md" >}} API provides two ways to customize your proxy:

| Approach | Validation | Stability | Use case |
|----------|------------|-----------|----------|
| **Configs** (e.g., `envoyContainer`, `service`, `podTemplate`) | Validated by control plane when data plane is created or updated | Stable API contract | Common settings like image names, logging levels, resource limits |
| **Overlays** (e.g., `deploymentOverlay`, `serviceOverlay`) | Validated by Kubernetes when resources are created, not by the control plane | No stability guarantee | All Kubernetes customization not exposed through configs |

**Use configs when possible.** Configs are validated by the control plane when the data plane is created or updated, catching errors early. They also provide a stable API that won't break across upgrades.

**Use overlays for everything else.** Overlays give you full control over the generated Kubernetes resources, but they operate on internal implementation details that may change between versions.

## Overlays (strategic merge patch) {#overlays}

Overlays let you customize the Kubernetes resources that the control plane generates for your Envoy proxy. When you create a Gateway, the control plane generates resources like Deployments, Services, and ServiceAccounts. Overlays use [Kubernetes strategic merge patch (SMP)](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-api-machinery/strategic-merge-patch.md) semantics to modify these resources after they are rendered. For additional examples, see the [kubectl patch documentation](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/update-api-object-kubectl-patch/#use-a-strategic-merge-patch-to-update-a-deployment).

### When to use overlays

Overlays are useful when you need to customize resources in ways that are not directly exposed through the {{< reuse "docs/snippets/gatewayparameters.md" >}} configs. Common use cases include:

- Removing default security contexts for platforms like OpenShift (when `omitDefaultSecurityContext` is not sufficient)
- Setting up Horizontal Pod Autoscalers (HPA), Vertical Pod Autoscalers (VPA), or Pod Disruption Budgets (PDB)
- Adding init containers or sidecar containers
- Customizing deployment strategy beyond what configs expose
- Replacing default service ports entirely (configs can only add NodePorts)

{{< callout type="warning" >}}
**Upgrade risk:** Overlays modify the internal Kubernetes resources that the control plane generates. These resources are implementation details, not a stable API. Future upgrades may change the structure of these resources, which could cause your overlays to fail or behave unexpectedly. Test your overlays thoroughly after each upgrade.
{{< /callout >}}

### How overlays work

Overlays are applied **after** the control plane renders the base Kubernetes resources. The control plane:

1. Reads configs from your {{< reuse "docs/snippets/gatewayparameters.md" >}} (like `envoyContainer`, `service`, `podTemplate`)
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
  kube:
    deploymentOverlay:
      spec:
        template:
          spec:
            containers:
              - name: envoy
                # Removes the securityContext entirely
                securityContext: null
```

**Using $patch: delete (works with any apply mode):**

```yaml
spec:
  kube:
    deploymentOverlay:
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

You can overlay the following resource types in the {{< reuse "docs/snippets/gatewayparameters.md" >}} `spec.kube`:

| Field | Resource Type | Description |
|-------|--------------|-------------|
| `deploymentOverlay` | Deployment | The Envoy proxy deployment |
| `serviceOverlay` | Service | The service exposing the proxy |
| `serviceAccountOverlay` | ServiceAccount | The service account for the proxy pods |
| `horizontalPodAutoscaler` | HorizontalPodAutoscaler | Created **only** when this overlay is specified |
| `verticalPodAutoscaler` | VerticalPodAutoscaler | Created **only** when this overlay is specified |
| `podDisruptionBudget` | PodDisruptionBudget | Created **only** when this overlay is specified |

{{< callout type="info" >}}
**HPA, VPA, and PDB are opt-in.** Unlike Deployment, Service, and ServiceAccount, the control plane does not create HPA, VPA, or PDB resources by default. These resources are created only when you provide an overlay for them. This gives you full control over autoscaling and disruption policies.
{{< /callout >}}

### Precedence: GatewayClass vs Gateway parameters {#precedence}

You can attach {{< reuse "docs/snippets/gatewayparameters.md" >}} to either a GatewayClass (shared by all Gateways using that class) or to an individual Gateway. When both are specified, they are processed in the following order:

1. **GatewayClass configs are applied first** - Settings like `envoyContainer`, `service`, `podTemplate`
2. **Gateway configs merge on top** - Gateway configs override conflicting GatewayClass configs
3. **GatewayClass overlays are applied** - After all configs are processed, overlays modify the rendered resources
4. **Gateway overlays merge on top** - Gateway overlays override conflicting GatewayClass overlays

This means all configs from both sources are fully processed before any overlay is applied. The overlays then modify the already-rendered Kubernetes resources.

The overlay merge uses strategic merge patch semantics, which means:
- For scalar values (like `replicas`), Gateway wins
- For maps (like `labels`), keys are merged, with Gateway winning on conflicts
- For lists (like `containers`), items are merged by their merge key (e.g., `name` for containers)

{{< callout type="warning" >}}
**Debugging tip:** When overlays don't behave as expected, check if you have parameters on both the GatewayClass and Gateway. Each overlay might look correct individually but produce unexpected results when merged in serial. Use `kubectl get deployment <gateway-name> -o yaml` to see the final merged result.
{{< /callout >}}

## Overlays cookbook {#overlays-cookbook}

The following recipes demonstrate common overlay patterns. Each recipe shows a complete {{< reuse "docs/snippets/gatewayparameters.md" >}} resource that you can adapt to your needs.

### Remove security context for OpenShift {#recipe-openshift}

OpenShift manages security contexts through Security Context Constraints (SCCs). Remove the default security context to allow OpenShift to assign appropriate values.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: envoy-openshift
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    # Alternatively, use the omitDefaultSecurityContext config option
    omitDefaultSecurityContext: true
EOF
```

Alternatively, if you need more fine-grained control, use overlays:

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: envoy-openshift-overlay
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    deploymentOverlay:
      spec:
        template:
          spec:
            # Delete pod-level securityContext using $patch: delete (works with any apply mode)
            securityContext:
              $patch: delete
            containers:
              - name: envoy
                # Delete container-level securityContext using null (requires server-side apply)
                securityContext: null
EOF
```

### Set up Horizontal Pod Autoscaler (HPA) {#recipe-hpa}

Configure automatic scaling based on CPU utilization. The HPA resource is only created when you specify this overlay.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: envoy-hpa
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    horizontalPodAutoscaler:
      metadata:
        labels:
          app: envoy
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

### Set up Vertical Pod Autoscaler (VPA) {#recipe-vpa}

Configure automatic resource recommendations. The VPA resource is only created when you specify this overlay.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: envoy-vpa
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    verticalPodAutoscaler:
      metadata:
        labels:
          app: envoy
      spec:
        updatePolicy:
          updateMode: "Auto"
        resourcePolicy:
          containerPolicies:
            - containerName: envoy
              minAllowed:
                cpu: 100m
                memory: 128Mi
              maxAllowed:
                cpu: 2
                memory: 2Gi
EOF
```

### Set up Pod Disruption Budget (PDB) {#recipe-pdb}

Configure a Pod Disruption Budget to ensure availability during voluntary disruptions. The PDB resource is only created when you specify this overlay.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: envoy-pdb
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    podDisruptionBudget:
      metadata:
        labels:
          app: envoy
      spec:
        minAvailable: 1
EOF
```

### Customize service ports {#recipe-service-ports}

Replace the default service ports with custom port configurations.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: envoy-service-ports
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    serviceOverlay:
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

### Static IP for LoadBalancer {#recipe-static-ip}

Assign a static IP address to the LoadBalancer service.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: envoy-static-ip
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    serviceOverlay:
      spec:
        loadBalancerIP: 203.0.113.10
EOF
```

### Add init containers {#recipe-init-containers}

Add init containers that run before the main Envoy container starts.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: envoy-init
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    deploymentOverlay:
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

Add sidecar containers alongside the main Envoy container.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: envoy-sidecar
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    deploymentOverlay:
      spec:
        template:
          spec:
            containers:
              - name: envoy
                # This merges with the existing envoy container
              - name: log-shipper
                image: fluent/fluent-bit:latest
                volumeMounts:
                  - name: logs
                    mountPath: /var/log/envoy
EOF
```

### Custom Istio sidecar proxy {#recipe-istio-sidecar}

When running in an Istio service mesh, you can replace the default Istio sidecar proxy with a custom image. Use `$patch: replace` on the container to completely replace its configuration rather than merging.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: envoy-custom-istio
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    deploymentOverlay:
      spec:
        template:
          spec:
            containers:
              - name: istio-proxy
                $patch: replace
                image: customproxy:custom-tag
                args:
                  - "proxy"
EOF
```

{{< callout type="info" >}}
**Note:** The `$patch: replace` directive completely replaces the `istio-proxy` container definition rather than merging with the existing one. This is useful when you need full control over the container spec, but means you must provide all required fields.
{{< /callout >}}

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

2. **Wrong container name:** When modifying container settings, you must specify the correct container name (`envoy`) as the merge key.

   ```yaml
   # Wrong - missing container name, won't merge with existing container
   containers:
     - resources:
         limits:
           memory: 512Mi

   # Correct - includes container name as merge key
   containers:
     - name: envoy
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

**Symptoms:** The Envoy pod enters CrashLoopBackOff or fails to schedule.

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

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete gateway custom -n kgateway-system
kubectl delete {{< reuse "docs/snippets/gatewayparameters.md" >}} custom-gw-params -n kgateway-system
``` 
