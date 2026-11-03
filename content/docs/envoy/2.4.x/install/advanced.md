---
title: Advanced settings
weight: 70
description: Install kgateway and related components.
---

{{< reuse "kgw-docs/pages/install/advanced.md" >}}

## Common labels

Add custom labels to all resources that are created by the Helm charts, including the Deployment, Service, ServiceAccount, and ClusterRoles. This allows you to better organize your resources or integrate with external tooling. 

The following snippet adds the `label-key` and `kgw-managed` labels to all resources. 

```yaml
commonLabels: 
  label-key: label-value
  kgw-managed: "true"
```

## Topology spread constraints

Use topology spread constraints to control how kgateway controller pods are distributed across failure domains such as zones or nodes. This setup helps improve availability and resilience by preventing all replicas from landing in the same zone or node.

For more information, see the [Kubernetes topology spread constraints documentation](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/).

The following example spreads controller pods evenly across availability zones, and prevents scheduling if the skew cannot be satisfied.

```yaml
topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: topology.kubernetes.io/zone
    whenUnsatisfiable: DoNotSchedule
    labelSelector:
      matchLabels:
        app.kubernetes.io/name: kgateway
```

## PriorityClass

You can assign a PriorityClassName to the control plane pods by using the Helm chart. [Priority](https://kubernetes.io/docs/concepts/scheduling-eviction/pod-priority-preemption/) indicates the importance of a pod relative to other pods. If a pod cannot be scheduled, the scheduler tries to preempt (evict) lower priority pods to make scheduling of the pending pod possible. 

To assign a PriorityClassName to the control plane, you must first create a PriorityClass resource. The following example creates a PriorityClass with the name `system-cluster-critical` that assigns a priority of 1 million. 

```yaml
kubectl apply -f- <<EOF
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: system-cluster-critical
value: 1000000
globalDefault: false
description: "Use this priority class on system-critical pods only."
EOF
```

In your Helm values file, add the name of the PriorityClass in the `controller.priorityClassName` field. 

```yaml
controller: 
  priorityClassName: 
```

## Autoscaling

You can configure Horizontal Pod Autoscaler (HPA) or Vertical Pod Autoscaler (VPA) policies for the {{< reuse "kgw-docs/snippets/kgateway.md" >}} control plane. To set up these policies, you use the `horizontalPodAutoscaler` or `verticalPodAutoscaler` fields in the Helm chart.

> [!NOTE]
> Note that {{< reuse "kgw-docs/snippets/kgateway.md" >}} uses leader election if multiple replicas are present. The elected leader's workload is typically larger than the workload of non-leader replicas and therefore drives the overall infrastructure cost. Because of that, Vertical Pod Autoscaling can be a reasonable solution to ensure that the elected leader has the resources it needs to perform its work successfully. In cases where the leader has a large workload, Horizontal Pod Autoscaling might not be as effective, as it adds more replicas that do not reduce the workload of the elected leader.

> [!WARNING]
> If you plan to set up both VPA and HPA policies, make sure to closely monitor performance and cost during scale up events. Using both policies can lead to conflict or even destructive loops that impact the performance of your control plane.


### Vertical Pod Autoscaler (VPA)

Vertical Pod Autoscaler (VPA) is a Kubernetes component that automatically adjusts the CPU and memory reservations of your pods to match their actual usage. 

The following Helm configuration ensures that the control plane pod is always assigned a minimum of 0.1 CPU cores (100millicores) and 128Mi of memory. 

```yaml
controller:
  verticalPodAutoscaler:
    updatePolicy:
      updateMode: Auto
    resourcePolicy:
      containerPolicies:
      - containerName: "*"
        minAllowed:
          cpu: 100m
          memory: 128Mi
```

### Horizontal Pod Autoscaler (HPA)

Horizontal Pod Autoscaler (HPA) adds more instances of the pod to your environment when certain memory or CPU thresholds are reached. 

In the following example, you want to have 1 control plane replica running at any given time. If the CPU utilization averages 80%, you want to gradually scale up your replicas. You can have a maximum of 5 replicas at any given time. 
```yaml
controller: 
  horizontalPodAutoscaler:
    minReplicas: 1
    maxReplicas: 5
    metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 80
```


**Note**: To monitor the memory and CPU threshold, you must deploy the Kubernetes `metrics-server` to your cluster. The `metrics-server` retrieves metrics, such as CPU and memory consumption, for your workloads. 

You can install the server with the following command: 
```sh
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl -n kube-system patch deployment metrics-server \
 --type=json \
 -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'
```

Then, start monitoring CPU and memory consumption with the `kubectl top pod` command. 

## PodDisruptionBudget

Configure a Pod Disruption Budget to ensure that a minimum number of control plane instances are up and running at any given time during voluntary disruptions, such as upgrades. In this example, 50% of your control plane instances must be running.

```yaml
controller: 
  podDisruptionBudget:
    minAvailable: 50%
```

## Controller probes

You can customize the readiness and startup probes for the kgateway controller container by using the `controller.readinessProbe` and `controller.startupProbe` Helm values. Your settings are deep-merged with the default probe configuration, so you only need to specify the fields you want to change.

By default, both probes use an `httpGet` handler that checks the `/readyz` endpoint on the health port. The default readiness probe polls every 10 seconds with an initial delay of 1 second. The default startup probe polls every second with no initial delay and a failure threshold of 600, allowing up to 10 minutes for the controller to start.

If you provide an `exec`, `grpc`, or `tcpSocket` handler, the default `httpGet` handler is replaced entirely. Otherwise, the `httpGet` handler is kept and your overrides are merged on top.

The following example adjusts the timing fields of the default readiness probe without changing the default `httpGet` handler.

```yaml
controller:
  readinessProbe:
    initialDelaySeconds: 5
    periodSeconds: 20
    failureThreshold: 3
```

The following example replaces the default `httpGet` handler with a custom `exec` handler on the startup probe.

```yaml
controller:
  startupProbe:
    exec:
      command: ["cat", "/tmp/ready"]
    initialDelaySeconds: 10
    periodSeconds: 5
    failureThreshold: 60
```

## xDS first-connect grace period

By default, the control plane waits 1 second after a new proxy connects before sending its first xDS snapshot. This gives per-client translation time to converge and prevents newly started gateway pods from receiving incomplete configuration after a controller restart.

You can adjust the grace period by using the `KGW_XDS_FIRST_CONNECT_DELAY` environment variable on the controller. The value is a Go duration string, for example `2s`. Set it to `0` to disable the grace period entirely.

```yaml
controller:
  extraEnv:
    KGW_XDS_FIRST_CONNECT_DELAY: "2s"
```


## Controller admin server bind address

The kgateway controller runs an admin and debug server on port 9095. By default, the server binds to `localhost` and is only accessible from within the pod.

To access the admin and debug servers from your local machine, use the `kubectl port-forward` command to expose port 9095 on your local machine. No change of the bind address is required.

```sh
kubectl port-forward deployment/{{< reuse "kgw-docs/snippets/pod-name.md" >}} -n {{< reuse "kgw-docs/snippets/namespace.md" >}} 9095:9095
```

If you need other pods in the cluster to reach the admin server directly, you can change the bind address by using the `controller.admin.bindAddress` Helm value or the `KGW_ADMIN_BIND_ADDRESS` environment variable. Setting `bindAddress` to `0.0.0.0` makes the server listen on all pod interfaces, so other pods can reach it at `http://<pod-ip>:9095`. To find the pod IP, run `kubectl get pod -l app.kubernetes.io/name={{< reuse "kgw-docs/snippets/pod-name.md" >}} -n {{< reuse "kgw-docs/snippets/namespace.md" >}} -o wide`.

> [!WARNING]
> The admin server exposes pprof profiling endpoints, logging controls, and internal config snapshots. Only expose it outside the pod in trusted environments, such as a local development cluster or a dedicated profiling setup.

```yaml
controller:
  admin:
    bindAddress: 0.0.0.0
```


