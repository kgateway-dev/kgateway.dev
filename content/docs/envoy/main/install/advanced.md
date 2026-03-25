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



