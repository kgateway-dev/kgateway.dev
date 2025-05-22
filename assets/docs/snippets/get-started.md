2. Deploy the Kubernetes Gateway API CRDs.

   ```sh
   kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v{{< reuse "docs/versions/k8s-gw-version.md" >}}/standard-install.yaml
   ```
   
   <!--wait
   wait:
     target:
       kind: CustomResourceDefinition
       metadata:
         name: gatewayclasses.gateway.networking.k8s.io
         namespace: default
     jsonPath: .status.acceptedNames.kind
     jsonPathExpectation:
       comparator: equals
       value: "'GatewayClass'"
     polling:
       timeoutSeconds: 30
   -->
   
3. Deploy the kgateway CRDs by using Helm. The following command uses the latest stable release, v{{< reuse "docs/versions/n-patch.md" >}}. For active development, update the version to v{{< reuse "docs/versions/patch-dev.md" >}}.

   ```sh
   helm upgrade -i --create-namespace --namespace kgateway-system --version v{{< reuse "docs/versions/n-patch.md" >}} kgateway-crds oci://cr.kgateway.dev/kgateway-dev/charts/kgateway-crds
   ```
   
   <!--wait
   wait:
     target:
       kind: CustomResourceDefinition
       metadata:
         name: trafficpolicies.gateway.kgateway.dev
         namespace: default
     jsonPath: .status.acceptedNames.kind
     jsonPathExpectation:
       comparator: equals
       value: "'TrafficPolicy'"
     polling:
       timeoutSeconds: 30
   -->

4. Install kgateway by using Helm. The following command uses the latest stable release, v{{< reuse "docs/versions/n-patch.md" >}}. For active development, update the version to v{{< reuse "docs/versions/patch-dev.md" >}}.

   ```sh
   helm upgrade -i --namespace kgateway-system --version v{{< reuse "docs/versions/n-patch.md" >}} kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway
   ```

5. Make sure that `kgateway` is running.

   ```sh
   kubectl get pods -n kgateway-system
   ```

   Example output:

   ```console {id="no-test"}
   NAME                        READY   STATUS    RESTARTS   AGE
   kgateway-5495d98459-46dpk   1/1     Running   0          19s
   ```
   
   <!--wait
   wait:
     target:
       kind: GatewayClass
       metadata:
         name: kgateway
         namespace: default
     jsonPath: .status.conditions[?(@.type == "Accepted")].status
     jsonPathExpectation:
       comparator: equals
       value: "'True'"
     polling:
       timeoutSeconds: 30
   -->
   <!--wait
   wait:
     target:
       kind: Deployment
       metadata:
         name: kgateway
         namespace: kgateway-system
     jsonPath: .status.readyReplicas
     jsonPathExpectation:
       comparator: equals
       value: 1
     polling:
       timeoutSeconds: 120
   -->  