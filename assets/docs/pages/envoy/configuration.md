Customize your Envoy proxy with {{< reuse "docs/snippets/gatewayparameters.md" >}}.

## About customizing your proxy {#proxy-configuration}

When you create a Gateway resource, {{< reuse "docs/snippets/kgateway.md" >}} provisions the data plane for you, including a Deployment, Service, and ServiceAccount. You can customize these resources using the {{< reuse "docs/snippets/gatewayparameters.md" >}} custom resource.

You can choose between the following options to customize your Envoy proxy:

* **Configs (recommended)**: The {{< reuse "docs/snippets/gatewayparameters.md" >}} resource provides typed configuration fields for common customizations like container images, resource limits, log levels, and more. Configs are validated by the control plane when the data plane is created or updated, catching errors early.
* **Overlays (strategic merge patch)**: For advanced customization of the Kubernetes resources that the control plane generates (such as Deployments, Services, ServiceAccounts), you can use overlays. Overlays use [Kubernetes strategic merge patch](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-api-machinery/strategic-merge-patch.md) semantics to modify the generated resources after they are rendered. See the [Overlays section](#overlays) for details and the [Overlays cookbook](#overlays-cookbook) for common recipes.

## Before you begin

Set up an [Envoy gateway proxy]({{< link-hextra path="/setup/default/" >}}).

## Step 1: Customize with configs {#configs}

The {{< reuse "docs/snippets/gatewayparameters.md" >}} resource provides typed configuration fields for common customizations. These fields are validated by the control plane, catching errors early.

1. Create a {{< reuse "docs/snippets/gatewayparameters.md" >}} resource with your custom configuration. The following example changes the Envoy log level to `debug` and sets resource limits.
   ```yaml
   kubectl apply -f- <<'EOF'
   apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
   metadata:
     name: custom-envoy-config
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     kube:
       envoyContainer:
         bootstrap:
           logLevel: debug
         resources:
           requests:
             cpu: 100m
             memory: 128Mi
           limits:
             cpu: 500m
             memory: 512Mi
   EOF
   ```

2. Create a Gateway resource that uses your {{< reuse "docs/snippets/gatewayparameters.md" >}}.

   ```yaml
   kubectl apply -f- <<'EOF'
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: custom-envoy
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "docs/snippets/gatewayclass.md" >}}
     infrastructure:
       parametersRef:
         name: custom-envoy-config
         group: {{< reuse "docs/snippets/gatewayparam-group.md" >}}
         kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
     listeners:
       - name: http
         port: 8080
         protocol: HTTP
         allowedRoutes:
           namespaces:
             from: All
   EOF
   ```

3. Check the pod logs to verify that Envoy is using the debug log level.
   ```sh
   kubectl logs deployment/custom-envoy -n {{< reuse "docs/snippets/namespace.md" >}}
   ```

## Overlays (strategic merge patch) {#overlays}

Overlays let you customize the Kubernetes resources that the control plane generates for your Envoy proxy. When you create a Gateway, the control plane generates resources like Deployments, Services, and ServiceAccounts. Overlays use [Kubernetes strategic merge patch (SMP)](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-api-machinery/strategic-merge-patch.md) semantics to modify these resources after they are rendered. For additional examples, see the [kubectl patch documentation](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/update-api-object-kubectl-patch/#use-a-strategic-merge-patch-to-update-a-deployment).

### Configs vs overlays {#configs-vs-overlays}

The {{< reuse "docs/snippets/gatewayparameters.md" >}} API provides two ways to customize your proxy:

| Approach | Validation | Stability | Use case |
|----------|------------|-----------|----------|
| **Configs** (e.g., `envoyContainer`, `service`, `podTemplate`) | Validated by control plane when data plane is created or updated | Stable API contract | Common settings like image names, logging levels, resource limits |
| **Overlays** (e.g., `deploymentOverlay`, `serviceOverlay`) | Validated by Kubernetes when resources are created, not by the control plane | No stability guarantee | All Kubernetes customization not exposed through configs |

**Use configs when possible.** Configs are validated by the control plane when the data plane is created or updated, catching errors early. They also provide a stable API that won't break across upgrades.

**Use overlays for everything else.** Overlays give you full control over the generated Kubernetes resources, but they operate on internal implementation details that may change between versions.

### When to use overlays

Overlays are useful when you need to customize resources in ways that are not directly exposed through the {{< reuse "docs/snippets/gatewayparameters.md" >}} configs. Common use cases include:

- Adding image pull secrets to pull from private registries
- Removing default security contexts for platforms like OpenShift
- Adding custom labels, annotations, or environment variables
- Configuring pod scheduling (node selectors, affinities, tolerations)
- Setting up Horizontal Pod Autoscalers (HPA), Vertical Pod Autoscalers (VPA), or Pod Disruption Budgets (PDB)
- Mounting custom ConfigMaps or Secrets as volumes
- Configuring cloud provider-specific service annotations

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

**Example: Potential conflict**

Consider a GatewayClass with:
```yaml
spec:
  kube:
    deploymentOverlay:
      spec:
        replicas: 3
        template:
          spec:
            containers:
              - name: envoy
                resources:
                  limits:
                    memory: 512Mi
```

And a Gateway with:
```yaml
spec:
  kube:
    deploymentOverlay:
      spec:
        replicas: 5
        template:
          spec:
            containers:
              - name: envoy
                resources:
                  limits:
                    cpu: 500m
```

The result merges both:
- `replicas: 5` (Gateway wins)
- `memory: 512Mi` from GatewayClass is preserved
- `cpu: 500m` from Gateway is added

{{< callout type="warning" >}}
**Debugging tip:** When overlays don't behave as expected, check if you have parameters on both the GatewayClass and Gateway. Each overlay might look correct individually but produce unexpected results when merged in serial. Use `kubectl get deployment <gateway-name> -o yaml` to see the final merged result.
{{< /callout >}}

## Overlays cookbook {#overlays-cookbook}

The following recipes demonstrate common overlay patterns. Each recipe shows a complete {{< reuse "docs/snippets/gatewayparameters.md" >}} resource that you can adapt to your needs.

### Change deployment replicas {#recipe-replicas}

Set a specific number of replicas for the Envoy deployment.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: envoy-replicas
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    deploymentOverlay:
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
  name: envoy-pull-secrets
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    deploymentOverlay:
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

### Add environment variables {#recipe-env-vars}

Add custom environment variables to the Envoy container using configs.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: envoy-env
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    envoyContainer:
      env:
        - name: MY_CUSTOM_VAR
          value: "my-value"
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
EOF
```

### Configure pod scheduling {#recipe-pod-scheduling}

Configure node selectors, affinities, tolerations, and topology spread constraints to control where Envoy pods are scheduled.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: envoy-scheduling
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    deploymentOverlay:
      spec:
        template:
          spec:
            nodeSelector:
              node-type: gateway
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
                value: gateway
                effect: NoSchedule
            topologySpreadConstraints:
              - maxSkew: 1
                topologyKey: kubernetes.io/hostname
                whenUnsatisfiable: DoNotSchedule
                labelSelector:
                  matchLabels:
                    app: envoy
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

### Mount custom ConfigMap as volume {#recipe-configmap-volume}

Mount a custom ConfigMap into the Envoy container.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: envoy-custom-volume
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    deploymentOverlay:
      spec:
        template:
          spec:
            volumes:
              - name: custom-config
                configMap:
                  name: my-custom-config
            containers:
              - name: envoy
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
  name: envoy-labels
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    deploymentOverlay:
      metadata:
        labels:
          environment: production
          team: platform
        annotations:
          description: "Production Envoy proxy"
      spec:
        template:
          metadata:
            labels:
              environment: production
            annotations:
              prometheus.io/scrape: "true"
              prometheus.io/port: "9091"
    serviceOverlay:
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

### Set resource requests and limits {#recipe-resources}

Configure CPU and memory requests and limits for the Envoy container using configs.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: envoy-resources
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    envoyContainer:
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

Configure custom security settings for the pod.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: envoy-security
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    podTemplate:
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
  name: envoy-remove-label
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    deploymentOverlay:
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
  name: envoy-replace-volumes
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    deploymentOverlay:
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
  name: envoy-image
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    envoyContainer:
      image:
        registry: my-registry.io
        repository: my-org/envoy
        tag: v1.30.0
        pullPolicy: Always
EOF
```

You can also pin to a specific digest for immutable deployments:

```yaml
spec:
  kube:
    envoyContainer:
      image:
        registry: my-registry.io
        repository: my-org/envoy
        digest: sha256:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890
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

### GKE-specific service annotations {#recipe-gke}

Configure GKE-specific features like Regional Backend Services (RBS) and static IPs using service annotations.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: envoy-gke
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    serviceOverlay:
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
  name: envoy-aws
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    serviceOverlay:
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
  name: envoy-azure
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    serviceOverlay:
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
  name: envoy-delete-security
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    deploymentOverlay:
      spec:
        template:
          spec:
            # Delete pod-level securityContext using $patch: delete
            securityContext:
              $patch: delete
            containers:
              - name: envoy
                # Delete container-level securityContext:
                securityContext:
                  $patch: delete
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

### ServiceAccount annotations for IAM {#recipe-sa-iam}

Add annotations to the ServiceAccount for cloud provider IAM integration (e.g., AWS IRSA, GKE Workload Identity).

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: envoy-iam
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    serviceAccountOverlay:
      metadata:
        annotations:
          # AWS IRSA
          eks.amazonaws.com/role-arn: "arn:aws:iam::123456789012:role/envoy-role"
          # Or GKE Workload Identity
          # iam.gke.io/gcp-service-account: "envoy@my-project.iam.gserviceaccount.com"
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

## Clean up

{{< reuse "docs/snippets/cleanup.md" >}}

```bash
kubectl delete Gateway custom-envoy -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete {{< reuse "docs/snippets/gatewayparameters.md" >}} custom-envoy-config -n {{< reuse "docs/snippets/namespace.md" >}}
```
