---
title: Horizontal Pod Autoscaling (HPA)
weight: 40
description:
---

You can bring your own Horizontal Pod Autoscaler (HPA) plug-in to {{< reuse "docs/snippets/kgateway.md" >}}. This way, you can automatically scale gateway proxy pods up and down based on certain thresholds, like memory and CPU consumption. 

To allow integration with HPA plug-ins, do not specify any custom replicas in the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource. This way, your HPA plug-in can scale the proxy based on your autoscaling strategy. 

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up your own HPA plug-in

1. Deploy the Kubernetes `metrics-server` in your cluster. The `metrics-server` retrieves metrics, such as CPU and memory consumption for your workloads. These metrics can be used by the HPA plug-in to determine if the pod must be scaled up or down.
   ```sh
   kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
   kubectl -n kube-system patch deployment metrics-server \
    --type=json \
    -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'
   ```
   
   Example output: 
   ```console
   serviceaccount/metrics-server created
   clusterrole.rbac.authorization.k8s.io/system:aggregated-metrics-reader created
   clusterrole.rbac.authorization.k8s.io/system:metrics-server created
   rolebinding.rbac.authorization.k8s.io/metrics-server-auth-reader created
   clusterrolebinding.rbac.authorization.k8s.io/metrics-server:system:auth-delegator created
   clusterrolebinding.rbac.authorization.k8s.io/system:metrics-server created
   service/metrics-server created
   deployment.apps/metrics-server configured
   apiservice.apiregistration.k8s.io/v1beta1.metrics.k8s.io created
   ```

2. Review the metrics for the http Gateway. 
   ```sh
   kubectl top pod -n {{< reuse "docs/snippets/namespace.md" >}}  | grep http
   ```
   
   Example output: 
   ```
   http-594455765c-5szpq        3m           19Mi  
   ```

6. Create a HorizontalPodAutoscaler resource that scales your gateway proxy up to 10 replicas if the memory consumption exceeds 10Mi. You can adjust this value depending on the memory value that you retrieved in the previous step. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: autoscaling/v2
   kind: HorizontalPodAutoscaler
   metadata:
     name: hpa
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     scaleTargetRef:
       apiVersion: apps/v1
       kind: Deployment
       name: http
     minReplicas: 1
     maxReplicas: 10
     metrics:
       - type: Resource
         resource:
           name: memory
           target:
             type: AverageValue
             averageValue: 10Mi
   EOF
   ```

7. Wait a few minutes for Kubernetes to scale up your gateway proxies. Then, check the number of `http` pods that were created. Because every pod exceeds the memory threshold that you defined in the HPA policy, Kubernetes scales up the pods to the 10 maximum replicas. 
   ```sh
   kubectl top pod -n {{< reuse "docs/snippets/namespace.md" >}}  | grep http
   ```
   
   Example output: 
   ```
   http-594455765c-5szpq                   3m           19Mi            
   http-594455765c-gvf9g                   3m           19Mi            
   http-594455765c-h2zb9                   3m           19Mi            
   http-594455765c-mghsf                   3m           19Mi            
   http-594455765c-n6prj                   3m           19Mi            
   http-594455765c-nvs6c                   3m           19Mi            
   http-594455765c-srfcz                   3m           19Mi            
   http-594455765c-ssvjx                   3m           19Mi            
   http-594455765c-tx2z6                   3m           19Mi            
   http-594455765c-vxjbp                   3m           19Mi 
   ```


## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete hpa hpa -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```
   