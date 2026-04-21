---
title: Advanced settings
weight: 70
description: Install kgateway and related components.
---

{{< reuse "docs/pages/install/advanced.md" >}}

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

You can configure Horizontal Pod Autoscaler or Vertical Pod Autoscaler policies for the {{< reuse "agw-docs/snippets/kgateway.md" >}} control plane. To set up these policies, you use the `horizontalPodAutoscaler` or `verticalPodAutoscaler` fields in the Helm chart.

{{< callout type="info" >}}
Note that {{< reuse "agw-docs/snippets/kgateway.md" >}} uses leader election if multiple replicas are present. The elected leader's workload is typically larger than the workload of non-leader replicas and therefore drives the overall infrastructure cost. Because of that, Vertical Pod Autoscaling can be a reasonable solution to ensure that the elected leader has the resources it needs to perform its work successfully. In cases where the leader has a large workload, Horizontal Pod Autoscaling might not be as effective as it adds more replicas that do not reduce the workload of the elected leader. 
{{< /callout >}}

{{< callout type="warning" >}}
If you plan to set up both VPA and HPA policies, make sure to closely monitor performance and cost during scale up events. Using both policies can lead to conflict or even destructive loops that impact the performance of your control plane. 
{{< /callout >}}


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


**Note**: To monitor the memory and CPU threshold, you need to deploy the Kubernetes `metrics-server` in your cluster. The `metrics-server` retrieves metrics, such as CPU and memory consumption for your workloads. 

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




