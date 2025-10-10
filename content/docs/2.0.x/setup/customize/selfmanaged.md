---
title: Self-managed gateways (BYO)
weight: 30
prev: /docs/setup/customize/aws-elb
---

Follow the [Get started guide](/docs/quickstart/) to install kgateway. You do not need to create a Gateway resource, because you create a self-managed Gateway as part of this guide. 

## Create a self-managed gateway proxy

1. Create a GatewayParameters resource that allows you to create self-managed gateway proxies. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: GatewayParameters
   metadata:
     name: self-managed
     namespace: kgateway-system
   spec:
     selfManaged: {}
   EOF
   ```

2. Create a Gateway that references the GatewayParameters resource that you created. 
   ```yaml
   kubectl apply -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: self-managed
     namespace: kgateway-system
   spec:
     gatewayClassName: kgateway
     infrastructure:
       parametersRef:
         name: self-managed
         group: gateway.kgateway.dev
         kind: GatewayParameters        
     listeners:
     - protocol: HTTP
       port: 80
       name: http
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

3. Verify that the Gateway is created.  
   ```sh
   kubectl get gateway self-managed -n kgateway-system -o yaml
   ```

4. Verify that no gateway proxy deployment and service were created for your Gateway. The output is blank.
   ```sh
   kubectl get pods -n kgateway-system | grep self-managed
   kubectl get services -n kgateway-system | grep self-managed
   ```
   
5. Create your own gateway proxy deployment. Note that this deployment needs to have valid Envoy configuration that includes the correct name and namespace of your Gateway resource to successfully bootstrap your gateway proxy and bind it to the Gateway resource. You can use the following template as a starting point to build your own Envoy configuration. To bind your gateway proxy with the Gateway resource, ensure that you replace `$GATEWAY_NAME` and `$GATEWAY_NAMESPACE` with the name of the Gateway that you created earlier. 
   
   Example deployment template in the [GitHub `proxy-deployment.yaml` file](https://github.com/kgateway-dev/kgateway/blob/{{< reuse "docs/versions/github-branch.md" >}}/internal/kgateway/helm/kgateway/templates/gateway/proxy-deployment.yaml).
   
   Example configuration to update in the ConfigMap `data.envoy.yaml` section:

   ```yaml
   admin:
     address:
       socket_address: { address: 127.0.0.1, port_value: 19000 }
   node:
     cluster: $GATEWAY_NAME.$GATEWAY_NAMESPACE
     metadata:
       role: gloo-kube-gateway-api~$GATEWAY_NAMESPACE~$GATEWAY_NAMESPACE-$GATEWAY_NAME
   static_resources:
     listeners:
     - name: read_config_listener
       address:
         socket_address: { address: 0.0.0.0, port_value: 8082 }
       filter_chains:
         - filters:
           - name: envoy.filters.network.http_connection_manager
             typed_config:
               "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
               stat_prefix: ingress_http
               codec_type: AUTO
               route_config:
                 name: main_route
                 virtual_hosts:
                   - name: local_service
                     domains: ["*"]
                     routes:
                       - match:
                           path: "/ready"
                           headers:
                             - name: ":method"
                               string_match:
                                 exact: GET
                         route:
                           cluster: admin_port_cluster
               http_filters:
                 - name: envoy.filters.http.router
                   typed_config:
                     "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router
     clusters:
       - name: xds_cluster
         alt_stat_name: xds_cluster
         connect_timeout: 5.000s
         load_assignment:
           cluster_name: xds_cluster
           endpoints:
           - lb_endpoints:
             - endpoint:
                 address:
                   socket_address:
                     address: $CONTROLLER_HOST
                     port_value: 9977
         typed_extension_protocol_options:
           envoy.extensions.backends.http.v3.HttpProtocolOptions:
             "@type": type.googleapis.com/envoy.extensions.backends.http.v3.HttpProtocolOptions
             explicit_http_config:
               http2_protocol_options: {}
         backend_connection_options:
           tcp_keepalive:
             keepalive_time: 10
         type: STRICT_DNS
         respect_dns_ttl: true
       - name: admin_port_cluster
         connect_timeout: 5.000s
         type: STATIC
         lb_policy: ROUND_ROBIN
         load_assignment:
           cluster_name: admin_port_cluster
           endpoints:
           - lb_endpoints:
             - endpoint:
                 address:
                   socket_address:
                     address: 127.0.0.1
                     port_value: 19000
   dynamic_resources:
     ads_config:
       transport_api_version: V3
       api_type: GRPC
       rate_limit_settings: {}
       grpc_services:
       - envoy_grpc:
           cluster_name: xds_cluster
     cds_config:
       resource_api_version: V3
       ads: {}
     lds_config:
       resource_api_version: V3
       ads: {}
   ```
   
## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete gatewayparameters self-managed -n kgateway-system
kubectl delete gateway self-managed -n kgateway-system
```