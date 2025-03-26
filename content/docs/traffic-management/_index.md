---
linkTitle: "Traffic management"
title: Control traffic and route requests
weight: 400
---

{{< cards >}}
  {{< card link="destination-types" title="Destination types" >}}
  {{< card link="direct-response" title="Direct response" >}}
  {{< card link="match" title="Request matching" >}}
  {{< card link="redirect" title="Redirects" >}}
  {{< card link="rewrite" title="Rewrites" >}}
  {{< card link="route-delegation" title="Route delegation" >}}
  {{< card link="buffering" title="Buffering" >}}
  {{< card link="header-control" title="Header control" >}}
  {{< card link="transformations" title="Transformations" >}}
  {{< card link="traffic-split" title="Traffic splitting" >}}
{{< /cards >}}

kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: RoutePolicy
metadata:
  name: transformation
  namespace: httpbin
spec:
  targetRef: 
    group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: parent
  transformation:
    response:
      set:
      - name: x-solo-response
        value: '{{ request_header("x-solo-request") }}' 
EOF
