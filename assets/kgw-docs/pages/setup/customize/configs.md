Review common proxy customizations that you might want to apply in your environment. For steps on how to apply these configurations, see [Change proxy settings]({{< link-hextra path="/setup/customize/gateway/" >}}).

## Horizontal Pod Autoscaler (HPA) {#hpa}

Use `horizontalPodAutoscaler` to automatically create an HPA that targets the gateway proxy Deployment. The HPA is only created when this field is present. The `scaleTargetRef` is automatically configured to point to the proxy Deployment.

{{< callout type="info" >}}
Do not set `kube.deployment.replicas` when using an HPA. If a fixed replica count is set, the HPA cannot scale the Deployment.
{{< /callout >}}

1. Install the Kubernetes `metrics-server` if it is not already running in your cluster.

   ```sh
   kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
   ```

2. Update your {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resource to add a `horizontalPodAutoscaler`. The following example scales the gateway proxy between 2 and 10 replicas based on CPU utilization.

   ```yaml
   kubectl apply --server-side -f- <<'EOF'
   apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
   metadata:
     name: gw-params
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     kube:
       horizontalPodAutoscaler:
         metadata:
           labels:
             app.kubernetes.io/name: gw-params
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

3. Create a Gateway that references your {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}.

   ```yaml
   kubectl apply -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: custom
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "kgw-docs/snippets/gatewayclass.md" >}}
     infrastructure:
       parametersRef:
         name: gw-params
         group: {{< reuse "kgw-docs/snippets/trafficpolicy-group.md" >}}
         kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
     listeners:
     - protocol: HTTP
       port: 80
       name: http
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

4. Verify that the HPA was created and is targeting the gateway proxy Deployment.

   ```sh
   kubectl get hpa -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
   ```

   Example output:

   ```
   NAME     REFERENCE          TARGETS         MINPODS   MAXPODS   REPLICAS   AGE
   custom   Deployment/custom  <unknown>/80%   2         10        2          30s
   ```

## Vertical Pod Autoscaler (VPA) {#vpa}

Use `verticalPodAutoscaler` to automatically create a VPA that targets the gateway proxy Deployment. The VPA is only created when this field is present. The `targetRef` is automatically configured to point to the proxy Deployment.

{{< callout type="info" >}}
The VPA feature requires the [Kubernetes VPA controller](https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler) to be installed in your cluster.
{{< /callout >}}

1. Install the VPA controller if it is not already running in your cluster. See the [VPA installation guide](https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler#installation) for instructions.

2. Update your {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resource to add a `verticalPodAutoscaler`. The following example configures the VPA to automatically adjust resource requests in `Auto` mode within defined bounds.

   ```yaml
   kubectl apply --server-side -f- <<'EOF'
   apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
   metadata:
     name: gw-params
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     kube:
       verticalPodAutoscaler:
         metadata:
           labels:
             app.kubernetes.io/name: gw-params
         spec:
           updatePolicy:
             updateMode: Auto
           resourcePolicy:
             containerPolicies:
               - containerName: "*"
                 minAllowed:
                   cpu: 50m
                   memory: 64Mi
                 maxAllowed:
                   cpu: 2
                   memory: 2Gi
   EOF
   ```

3. Create a Gateway that references your {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}.

   ```yaml
   kubectl apply -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: custom
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "kgw-docs/snippets/gatewayclass.md" >}}
     infrastructure:
       parametersRef:
         name: gw-params
         group: {{< reuse "kgw-docs/snippets/trafficpolicy-group.md" >}}
         kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
     listeners:
     - protocol: HTTP
       port: 80
       name: http
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

4. Verify that the VPA was created and is targeting the gateway proxy Deployment.

   ```sh
   kubectl get vpa -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
   ```

   Example output:

   ```
   NAME     MODE   CPU   MEM    PROVIDED   AGE
   custom   Auto   50m   64Mi   True       30s
   ```

## Pod Disruption Budget (PDB) {#pdb}

Use `podDisruptionBudget` to automatically create a PDB that targets the gateway proxy Deployment. The PDB is only created when this field is present. The `selector` is automatically configured to match the proxy pods.

The following example ensures that at least one gateway proxy pod remains available during voluntary disruptions such as cluster upgrades.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  kube:
    podDisruptionBudget:
      metadata:
        labels:
          app.kubernetes.io/name: gw-params
      spec:
        minAvailable: 1
EOF
```

## OpenShift security contexts {#openshift-security-context}

OpenShift manages security contexts through Security Context Constraints (SCCs). Set the built-in `omitDefaultSecurityContext` field to prevent the control plane from adding default pod and container security contexts, so that OpenShift can assign appropriate values.

```yaml
kubectl apply -f- <<'EOF'
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  kube:
    omitDefaultSecurityContext: true
EOF
```

## Deployment overlays

Use `deploymentOverlay` to apply a strategic merge patch only for Deployment settings that do not have built-in {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} fields. For details about scalar replacement, map and list merging, deletion directives, and overlay precedence, see [Customization options]({{< link-hextra path="/setup/customize/options/#overlays" >}}).

### Add init containers {#init-containers}

Add init containers that run before the main proxy container starts. Because `initContainers` uses `name` as its strategic merge patch key, this item is appended without replacing any init containers that are already present.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  kube:
    deploymentOverlay:
      spec:
        template:
          spec:
            initContainers:
              - name: initialize-gateway
                image: busybox:1.36
                command: ["sh", "-c", "echo initialization complete"]
EOF
```

### Add sidecar containers {#sidecar-containers}

Add a generic sidecar alongside the proxy container. The `containers` list also merges on `name`, so the sidecar is appended and the generated proxy container is preserved.

{{< callout type="info" >}}
For TLS certificate handling, use the built-in `sdsContainer` field instead of adding a custom sidecar.
{{< /callout >}}

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  kube:
    deploymentOverlay:
      spec:
        template:
          spec:
            containers:
              - name: custom-sidecar
                image: busybox:1.36
                command: ["sh", "-c", "tail -f /dev/null"]
EOF
```
