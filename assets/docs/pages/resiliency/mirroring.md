Copy live production traffic to a shadow environment or service so that you can try out, analyze, and monitor new software changes before deploying them to production.

## About traffic mirroring

When releasing changes to a service, you want to finely control how those changes get exposed to users. This [progressive delivery](https://redmonk.com/jgovernor/2018/08/06/towards-progressive-delivery/) approach to releasing software allows you to reduce the blast radius, especially when changes introduce unintended behaviors. Traffic mirroring, also referred to as traffic shadowing, is one way to observe the impact of new software releases and test out new changes before you roll them out to production. Other approaches to slowly introduce new software include canary releases, A/B testing, or blue-green deployments. 

When you turn on traffic shadowing for an app, kgateway makes a copy of all incoming requests. Kgateway still proxies the request to the backing destination along the request path. It also sends a copy of the request asynchronously to another shadow destination. When a response or failure happens, copies are not generated. This way, you can test how traffic is handled by a new release or version of your app with zero production impact. You can also compare the shadowed results against the expected results. You can use this information to decide how to proceed with a canary release.

<!--
When a copy of the request is sent to the shadow app, kgateway adds a `-shadow` postfix to the `Host` or `Authority` header. For example, if traffic is sent to `foo.bar.com`, the `Host` header value is set to `foo.bar.com-shadow`. This way, the app that receives the shadowed traffic can determine if the traffic is shadowed or not. This information might be valuable for stateful services, such as to roll back any stateful transactions that are associated with processing the request. To learn more about advanced traffic shadowing patterns, see [this blog](https://blog.christianposta.com/microservices/advanced-traffic-shadowing-patterns-for-microservices-with-istio-service-mesh/). -->

To observe and analyze shadowed traffic, you can use a tool like [Open Diffy](https://github.com/opendiffy/diffy). This tool create diff-compares on the responses. You can use this data to verify that the response is correct and to detect API forward/backward compatibility problems. 

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up mirroring

1. Edit the httpbin service that you deployed earlier to add the `version: v1` selector label. This label ensures that traffic to the v1 version is always routed to this instances of the httpbin app. 
   ```sh
   kubectl patch service httpbin -n httpbin --type='json' -p='[{"op": "add", "path": "/spec/selector/version", "value": "v1"}]'
   ```
  
2. Deploy another version (`v2`) of httpbin. You use this app to receive the mirrored traffic from httpbin `v1`. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: v1
   kind: Service
   metadata:
     name: httpbin2
     namespace: httpbin
     labels:
       app: httpbin
       service: httpbin
   spec:
     ports:
       - name: http
         port: 8000
         targetPort: 8080
       - name: tcp
         port: 9000
     selector:
       app: httpbin
       version: v2
   ---
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: httpbin2
     namespace: httpbin
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: httpbin
         version: v2
     template:
       metadata:
         labels:
           app: httpbin
           version: v2
       spec:
         serviceAccountName: httpbin
         containers:
           - image: docker.io/mccutchen/go-httpbin:v2.6.0
             imagePullPolicy: IfNotPresent
             name: httpbin
             command: [ go-httpbin ]
             args:
               - "-port"
               - "8080"
               - "-max-duration"
               - "600s" # override default 10s
             ports:
               - containerPort: 8080
           # Include curl container for e2e testing, allows sending traffic mediated by the proxy sidecar
           - name: curl
             image: curlimages/curl:7.83.1
             resources:
               requests:
                 cpu: "100m"
               limits:
                 cpu: "200m"
             imagePullPolicy: IfNotPresent
             command:
               - "tail"
               - "-f"
               - "/dev/null"
           - name: hey
             image: gcr.io/solo-public/docs/hey:0.1.4
             imagePullPolicy: IfNotPresent
   EOF
   ```
3. Verify that the httpbin2 pod is up and running. 
   ```sh
   kubectl get pods -n httpbin
   ```
   
4. Create an HTTPRoute for the httpbin app that mirrors requests along the `mirror.example` domain from the httpbin app to the httpbin2 app. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-mirror
     namespace: httpbin
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
     - mirror.example
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /
       filters:
       - type: RequestMirror
         requestMirror:
           backendRef:
             kind: Service
             name: httpbin2
             port: 8000
       backendRefs:
       - name: httpbin
         port: 8000
   EOF
   ```

5. Send a few requests to the httpbin app on the `mirror.example` domain. Verify that you get back a 200 HTTP response code. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing"  tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer"  %}}
   ```sh
   for i in {1..5}; do curl -vi http://$INGRESS_GW_ADDRESS:8080/headers \
   -H "host: mirror.example:8080"; done
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   for i in {1..5}; do curl -vi localhost:8080/headers \
   -H "host: mirror.example"; done
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
6. Get the logs of the httpbin app and verify that you see the requests that you sent. 
   ```sh
   kubectl logs -l version=v1 -n httpbin
   ```
   
   Example output: 
   ```
   time="2025-03-14T19:43:01.1546" status=200 method="GET" uri="/headers" size_bytes=508 duration_ms=0.05 user_agent="curl/8.7.1" client_ip=10.0.8.23
   time="2025-03-14T19:43:02.3565" status=200 method="GET" uri="/headers" size_bytes=443 duration_ms=0.06 user_agent="curl/8.7.1" client_ip=10.0.8.23
   time="2025-03-14T19:43:03.0178" status=200 method="GET" uri="/headers" size_bytes=508 duration_ms=0.08 user_agent="curl/8.7.1" client_ip=10.0.6.27
   time="2025-03-14T19:43:03.3874" status=200 method="GET" uri="/headers" size_bytes=508 duration_ms=0.06 user_agent="curl/8.7.1" client_ip=10.0.8.23
   time="2025-03-14T19:43:03.6862" status=200 method="GET" uri="/headers" size_bytes=443 duration_ms=0.07 user_agent="curl/8.7.1" client_ip=10.0.6.27
   ```

7. Get the logs of the httpbin2 app and verify that you see the same requests. 
   ```sh
   kubectl logs -l version=v2 -n httpbin
   ```
   
   Example output: 
   ```
   time="2025-03-14T19:43:01.1548" status=200 method="GET" uri="/headers" size_bytes=443 duration_ms=0.17 user_agent="curl/8.7.1" client_ip=10.0.8.23
   time="2025-03-14T19:43:02.3565" status=200 method="GET" uri="/headers" size_bytes=508 duration_ms=0.06 user_agent="curl/8.7.1" client_ip=10.0.8.23
   time="2025-03-14T19:43:03.0173" status=200 method="GET" uri="/headers" size_bytes=443 duration_ms=0.15 user_agent="curl/8.7.1" client_ip=10.0.6.27
   time="2025-03-14T19:43:03.3869" status=200 method="GET" uri="/headers" size_bytes=443 duration_ms=0.16 user_agent="curl/8.7.1" client_ip=10.0.8.23
   time="2025-03-14T19:43:03.6858" status=200 method="GET" uri="/headers" size_bytes=508 duration_ms=0.05 user_agent="curl/8.7.1" client_ip=10.0.6.27
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete service httpbin2 -n httpbin
kubectl delete deployment httpbin2 -n httpbin
kubectl delete httproute httpbin-mirror -n httpbin
```


