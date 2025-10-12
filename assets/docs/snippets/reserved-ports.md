The following ports are reserved by {{< reuse "docs/snippets/kgateway-capital.md" >}} and cannot be used when configuring your gateway proxy.  

| Port | Description | 
| -- | -- | 
| 19000 | The Envoy admin port. Gateway proxies expose an admin interface on this port that you can use to access important proxy information, such as the config dump, heap dump, healthchecks, and memory allocation.   |
| 15000 | The agentgateway admin port. Agentgateway proxies expose several endpoints on this port that you can use to access important proxy information, such as the config dump (`15000/config_dump`) and a read-only user interface (`15000/ui`). |
| 8082 | The readiness port. This port can be used to determine if the gateway proxy is ready to receive traffic. | 
| 9091 | The Prometheus scraping port. Gateway proxies expose all metrics on this port so that Prometheus can scrape them. | 

Note that if you configure one of these ports, the gateway proxy still deploys. However, you see error messages, such as the following in the logs. 
```sh
err="failed to apply object apps/v1, Kind=Deployment example-gateway: failed to create typed patch object
(gwtest/example-gateway; apps/v1, Kind=Deployment): .spec.template.spec.containers[name=\"kgateway-proxy\"].
ports: duplicate entries for key [containerPort=9091,protocol=\"TCP\"]"
```