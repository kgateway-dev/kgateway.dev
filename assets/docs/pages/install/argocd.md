In this installation guide, you install {{< reuse "/docs/snippets/kgateway.md" >}} in a Kubernetes cluster by using [Argo CD](https://argoproj.github.io/cd/). Argo CD is a declarative continuous delivery tool that is especially popular for large, production-level installations at scale. This approach incorporates Helm configuration files.

## Before you begin

1. Create or use an existing Kubernetes cluster. 
2. Install the following command-line tools.
   * [`kubectl`](https://kubernetes.io/docs/tasks/tools/#kubectl), the Kubernetes command line tool. Download the `kubectl` version that is within one minor version of the Kubernetes clusters you plan to use.
   * [`argo`](https://argo-cd.readthedocs.io/en/stable/cli_installation/), the Argo CD command line tool.
3. Install Argo CD in your cluster.
   ```shell
   kubectl create namespace argocd
   until kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/v2.12.3/manifests/install.yaml > /dev/null 2>&1; do sleep 2; done
   # wait for deployment to complete
   kubectl -n argocd rollout status deploy/argocd-applicationset-controller
   kubectl -n argocd rollout status deploy/argocd-dex-server
   kubectl -n argocd rollout status deploy/argocd-notifications-controller
   kubectl -n argocd rollout status deploy/argocd-redis
   kubectl -n argocd rollout status deploy/argocd-repo-server
   kubectl -n argocd rollout status deploy/argocd-server   
   ```
4. Update the default Argo CD password for the admin user to `solo.io`.
   ```shell
   # bcrypt(password)=$2a$10$79yaoOg9dL5MO8pn8hGqtO4xQDejSEVNWAGQR268JHLdrCw6UCYmy
   # password: solo.io
   kubectl -n argocd patch secret argocd-secret \
     -p '{"stringData": {
       "admin.password": "$2a$10$79yaoOg9dL5MO8pn8hGqtO4xQDejSEVNWAGQR268JHLdrCw6UCYmy",
       "admin.passwordMtime": "'$(date +%FT%T%Z)'"
   }}'
   ```

## Install

Install {{< reuse "/docs/snippets/kgateway.md" >}} by using Argo CD.

{{< reuse "docs/snippets/argocd.md" >}}


## Next steps

Now that you have {{< reuse "/docs/snippets/kgateway.md" >}} set up and running, check out the following guides to expand your API gateway capabilities.
- Learn more about [{{< reuse "/docs/snippets/kgateway.md" >}}, its features and benefits](../../about/overview). 
- [Deploy an API gateway and sample app](../sample-app/) to test out routing to an app.
- Add routing capabilities to your httpbin route by using the [Traffic management](../../traffic-management) guides. 
- Explore ways to make your routes more resilient by using the [Resiliency](../../resiliency) guides. 
- Secure your routes with external authentication and rate limiting policies by using the [Security](../../security) guides. 

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

Follow the [Uninstall with Argo CD guide](../../operations/uninstall#argocd).
