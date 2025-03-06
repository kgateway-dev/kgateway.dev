---
title: Static
weight: 10
---

Route requests to services that listen for incoming traffic on a fixed IP address and port or hostname and port combination by using static Backends.

You simply add the list of static hosts or DNS names to your Backend resource and then reference the Backend in your HTTPRoute resource. Unlike Backends that are dynamically created by using the discovery feature in {{< reuse "docs/snippets/product-name.md" >}}, static Backend resources must be created manually by the user.  

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up a static Backend

1. Create a static Backend resource that routes requests to the [JSON testing API](http://jsonplaceholder.typicode.com/).
   ```yaml
   kubectl apply -f- <<EOF 
   apiVersion: gloo.solo.io/v1
   kind: Backend
   metadata:
     name: json-backend
   spec:
     static:
       hosts:
         - addr: jsonplaceholder.typicode.com
           port: 80
   EOF
   ```

2. Create a RouteOption resource that rewrites the hostname to the `jsonplaceholder.typicode.com`. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: RouteOption
   metadata:
     name: rewrite
     namespace: default
   spec:
     options:
       hostRewrite: 'jsonplaceholder.typicode.com'
   EOF
   ```
   
3. Create an HTTPRoute resource that routes traffic on the `static.example` domain to your Backend resource. To ensure that your request can be forwarded to the JSON testing API, you must also reference the RouteOption resource that rewrites hostnames to `jsonplaceholder.typicode.com`.
   
   {{< callout type="warning" >}}
   Do not specify a port in the `spec.backendRefs.port` field when referencing your Backend. The port is defined in your Backend resource and ignored if set on the HTTPRoute resource.
   {{< /callout >}}
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: static-backend
     namespace: default
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     hostnames:
       - static.example
     rules:
       - backendRefs:
         - name: json-backend
           kind: Backend
           group: gloo.solo.io
         filters:
         - type: ExtensionRef
           extensionRef:
             group: gateway.solo.io
             kind: RouteOption
             name: rewrite
   EOF
   ```

4. Send a request to your Backend and verify that you get back a 200 HTTP response code and a list of posts. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/posts -H "host: static.example:8080" 
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -vik localhost:8080/posts -H "host: static.example:8080" 
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```
    < 
    [
      {  
        "userId": 1,
        "id": 1,
        "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
        "body": "quia et suscipit\nsuscipit recusandae consequuntur expedita et cum\nreprehenderit molestiae ut ut quas totam\nnostrum rerum est autem sunt rem eveniet architecto"
      },
      {
        "userId": 1,
        "id": 2,
        "title": "qui est esse",
        "body": "est rerum tempore vitae\nsequi sint nihil reprehenderit dolor beatae ea dolores neque\nfugiat blanditiis voluptate porro vel nihil molestiae ut reiciendis\nqui aperiam non debitis possimus qui neque nisi nulla"
      },
      {
        "userId": 1,
        "id": 3,
        "title": "ea molestias quasi exercitationem repellat qui ipsa sit aut",
        "body": "et iusto sed quo iure\nvoluptatem occaecati omnis eligendi aut ad\nvoluptatem doloribus vel accusantium quis pariatur\nmolestiae porro eius odio et labore et velit aut"
      },
      {
        "userId": 1,
        "id": 4,
        "title": "eum et est occaecati",
        "body": "ullam et saepe reiciendis voluptatem adipisci\nsit amet autem assumenda provident rerum culpa\nquis hic commodi nesciunt rem tenetur doloremque ipsam iure\nquis sunt voluptatem rerum illo velit"
      },
   ...
   ```
   
## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete httproute static-backend
kubectl delete routeoption rewrite
kubectl delete backend json-backend
```
