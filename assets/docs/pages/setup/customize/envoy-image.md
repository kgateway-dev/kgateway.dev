
Build a custom `envoy-wrapper` image on top of any upstream Envoy release and use it in your gateway proxies. For example, this process can be useful to apply CVE fixes that were released upstream, but are not yet released in kgateway.  

## How it works {#how-it-works}

The kgateway data plane isn't a plain Envoy binary. It bundles two extra components on top of upstream Envoy:

- **`envoyinit`**: A Go binary that runs as PID 1, manages the Envoy process lifecycle, and injects bootstrap configuration from xDS.
- **`librust_module.so`**: A Rust dynamic module that powers kgateway's transformation engine (`rustformation`) and other data-plane features. Envoy loads this `.so` module at startup through its Dynamic Modules API.

Because the Dynamic Modules ABI is tied to a specific Envoy minor version, you can't swap in a plain upstream Envoy image. Instead, you must build the module and image together. The `envoy-wrapper-docker` Makefile target handles this: it compiles the Rust module against the Envoy SDK and layers it on top of whatever base image you pass in.

## Before you begin {#before-you-begin}

- A clone of the `kgateway` repository at the **same version** as the kgateway control plane running in your cluster. The repository version determines which Rust module is compiled, and that module must match your control plane.
- Set up a Docker engine with [BuildKit / `buildx`](https://docs.docker.com/buildx/working-with-buildx/) support. For example, you can install the [Docker Desktop app](https://www.docker.com/products/docker-desktop/). 
- Set up a container registry that your cluster can pull from and connect to it. 
- The Rust toolchain is managed automatically by `rustup` using the `rust-toolchain.toml` file in the repository. You don't need to install it yourself.

## Compatibility {#compatibility}

The Rust dynamic module is compiled against the `envoy-proxy-dynamic-modules-rust-sdk`, which is pinned to the same Envoy version that kgateway targets in a given release. This means:

- **Patch-version bumps are safe.** The Dynamic Modules ABI is stable within a minor release. If kgateway targets `v1.37.2`, you can safely use `v1.37.3` or any other `v1.37.x` patch.
- **Minor-version bumps aren't a simple image swap.** Going from `v1.37.x` to `v1.38.x` means updating the SDK pin and rebuilding the module. That's a full Envoy upgrade at the kgateway source level, not something you'd do with this guide.

If you are unsure which Envoy minor version your kgateway release targets, check the `ENVOY_IMAGE` variable at the top of the project `Makefile`.

## Step 1: Build the wrapper image {#build}

From the root of your kgateway clone, run `make envoy-wrapper-docker` with the upstream Envoy image you want and the output registry you control.

```sh
export ENVOY_IMAGE=docker.io/envoyproxy/envoy:v1.37.3
export IMAGE_REGISTRY=registry.example.com/myorg
export VERSION=v2.3.0-custom
make envoy-wrapper-docker
```

The command completes the following tasks:

1. Builds the Rust dynamic module (`librust_module.so`) from `internal/envoy_modules/` by using `cargo-zigbuild`.
2. Creates a Dockerfile that sets the `ENVOY_IMAGE` as the base image (`FROM` entry).
3. Copies the compiled `.so` library, `envoyinit` binary, and entrypoint script to the output directory. 
4. Builds the image with `docker buildx build` and tags the image as `$IMAGE_REGISTRY/envoy-wrapper:$VERSION`.

By default, the build targets your host machine's architecture. To build for `amd64` architectures explicitly, such as when running on an `arm64` laptop, set the `GOARCH` environment variable as shown in the following example: 

```sh
GOARCH=amd64 ENVOY_IMAGE=... IMAGE_REGISTRY=... VERSION=... make envoy-wrapper-docker
```

## Step 2: Push the image {#push}

```sh
docker push registry.example.com/myorg/envoy-wrapper:v2.3.0-custom
```

If your cluster pulls from a private registry, [set up image pull secrets](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/) on the proxy pods. You can add them with the `podTemplate.imagePullSecrets` field in {{< reuse "docs/snippets/gatewayparameters.md" >}}.

## Step 3: Customize the Envoy image {#envoy-image}

Create a {{< reuse "docs/snippets/gatewayparameters.md" >}} resource that points `spec.kube.envoyContainer.image` to your custom wrapper image.

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: custom-envoy-image
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    envoyContainer:
      image:
        registry: registry.example.com/myorg
        repository: envoy-wrapper
        tag: v2.3.0-custom
EOF
```

The `image` field follows the same structure used for all container images in kgateway:

| Field | Description |
|---|---|
| `registry` | Container registry hostname, for example `registry.example.com/myorg` |
| `repository` | Image name, typically `envoy-wrapper` |
| `tag` | Image tag |
| `digest` | Optional. Use instead of or alongside `tag` to pin to an exact image digest |
| `pullPolicy` | Optional. Defaults to `IfNotPresent` |

## Step 4: Reference the GatewayParameters from your Gateway {#gateway}

Create or update your Gateway resource to reference the {{< reuse "docs/snippets/gatewayparameters.md" >}} you just created.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: my-gateway
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  gatewayClassName: {{< reuse "docs/snippets/gatewayclass.md" >}}
  infrastructure:
    parametersRef:
      group: {{< reuse "docs/snippets/gatewayparam-group.md" >}}
      kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
      name: custom-envoy-image
  listeners:
    - name: http
      protocol: HTTP
      port: 80
      allowedRoutes:
        namespaces:
          from: All
EOF
```

When kgateway reconciles this Gateway, it creates a proxy Deployment with the custom image. Existing proxy pods roll over automatically.

## Apply to all gateways by default {#default}

Instead of referencing the same {{< reuse "docs/snippets/gatewayparameters.md" >}} resource in each Gateway, you can configure the `{{< reuse "docs/snippets/gatewayclass.md" >}}` GatewayClass with your custom Envoy image by using the `gatewayClassParametersRefs.kgateway` Helm value. This way, all gateway proxies that use this GatewayClass are automatically deployed with the custom Envoy image. 

```yaml
# values.yaml
gatewayClassParametersRefs:
  kgateway:
    name: custom-envoy-image
    namespace: {{< reuse "docs/snippets/namespace.md" >}}
```

Then upgrade your kgateway installation with this values file:

```sh
helm upgrade -i -n {{< reuse "docs/snippets/namespace.md" >}} {{< reuse "/docs/snippets/helm-kgateway.md" >}} \
  oci://{{< reuse "/docs/snippets/helm-path.md" >}}/charts/{{< reuse "/docs/snippets/helm-kgateway.md" >}} \
  -f values.yaml
```

## Verify {#verify}

Check that the proxy pods are running the custom image.

```sh
kubectl get pods -n {{< reuse "docs/snippets/namespace.md" >}} -l gateway.networking.k8s.io/gateway-name=my-gateway \
  -o jsonpath='{.items[0].spec.containers[0].image}'
```

Example output:

registry.example.com/myorg/envoy-wrapper:v2.3.0-custom
```

## Cleanup {#cleanup}

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete gateway my-gateway -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete {{< reuse "docs/snippets/gatewayparameters.md" >}} custom-envoy-image -n {{< reuse "docs/snippets/namespace.md" >}}
```
