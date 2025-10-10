---
title: Idle stream timeouts
weight: 25
description:
---

Customize the default idle stream timeout of 5 minutes (300s). 

## About idle stream timeouts

By default, Envoy closes all idle request and response streams after 5 minutes if no data is sent or received and returns a 408 Request Timeout HTTP response code. Idle stream timeouts are different from request timeouts. Request timeouts configure the time Envoy allows for the entire request stream to be received from the client. An idle stream timeout on the other hand is the time Envoy allows a stream to exist without activity before it is terminated. Idle stream timeouts are recommended to protect against clients that stall or that open the stream and never send any data.

You can change the default idle stream timeout setting with a {{< reuse "docs/snippets/trafficpolicy.md" >}}.  While idle streams are a concept in the HTTP/2 and HTTP/3 protocols, Envoy also maps an HTTP/1 request to a stream. Because of that, you can apply idle stream timeouts to HTTP/1 traffic too. 

{{< callout >}}
{{< reuse "docs/snippets/proxy-kgateway.md" >}}
{{< /callout >}}


## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up idle stream timeouts

1. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} with your idle stream timeout settings. If you have an HTTPRoute with multiple HTTPRoute rules, you can use the `targetRefs.sectionName` to apply the timeout to a specific HTTPRoute rule. In this example, you apply the policy to the httpbin HTTPRoute.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: timeout
     namespace: httpbin
   spec:
     targetRefs:
     - kind: HTTPRoute
       group: gateway.networking.k8s.io
       name: httpbin
     timeouts:
       streamIdle: 600s
   EOF
   ```

2. Verify that the gateway proxy is configured with the idle stream timeout.
   1. Port-forward the gateway proxy on port 19000.

      ```sh
      kubectl port-forward deployment/http -n {{< reuse "docs/snippets/namespace.md" >}} 19000
      ```

   2. Get the configuration of your gateway proxy as a config dump.

      ```sh
      curl -X POST 127.0.0.1:19000/config_dump\?include_eds > gateway-config.json
      ```

   3. Open the config dump and find the route configuration for the `kube_httpbin_httpbin_8000` Envoy cluster on the `listener~8080~www_example_com` virtual host. Verify that the timeout policy is set as you configured it.
      
      Example `jq` command:
      ```sh
      jq '.configs[] | select(."@type" == "type.googleapis.com/envoy.admin.v3.RoutesConfigDump") | .dynamic_route_configs[].route_config.virtual_hosts[] | select(.routes[].route.cluster == "kube_httpbin_httpbin_8000")' gateway-config.json
      ```
      
      Example output:
      ```console{hl_lines=[9]}
      "routes": [
        {
        "match": {
            "prefix": "/"
        },
        "route": {
            "cluster": "kube_httpbin_httpbin_8000",
            "cluster_not_found_response_code": "INTERNAL_SERVER_ERROR",
            "idle_timeout": "600s"
        },
        "metadata": {
            "filter_metadata": {
            "merge.TrafficPolicy.gateway.kgateway.dev": {
                "timeouts": [
                "gateway.kgateway.dev/TrafficPolicy/httpbin/timeout"
                ]
            }
            }
        },
        "name": "listener~8080~www_example_com-route-0-httproute-httpbin-httpbin-0-0-matcher-0"
        }
      ],
      ```

   
## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}
   
```sh
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} timeout -n httpbin
```