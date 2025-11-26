1. Follow the [Get started guide]({{< link-hextra path="/quickstart/" >}}) to install {{< reuse "docs/snippets/kgateway.md" >}}.

2. Deploy a [sample httpbin app]({{< link-hextra path="/install/sample-app/" >}}).

3. {{% reuse "docs/snippets/prereq-listenerset.md" %}}

   **ListenerSets**: {{< reuse "docs/versions/warn-2-1-only.md" >}} Also, you must install the experimental channel of the Kubernetes Gateway API at version 1.3 or later.