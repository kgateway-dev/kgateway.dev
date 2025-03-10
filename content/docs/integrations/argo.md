---
title: Argo Rollouts
weight: 510
description: Use kgateway with Argo Rollouts. 
---

[Argo Rollouts](https://argoproj.github.io/rollouts/) is a Kubernetes controller that provides advanced deployment capabilities such as blue-green, canary, canary analysis, experimentation, and progressive delivery features to Kubernetes. Because Argo Rollouts supports the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}}, you can use Argo Rollouts to control how traffic is split and forwarded from the proxies that {{< reuse "docs/snippets/product-name.md" >}} v2 manages to the apps in your cluster. 

## Before you begin 

{{< reuse "docs/snippets/prereq.md" >}}

## Install Argo Rollouts

1. Create the `argo-rollouts` namespace and deploy the Argo Rollouts components into it. 
   ```sh
   kubectl create namespace argo-rollouts
   kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml
   ```

2. Change the config map for the Argo Rollouts pod to install the Argo Rollout Gateway API plug-in. 
   ```yaml
   cat <<EOF | kubectl apply -f -
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: argo-rollouts-config 
     namespace: argo-rollouts
   data:
     trafficRouterPlugins: |-
       - name: "argoproj-labs/gatewayAPI"
         location: "https://github.com/argoproj-labs/rollouts-plugin-trafficrouter-gatewayapi/releases/download/v0.0.0-rc1/gateway-api-plugin-linux-amd64"
   EOF
   ```

3. Restart the Argo Rollouts pod to pick up the latest configuration changes. 
   ```sh
   kubectl rollout restart deployment -n argo-rollouts argo-rollouts
   ```

## Create RBAC rules for Argo

1. Create a cluster role to allow the Argo Rollouts pod to manage HTTPRoute resources. 
   {{< callout type="warning" >}}
   The following cluster role allows the Argo Rollouts pod to access and work with any resources in the cluster. Use this configuration with caution and only in test environments. 
   {{< /callout >}} 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: rbac.authorization.k8s.io/v1
   kind: ClusterRole
   metadata:
     name: gateway-controller-role
     namespace: argo-rollouts
   rules:
     - apiGroups:
         - "*"
       resources:
         - "*"
       verbs:
         - "*"
   EOF
   ```

2. Create a cluster role binding to give the Argo Rollouts service account the permissions from the cluster role. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: rbac.authorization.k8s.io/v1
   kind: ClusterRoleBinding
   metadata:
     name: gateway-admin
   roleRef:
     apiGroup: rbac.authorization.k8s.io
     kind: ClusterRole
     name: gateway-controller-role
   subjects:
     - namespace: argo-rollouts
       kind: ServiceAccount
       name: argo-rollouts
   EOF
   ```

## Set up a rollout

1. Create a stable and canary service for the `rollouts-demo` pod that you deploy in the next step.  
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: v1
   kind: Service
   metadata:
     name: argo-rollouts-stable-service
     namespace: default
   spec:
     ports:
       - port: 80
         targetPort: http
         protocol: TCP
         name: http
     selector:
       app: rollouts-demo
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: argo-rollouts-canary-service
     namespace: default
   spec:
     ports:
       - port: 80
         targetPort: http
         protocol: TCP
         name: http
     selector:
       app: rollouts-demo
   EOF
   ```

2. Create an Argo Rollout that deploys the `rollouts-demo` pod. Add your stable and canary services to the `spec.strategy.canary` section. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: argoproj.io/v1alpha1
   kind: Rollout
   metadata:
     name: rollouts-demo
     namespace: default
   spec:
     replicas: 3
     strategy:
       canary:
         canaryService: argo-rollouts-canary-service # our created canary service
         stableService: argo-rollouts-stable-service # our created stable service
         trafficRouting:
           plugins:
             argoproj-labs/gatewayAPI:
               httpRoute: argo-rollouts-http-route 
               namespace: default
         steps:
         - setWeight: 30
         - pause: { duration: 30s }
         - setWeight: 60
         - pause: { duration: 30s }
         - setWeight: 100
         - pause: { duration: 30s }
     revisionHistoryLimit: 2
     selector:
       matchLabels:
         app: rollouts-demo
     template:
       metadata:
         labels:
           app: rollouts-demo
       spec:
         containers:
           - name: rollouts-demo
             image: kostiscodefresh/summer-of-k8s-app:v1
             ports:
               - name: http
                 containerPort: 8080
                 protocol: TCP
             resources:
               requests:
                 memory: 32Mi
                 cpu: 5m
   EOF
   ```

2. Create an HTTPRoute resource to expose the `rollouts-demo` pod on the HTTP gateway that you created as part of the [Get started guide](/docs/quickstart). The HTTP resource can serve both the stable and canary versions of your app. 
   ```yaml
   kubectl apply -f- <<EOF
   kind: HTTPRoute
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: argo-rollouts-http-route
     namespace: default
   spec:
     parentRefs:
       - name: http
         namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     hostnames:
     - "demo.example.com"
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /  
       backendRefs:
       - name: argo-rollouts-stable-service
         kind: Service
         port: 80
       - name: argo-rollouts-canary-service
         kind: Service
         port: 80
   EOF
   ```

3. Send a request to the `rollouts-demo` app and verify your CLI output.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab  %}}
   1. Get the external address of the gateway and save it in an environment variable.
      ```sh
      export INGRESS_GW_ADDRESS=$(kubectl get svc -n {{< reuse "docs/snippets/ns-system.md" >}} http -o jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
      echo $INGRESS_GW_ADDRESS
      ```
   
   2. Send a request to the `rollouts-demo` app and verify that you see the `ver: 1.0` response from the stable service. 
      ```sh
      curl http://$INGRESS_GW_ADDRESS:8080/callme -H "host: demo.example.com:8080"
      ```

      Example output: 
      ```console
      <div class='pod' style='background:#44B3C2'> ver: 1.0
      </div>%
      ```
   {{% /tab %}}
   {{% tab  %}}
   3. Port-forward the `http` pod on port 8080. 
      ```sh
      kubectl port-forward deployment/http -n {{< reuse "docs/snippets/ns-system.md" >}} 8080:8080
      ```
   
   4. Send a request to the `rollouts-demo` app and verify that you see the `ver: 1.0` response from the stable service.
      ```sh
      curl -vik localhost:8080/callme -H "host: demo.example.com"
      ```

      Example output: 
      ```console
      <div class='pod' style='background:#44B3C2'> ver: 1.0
      </div>%
      ```

   {{% /tab %}}
   {{< /tabs >}}

4. Change the manifest to use the `v2` tag to start a rollout of your app. Argo Rollouts automatically starts splitting traffic between version 1 and version 2 of the app for the duration of the rollout.
   ```sh
   kubectl patch rollout rollouts-demo -n default \
     --type='json' -p='[{"op": "replace", "path": "/spec/template/spec/containers/0/image", "value":"kostiscodefresh/summer-of-k8s-app:v2"}]'
   ```

5. Send another request to your app. Because traffic is split between version 1 and version 2 of the app, you see responses from both app versions until the rollout is completed.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab  %}}
   ```bash
   while true; do curl -H "host: demo.example.com" $INGRESS_GW_ADDRESS:8080/callme; done     
   ```

   Example output: 
   ```console
   <div class='pod' style='background:#F1A94E'> ver: 2.0
   </div><div class='pod' style='background:#F1A94E'> ver: 2.0
   </div><div class='pod' style='background:#44B3C2'> ver: 1.0
   </div><div class='pod' style='background:#44B3C2'> ver: 1.0
   </div><div class='pod' style='background:#F1A94E'> ver: 2.0
   </div><div class='pod' style='background:#44B3C2'> ver: 1.0
   </div><div class='pod' style='background:#F1A94E'> ver: 2.0
   </div><div class='pod' style='background:#F1A94E'> ver: 2.0
   </div><div class='pod' style='background:#44B3C2'> ver: 1.0
   </div><div class='pod' style='background:#F1A94E'> ver: 2.0
   </div><div class='pod' style='background:#F1A94E'> ver: 2.0
   </div><div class='pod' style='background:#44B3C2'> ver: 1.0
   </div><div class='pod' style='background:#F1A94E'> ver: 2.0
   </div><div class='pod' style='background:#F1A94E'> ver: 2.0
   </div><div class='pod' style='background:#F1A94E'> ver: 2.0
   ```
   {{% /tab %}}
   {{% tab  %}}
   ```sh
   while true; do curl localhost:8080/callme -H "host: demo.example.com"; done
   ```
   Example output: 
   ```console
   <div class='pod' style='background:#F1A94E'> ver: 2.0
   </div><div class='pod' style='background:#F1A94E'> ver: 2.0
   </div><div class='pod' style='background:#44B3C2'> ver: 1.0
   </div><div class='pod' style='background:#44B3C2'> ver: 1.0
   </div><div class='pod' style='background:#F1A94E'> ver: 2.0
   </div><div class='pod' style='background:#44B3C2'> ver: 1.0
   </div><div class='pod' style='background:#F1A94E'> ver: 2.0
   </div><div class='pod' style='background:#F1A94E'> ver: 2.0
   </div><div class='pod' style='background:#44B3C2'> ver: 1.0
   </div><div class='pod' style='background:#F1A94E'> ver: 2.0
   </div><div class='pod' style='background:#F1A94E'> ver: 2.0
   </div><div class='pod' style='background:#44B3C2'> ver: 1.0
   </div><div class='pod' style='background:#F1A94E'> ver: 2.0
   </div><div class='pod' style='background:#F1A94E'> ver: 2.0
   </div><div class='pod' style='background:#F1A94E'> ver: 2.0
   ```
   {{% /tab %}}
   {{< /tabs >}}

Congratulations, you successfully rolled out a new version of your app without downtime by using the HTTP gateway that is managed by {{< reuse "docs/snippets/product-name.md" >}} v2. After a rollout, you typically perform tasks such as the following: 

- **Testing**: Conduct thorough testing of your app to ensure that it functions correctly after the rollout.
- **Monitoring**: Monitor your application to detect any issues that may arise after the rollout. 
- **Documentation**: Update documentation or runbooks to reflect any changes in your application.
- **User Validation**: Have users validate that the app functions correctly and meets their requirements.
- **Performance Testing**: Depending on your app, consider conducting performance testing to ensure that your app can handle the expected load without issues.
- **Resource Cleanup**: If the rollout included changes to infrastructure or other resources, ensure that any temporary or unused resources are cleaned up to avoid incurring unnecessary costs.
- **Communication**: Communicate with your team and stakeholders to update them on the status of the rollout and any issues that were encountered and resolved.
- **Security Audit**: If your application has undergone significant changes, consider conducting a security audit to ensure that no security vulnerabilities have been introduced.

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

1. Remove the HTTP route. 
   ```sh
   kubectl delete httproute argo-rollouts-http-route
   ```

2. Remove the Argo Rollout.
   ```sh
   kubectl delete rollout rollouts-demo
   ```

3. Remove the stable and canary services. 
   ```sh
   kubectl delete services argo-rollouts-canary-service argo-rollouts-stable-service
   ```

4. Remove the cluster role for the Argo Rollouts pod. 
   ```sh
   kubectl delete clusterrole gateway-controller-role -n argo-rollouts
   ```

5. Remove the cluster role binding. 
   ```sh
   kubectl delete clusterrolebinding gateway-admin 
   ```

6. Remove Argo Rollouts. 
   ```sh
   kubectl delete -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml
   kubectl delete namespace argo-rollouts
   ```


