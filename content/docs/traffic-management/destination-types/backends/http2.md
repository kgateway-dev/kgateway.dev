---
title: HTTP/2
weight: 40
---

You might have services in your Kubernetes cluster that use HTTP/2 for communication. Typically these are gRPC services, but it could apply to any service that uses HTTP/2 in its transport layer. To enable HTTP/2 communication, the `spec.useHttp2` value for the Backend must be set to `true`. This setting instructs {{< reuse "docs/snippets/product-name.md" >}} to use HTTP/2 for communication with the destination. 

Explore your options for how to add the `spec.useHttp2` value to your Backend resource.

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Enable on the Backend {#enable-on-backend}

You can add the `spec.useHttp2` setting to an Backend directly. 

1. Edit the Backend that was created for the httpbin app. 
   ```sh
   kubectl edit backend httpbin-httpbin-8000 -n {{< reuse "docs/snippets/ns-system.md" >}}
   ```
   
2. Add the `spec.useHttp2` setting as shown in the following example. 

   ```yaml {linenos=table,hl_lines=[27],linenostart=1,filename="http2-backend.yaml"}
   apiVersion: gloo.solo.io/v1
   kind: Backend
   metadata:
     annotations:
       gloo.solo.io/h2_service: "true"
       kubectl.kubernetes.io/last-applied-configuration: |
         {"apiVersion":"v1","kind":"Service","metadata":{"annotations":{},"labels":{"app":"httpbin","service":"httpbin"},"name":"httpbin","namespace":"httpbin"},"spec":{"ports":[{"name":"http","port":8000,"targetPort":8080},{"name":"tcp","port":9000}],"selector":{"app":"httpbin"}}}
     creationTimestamp: "2024-04-26T20:34:49Z"
     generation: 4
     labels:
       discovered_by: kubernetesplugin
     name: httpbin-httpbin-8000
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     resourceVersion: "4421071"
     uid: a73b1b82-2910-497a-9f82-ff513ebe911d
   spec:
     discoveryMetadata:
       labels:
         app: httpbin
         service: httpbin
     kube:
       selector:
         app: httpbin
       serviceName: httpbin
       serviceNamespace: httpbin
       servicePort: 8000
     useHttp2: true
   ```

3. Optional: Remove the `useHttp2` setting from your Backend by editing the Backend and removing the setting. 
   ```sh
   kubectl edit backend httpbin-httpbin-8000 -n {{< reuse "docs/snippets/ns-system.md" >}}
   ```
   

## Enable with service annotations {#enable-service-annotations}

One of the ways to enable HTTP/2, is to add the `gloo.solo.io/h2_service` annotation to the Kubernetes service and set it to `true`. If the annotation is present, {{< reuse "docs/snippets/product-name.md" >}} automatically updates the Backend and adds the `useHttp2` value.

{{% callout type="info" %}}
To use service annotations to enable HTTP/2 for a destination, you must [enable service discovery in {{< reuse "docs/snippets/product-name.md" >}}](/docs/traffic-management/destination-types/backends/#discovered-backends).
{{% /callout %}}

1. Review the httpbin Backend resource that was automatically created for the httpbin app that you deployed as part of the [Get started](/docs/quickstart/) guide. Note that the `spec.useHttp2` option is not set. 
   ```sh
   kubectl get backend httpbin-httpbin-8000 -n {{< reuse "docs/snippets/ns-system.md" >}} -o yaml
   ```

2. Add the `gloo.solo.io/h2_service=true` annotation to the httpbin service. 
   ```sh
   kubectl annotate service httpbin gloo.solo.io/h2_service=true -n httpbin
   ```

3. Review the httpbin Backend again and verify that you now see the `useHttp2: true` setting on your Backend. 
   ```sh
   kubectl get backend httpbin-httpbin-8000 -n {{< reuse "docs/snippets/ns-system.md" >}} -o yaml
   ```
   
   Example output: 
   ```yaml {linenos=table,hl_lines=[27],linenostart=1,filename="http2-backend.yaml"}
   apiVersion: gloo.solo.io/v1
   kind: Backend
   metadata:
     annotations:
       gloo.solo.io/h2_service: "true"
       kubectl.kubernetes.io/last-applied-configuration: |
         {"apiVersion":"v1","kind":"Service","metadata":{"annotations":{},"labels":{"app":"httpbin","service":"httpbin"},"name":"httpbin","namespace":"httpbin"},"spec":{"ports":[{"name":"http","port":8000,"targetPort":8080},{"name":"tcp","port":9000}],"selector":{"app":"httpbin"}}}
     creationTimestamp: "2024-04-26T20:34:49Z"
     generation: 4
     labels:
       discovered_by: kubernetesplugin
     name: httpbin-httpbin-8000
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     resourceVersion: "4421071"
     uid: a73b1b82-2910-497a-9f82-ff513ebe911d
   spec:
     discoveryMetadata:
       labels:
         app: httpbin
         service: httpbin
     kube:
       selector:
         app: httpbin
       serviceName: httpbin
       serviceNamespace: httpbin
       servicePort: 8000
     useHttp2: true
   ```

4. Update the annotation on the httpbin service and set it to `false`. 
   ```sh
   kubectl annotate service httpbin gloo.solo.io/h2_service=false -n httpbin --overwrite
   ```

5. Review the Backend resource again and verify that the `useHttp2` setting was updated to `false`.
   ```sh
   kubectl get backend httpbin-httpbin-8000 -n {{< reuse "docs/snippets/ns-system.md" >}} -o yaml 
   ```
   
   Example output: 
   ```yaml {linenos=table,hl_lines=[13],linenostart=1,filename="http2-backend.yaml"}
   ...
   spec:
    discoveryMetadata:
      labels:
        app: httpbin
        service: httpbin
    kube:
      selector:
        app: httpbin
      serviceName: httpbin
      serviceNamespace: httpbin
      servicePort: 8000
    useHttp2: false
   ```

{{% callout type="info" %}}
Once set, you cannot remove the `useHttp2` setting from an Backend entirely by using service annotations. For example, a command, such as `kubectl annotate service httpbin gloo.solo.io/h2_service- -n httpbin` does not remove this setting from the Backend. You can only update the `useHttp2` field and set it to `true` or `false`. To remove this setting from an Backend entirely, you must [edit the Backend and remove that setting](#enable-on-backend). 
{{% /callout %}}
   
{{% callout type="info" %}}
In a race condition where both the annotation and port name are set, the annotation value takes precedence as it is evaluated first. If the annotation is set to `false` and the port name is set to `http2`, the `spec.useHttp2` setting on the Backend evaluates to `false`. To avoid conflicting HTTP/2 settings, it is recommended to use either service annotations or port names. 
{{% /callout %}}
 
## Enable with port names {#enable-port-name}

You can enable HTTP/2 by setting specific port names on the service that exposes the Backend. The name of the port must be one of the following: `grpc`, `http2`, or `h2`. 

{{% callout type="info" %}}
To use port names to enable HTTP/2 for a destination, you must [enable service discovery in {{< reuse "docs/snippets/product-name.md" >}}](/docs/traffic-management/destination-types/backends/#discovered-backends).
{{% /callout %}}

1. Review the httpbin Backend resource that was automatically created for the httpbin app that you deployed as part of the [Get started](/docs/quickstart/) guide. Note that the `spec.useHttp2` option is not set. 
   ```sh
   kubectl get backend httpbin-httpbin-8000 -n {{< reuse "docs/snippets/ns-system.md" >}} -o yaml
   ```

2. Review the ports that are defined on the httpbin service. 
   ```sh
   kubectl get service httpbin -n httpbin -o yaml
   ```
   
   Example output: 
   ```yaml {linenos=table,hl_lines=[11,15],linenostart=1,filename="httpbin-service.yaml"}
   ...
   spec:
     clusterIP: 172.20.148.195
     clusterIPs:
     - 172.20.148.195
     internalTrafficPolicy: Cluster
     ipFamilies:
     - IPv4
     ipFamilyPolicy: SingleStack
     ports:
     - name: http
       port: 8000
       protocol: TCP
       targetPort: 8080
     - name: tcp
       port: 9000
       protocol: TCP
       targetPort: 9000
   ```

3. Edit the service and change the `http` port to `http2`. 
   ```sh
   kubectl edit service httpbin -n httpbin
   ```
   
   Example output: 
   ```yaml {linenos=table,hl_lines=[11],linenostart=1,filename="httpbin-service.yaml"}
   ...
   spec:
     clusterIP: 172.20.148.195
     clusterIPs:
     - 172.20.148.195
     internalTrafficPolicy: Cluster
     ipFamilies:
     - IPv4
     ipFamilyPolicy: SingleStack
     ports:
     - name: http2
       port: 8000
       protocol: TCP
       targetPort: 8080
     - name: tcp
       port: 9000
       protocol: TCP
       targetPort: 9000
   ```

4. Review the Backend for the httpbin app and verify that the `useHttp2` setting was added. 
   ```sh
   kubectl get backend httpbin-httpbin-8000 -n {{< reuse "docs/snippets/ns-system.md" >}} -o yaml
   ```
   
   Example output: 
   ```yaml {linenos=table,hl_lines=[13],linenostart=1,filename="httpbin-backend.yaml"}
   ...
   spec:
    discoveryMetadata:
      labels:
        app: httpbin
        service: httpbin
    kube:
      selector:
        app: httpbin
      serviceName: httpbin
      serviceNamespace: httpbin
      servicePort: 8000
    useHttp2: true
   ```
   
   
{{% callout type="info" %}}
Once set, you cannot remove the `useHttp2` setting from an Backend entirely by using port names. For example, if you change back the port name from `http2` to `http`, the `useHttp2` setting is not removed from the Backend. To remove this setting from an Backend entirely, you must [edit the Backend and remove that setting](#enable-on-backend). 
{{% /callout %}}

{{% callout type="info" %}}
In a race condition where both the annotation and port name are set, the annotation value takes precedence as it is evaluated first. If the annotation is set to `false` and the port name is set to `http2`, the `spec.useHttp2` setting on the Backend evaluates to `false`. To avoid conflicting HTTP/2 settings, it is recommended to use either service annotations or port names. 
{{% /callout %}}
