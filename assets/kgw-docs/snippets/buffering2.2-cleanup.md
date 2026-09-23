## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete {{< reuse "/kgw-docs/snippets/trafficpolicy.md" >}} transformation-buffer-body -n httpbin --ignore-not-found
kubectl delete {{< reuse "/kgw-docs/snippets/trafficpolicy.md" >}} transformation-buffer-limit -n httpbin --ignore-not-found
kubectl delete listenerpolicy bufferlimits -n {{< reuse "/kgw-docs/snippets/namespace.md" >}} --ignore-not-found
```
