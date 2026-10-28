1. Follow the [Get started guide]({{< link-hextra path="/quickstart/" >}}) to install {{< reuse "kgw-docs/snippets/kgateway.md" >}}.

2. Deploy a [sample httpbin app]({{< link-hextra path="/install/sample-app/" >}}).

3. {{% reuse "kgw-docs/snippets/prereq-listenerset.md" %}}

   **ListenerSets**: {{< reuse "kgw-docs/versions/warn-2-1-only.md" >}}{{< version include-if="2.0.x,2.1.x,2.2.x,2.3.x,2.4.x" >}} Also, you must install the experimental channel of the Kubernetes Gateway API at version 1.3 or later.{{< /version >}}