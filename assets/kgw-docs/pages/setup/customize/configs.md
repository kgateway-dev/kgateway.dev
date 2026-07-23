Review common proxy customizations that you might want to apply in your environment. The examples use built-in API fields whenever they are available and reserve overlays for settings that have no built-in equivalent. For steps on how to apply these configurations, see [Change proxy settings]({{< link-hextra path="/setup/customize/gateway/" >}}).

## Horizontal Pod Autoscaler (HPA) {#hpa}

Use `horizontalPodAutoscaler` to automatically create an HPA that targets the gateway proxy Deployment. The HPA is only created when this field is present. The `scaleTargetRef` is automatically configured to point to the proxy Deployment.

> [!NOTE]
> Do not set `kube.deployment.replicas` when using an HPA. If a fixed replica count is set, the HPA cannot scale the Deployment.

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

> [!NOTE]
> The VPA feature requires the [Kubernetes VPA controller](https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler) to be installed in your cluster.

1. Install the VPA controller if it is not already running in your cluster. See the [VPA installation guide](https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler#getting-started) for instructions.

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

## Deployment and pod configuration

Use the built-in `deployment`, `podTemplate`, and `envoyContainer` fields for common Deployment, pod, and proxy-container settings.

### Change deployment replicas {#deployment-replicas}

Set a specific number of replicas for the gateway proxy Deployment with the built-in `deployment.replicas` field.

```yaml
kubectl apply -f- <<'EOF'
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  kube:
    deployment:
      replicas: 3
EOF
```

> [!NOTE]
> Do not set `deployment.replicas` when you use an HPA, because the fixed value conflicts with autoscaling.

### Image pull secrets {#image-pull-secrets}

Add image pull secrets to pull container images from private registries with the built-in `podTemplate.imagePullSecrets` field.

```yaml
kubectl apply -f- <<'EOF'
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  kube:
    podTemplate:
      imagePullSecrets:
        - name: my-registry-secret
EOF
```

### Pod and node affinity {#pod-scheduling}

Use the built-in `podTemplate` fields to configure node selectors, affinities, tolerations, and topology spread constraints that control where gateway proxy pods are scheduled.

```yaml
kubectl apply -f- <<'EOF'
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  kube:
    podTemplate:
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
              app: kgateway
EOF
```

### Custom pod security context {#security-context}

Configure custom pod security settings with the built-in `podTemplate.securityContext` field. To customize the proxy container security context instead, use `envoyContainer.securityContext`.

```yaml
kubectl apply -f- <<'EOF'
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  kube:
    podTemplate:
      securityContext:
        runAsUser: 1000
        runAsGroup: 2000
        fsGroup: 3000
EOF
```

### Remove default security contexts for OpenShift {#openshift-security-context}

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

### Custom labels and annotations {#labels-annotations}

Use `Gateway.spec.infrastructure.labels` and `Gateway.spec.infrastructure.annotations` to add metadata to all managed resources for a Gateway, including the Deployment and pods. Use resource-specific `extraLabels` and `extraAnnotations` fields in {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} when the metadata must apply to only the pods, Service, or ServiceAccount.

```yaml
kubectl apply -f- <<'EOF'
kind: Gateway
apiVersion: gateway.networking.k8s.io/v1
metadata:
  name: custom
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  gatewayClassName: {{< reuse "kgw-docs/snippets/gatewayclass.md" >}}
  infrastructure:
    labels:
      environment: production
      team: platform
    annotations:
      description: "Production gateway proxy"
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

### Mount a ConfigMap as a volume {#configmap-volume}

Use `podTemplate.extraVolumes` to add a ConfigMap-backed volume and `envoyContainer.extraVolumeMounts` to mount it in the proxy container.

```yaml
kubectl apply -f- <<'EOF'
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  kube:
    podTemplate:
      extraVolumes:
        - name: custom-config
          configMap:
            name: my-custom-config
    envoyContainer:
      extraVolumeMounts:
        - name: custom-config
          mountPath: /etc/custom-config
          readOnly: true
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

Add a sidecar container alongside the proxy container. Because `name` is the merge key for the `containers` list, your sidecar is added as a new entry without affecting the generated proxy container.

> [!NOTE]
> For TLS certificate handling, use the built-in `sdsContainer` field instead of adding a custom sidecar.

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

### Replace all volumes {#replace-volumes}

Use `$patch: replace` to take full control of the pod volume list instead of merging additional volumes with `podTemplate.extraVolumes`. Place `$patch: replace` as a separate list item before the actual volumes.

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
            volumes:
              - $patch: replace
              - name: custom-config
                configMap:
                  name: my-custom-config
EOF
```

> [!CAUTION]
> Replacing all volumes removes volumes that are generated by the control plane and can prevent the proxy from starting. A production replacement must re-declare every generated volume that the proxy requires. If you only need to add volumes, use `podTemplate.extraVolumes` instead.

## Service configuration

Use the built-in `service` fields for Service settings. Use `Gateway.spec.addresses` for a static load-balancer address.

### Add service annotations {#service-annotations}

Add annotations to the proxy Service with `service.extraAnnotations`. A common use case is adding cloud provider-specific load-balancer configuration.

```yaml
kubectl apply -f- <<'EOF'
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  kube:
    service:
      extraAnnotations:
        service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
EOF
```

### Static IP for LoadBalancer {#static-ip}

Assign a static IP address to the Service that exposes the gateway proxy with `Gateway.spec.addresses`.

```yaml
kubectl apply -f- <<'EOF'
kind: Gateway
apiVersion: gateway.networking.k8s.io/v1
metadata:
  name: custom
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  gatewayClassName: {{< reuse "kgw-docs/snippets/gatewayclass.md" >}}
  addresses:
    - type: IPAddress
      value: 203.0.113.10
  listeners:
    - protocol: HTTP
      port: 80
      name: http
      allowedRoutes:
        namespaces:
          from: All
EOF
```

### LoadBalancer source IP ranges {#load-balancer-source-ranges}

Set up an allowlist with `service.loadBalancerSourceRanges` to restrict which source client IPs can connect to the LoadBalancer Service that exposes the gateway proxy.

```yaml
kubectl apply -f- <<'EOF'
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  kube:
    service:
      type: LoadBalancer
      loadBalancerSourceRanges:
        - 10.0.0.0/8
        - 192.168.0.0/16
EOF
```

### AWS EKS load balancer annotations {#aws-eks-annotations}

Configure AWS-specific load-balancer features with `service.extraAnnotations`.

```yaml
kubectl apply -f- <<'EOF'
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  kube:
    service:
      extraAnnotations:
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

### GKE service annotations {#gke-annotations}

Configure GKE-specific features such as Regional Backend Services and reserved IP addresses with `service.extraAnnotations`.

```yaml
kubectl apply -f- <<'EOF'
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  kube:
    service:
      extraAnnotations:
        # Enable Regional Backend Services for better load balancing
        cloud.google.com/l4-rbs: "enabled"
        # Use pre-reserved static IPs
        networking.gke.io/load-balancer-ip-addresses: "my-v4-ip,my-v6-ip"
        # Specify the subnet for internal load balancers
        networking.gke.io/load-balancer-subnet: "my-subnet"
EOF
```

### Azure AKS load balancer annotations {#azure-aks-annotations}

Configure Azure-specific load-balancer features with `service.extraAnnotations`.

```yaml
kubectl apply -f- <<'EOF'
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  kube:
    service:
      extraAnnotations:
        # Make it internal
        service.beta.kubernetes.io/azure-load-balancer-internal: "true"
        # Specify resource group for the load balancer
        service.beta.kubernetes.io/azure-load-balancer-resource-group: "my-resource-group"
EOF
```

## ServiceAccount configuration

Use the built-in `serviceAccount` field for ServiceAccount settings.

### ServiceAccount annotations for IAM {#sa-iam-annotations}

Add annotations with `serviceAccount.extraAnnotations` for cloud provider IAM integrations such as AWS IRSA or GKE Workload Identity.

```yaml
kubectl apply -f- <<'EOF'
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  kube:
    serviceAccount:
      extraAnnotations:
        # AWS IRSA
        eks.amazonaws.com/role-arn: "arn:aws:iam::123456789012:role/gateway-role"
        # Or GKE Workload Identity
        # iam.gke.io/gcp-service-account: "gateway@my-project.iam.gserviceaccount.com"
EOF
```
