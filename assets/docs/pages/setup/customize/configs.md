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

2. Update your {{< reuse "docs/snippets/gatewayparameters.md" >}} resource to add a `horizontalPodAutoscaler`. The following example scales the gateway proxy between 2 and 10 replicas based on CPU utilization.

   ```yaml
   kubectl apply --server-side -f- <<'EOF'
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
   metadata:
     name: gw-params
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
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

3. Create a Gateway that references your {{< reuse "docs/snippets/gatewayparameters.md" >}}.

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
         name: gw-params
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

4. Verify that the HPA was created and is targeting the gateway proxy Deployment.

   ```sh
   kubectl get hpa -n {{< reuse "docs/snippets/namespace.md" >}}
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

2. Update your {{< reuse "docs/snippets/gatewayparameters.md" >}} resource to add a `verticalPodAutoscaler`. The following example configures the VPA to automatically adjust resource requests in `Auto` mode within defined bounds.

   ```yaml
   kubectl apply --server-side -f- <<'EOF'
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
   metadata:
     name: gw-params
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
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

3. Create a Gateway that references your {{< reuse "docs/snippets/gatewayparameters.md" >}}.

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
         name: gw-params
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

4. Verify that the VPA was created and is targeting the gateway proxy Deployment.

   ```sh
   kubectl get vpa -n {{< reuse "docs/snippets/namespace.md" >}}
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
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
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

## Deployment overlays

Use `deploymentOverlay` to apply a strategic merge patch to the generated proxy Deployment.

### Change deployment replicas {#deployment-replicas}

Set a specific number of replicas for the gateway proxy Deployment.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    deploymentOverlay:
      spec:
        replicas: 3
EOF
```

### Image pull secrets {#image-pull-secrets}

Add image pull secrets to pull container images from private registries.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
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

### Add init containers {#init-containers}

Add init containers that run before the main proxy container starts.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
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

### Add sidecar containers {#sidecar-containers}

Add sidecar containers alongside the main proxy container.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    deploymentOverlay:
      spec:
        template:
          spec:
            containers:
              - name: kgateway
                # Merges with the existing proxy container
              - name: log-shipper
                image: fluent/fluent-bit:latest
                volumeMounts:
                  - name: logs
                    mountPath: /var/log/proxy
EOF
```

### Pod and node affinity {#pod-scheduling}

Configure node selectors, affinities, tolerations, and topology spread constraints to control where gateway proxy pods are scheduled.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
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
                    app: kgateway
EOF
```

### Custom pod security context {#security-context}

Configure custom security settings for the pod.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    deploymentOverlay:
      spec:
        template:
          spec:
            securityContext:
              runAsUser: 1000
              runAsGroup: 2000
              fsGroup: 3000
EOF
```

### Remove security context for OpenShift {#openshift-security-context}

OpenShift manages security contexts through Security Context Constraints (SCCs). Remove the default security context to allow OpenShift to assign appropriate values. Use `$patch: delete` to remove the pod-level security context, or set a container-level field to `null` to clear it.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    deploymentOverlay:
      spec:
        template:
          spec:
            # Remove the pod-level securityContext
            securityContext:
              $patch: delete
            containers:
              - name: kgateway
                # Remove the container-level securityContext
                securityContext: null
EOF
```

### Custom labels and annotations {#labels-annotations}

Add custom labels and annotations to the proxy Deployment and pods.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    deploymentOverlay:
      metadata:
        labels:
          environment: production
          team: platform
        annotations:
          description: "Production gateway proxy"
      spec:
        template:
          metadata:
            labels:
              environment: production
            annotations:
              prometheus.io/scrape: "true"
              prometheus.io/port: "9091"
EOF
```

### Mount a ConfigMap as a volume {#configmap-volume}

Mount a custom ConfigMap to the proxy container.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
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
              - name: kgateway
                volumeMounts:
                  - name: custom-config
                    mountPath: /etc/custom-config
                    readOnly: true
EOF
```

### Replace all volumes {#replace-volumes}

Use `$patch: replace` to completely replace the list of volumes instead of merging with the default list. Place `$patch: replace` as a separate list item before your actual volumes.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
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
Place `$patch: replace` as a separate list item **before** your actual items. If you include it in the same item as your configuration, you might end up with an empty list.
{{< /callout >}}

## Service overlays

Use `serviceOverlay` to apply a strategic merge patch to the generated proxy Service.

### Add service annotations {#service-annotations}

Add annotations to the proxy Service. A common use case is adding cloud provider-specific annotations for load balancer configuration.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    serviceOverlay:
      metadata:
        annotations:
          service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
EOF
```

### Static IP for LoadBalancer {#static-ip}

Assign a static IP address to the LoadBalancer Service.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    serviceOverlay:
      spec:
        loadBalancerIP: 203.0.113.10
EOF
```

### AWS EKS load balancer annotations {#aws-eks-annotations}

Configure AWS-specific load balancer features using Service annotations.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
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

### GKE service annotations {#gke-annotations}

Configure GKE-specific features like Regional Backend Services and static IPs using Service annotations.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
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

### Azure AKS load balancer annotations {#azure-aks-annotations}

Configure Azure-specific load balancer features using Service annotations.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
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

## ServiceAccount overlays

Use `serviceAccountOverlay` to apply a strategic merge patch to the generated proxy ServiceAccount.

### ServiceAccount annotations for IAM {#sa-iam-annotations}

Add annotations to the ServiceAccount for cloud provider IAM integration, such as AWS IRSA or GKE Workload Identity.

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    serviceAccountOverlay:
      metadata:
        annotations:
          # AWS IRSA
          eks.amazonaws.com/role-arn: "arn:aws:iam::123456789012:role/gateway-role"
          # Or GKE Workload Identity
          # iam.gke.io/gcp-service-account: "gateway@my-project.iam.gserviceaccount.com"
EOF
```
