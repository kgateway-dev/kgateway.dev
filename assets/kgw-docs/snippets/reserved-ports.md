The following ports are reserved by {{< reuse "kgw-docs/snippets/kgateway-capital.md" >}} and cannot be used when configuring your gateway proxy.  

| Port | Description | 
| -- | -- | 
| 19000 | The Envoy admin port. Gateway proxies expose an admin interface on this port that you can use to access important proxy information, such as the config dump, heap dump, healthchecks, and memory allocation.   |
| 8082 | The readiness port. This port can be used to determine if the gateway proxy is ready to receive traffic. | 
| 9091 | The Prometheus scraping port. Gateway proxies expose all metrics on this port so that Prometheus can scrape them. | 

{{< version exclude-if="2.0.x,2.1.x,2.2.x,2.3.x,2.4.x" >}}
If you configure a listener on one of these ports, {{< reuse "kgw-docs/snippets/kgateway-capital.md" >}} rejects the listener. The Gateway or ListenerSet status shows the listener with the `Invalid` reason and a message such as `invalid port 9091 in listener: port is reserved`. The gateway proxy does not open the port or add it to the proxy Service. 
{{< /version >}}
{{< version include-if="2.0.x,2.1.x,2.2.x,2.3.x,2.4.x" >}}
Note that if you configure one of these ports, the gateway proxy still deploys. However, you see error messages, such as the following in the logs. 
```sh
err="failed to apply object apps/v1, Kind=Deployment example-gateway: failed to create typed patch object
(gwtest/example-gateway; apps/v1, Kind=Deployment): .spec.template.spec.containers[name=\"kgateway-proxy\"].
ports: duplicate entries for key [containerPort=9091,protocol=\"TCP\"]"
```
{{< /version >}}
