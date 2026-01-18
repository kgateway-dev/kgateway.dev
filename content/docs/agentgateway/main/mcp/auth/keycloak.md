---
title: Set up Keycloak
weight: 20
---

Set up Keycloak in your cluster as your OAuth identity provider. Then, configure your agentgateway proxy to connect to your  With this guide, you set up a sample realm with two users, as well as configure settings that you might use for future auth scenarios.

## Install Keycloak {#install}

You might want to test how to restrict access to your applications to authenticated users, such as with external auth or JWT policies. You can install Keycloak in your cluster as an OpenID Connect (OIDC) provider.

The following steps install Keycloak in your cluster, and configure two user credentials as follows.
* Username: `user1`, password: `password`, email: `user1@example.com`
* Username: `user2`, password: `password`, email: `user2@solo.io`

Install and configure Keycloak:

1. Create a namespace for your Keycloak deployment.
   ```shell
   kubectl create namespace keycloak
   ```
2. Create the Keycloak deployment.
   ```shell
   kubectl -n keycloak apply -f https://raw.githubusercontent.com/solo-io/gloo-mesh-use-cases/main/policy-demo/oidc/keycloak.yaml
   ```
3. Wait for the Keycloak rollout to finish.
   ```shell
   kubectl -n keycloak rollout status deploy/keycloak
   ```
4. Set the Keycloak endpoint details from the load balancer service. If you are running locally in kind and need a local IP address for the load balancer service, consider using [`cloud-provider-kind`](https://github.com/kubernetes-sigs/cloud-provider-kind).
   ```shell
   export ENDPOINT_KEYCLOAK=$(kubectl -n keycloak get service keycloak -o jsonpath='{.status.loadBalancer.ingress[0].ip}{.status.loadBalancer.ingress[0].hostname}'):8080
   export HOST_KEYCLOAK=$(echo ${ENDPOINT_KEYCLOAK} | cut -d: -f1)
   export PORT_KEYCLOAK=$(echo ${ENDPOINT_KEYCLOAK} | cut -d: -f2)
   export KEYCLOAK_URL=http://${ENDPOINT_KEYCLOAK}
   echo $KEYCLOAK_URL
   ```
5. Set the Keycloak admin token. If you see a parsing error, try running the `curl` command by itself. You might notice that your internet provider or network rules are blocking the requests. If so, you can update your security settings or change the network so that the request can be processed.
   ```shell
   export KEYCLOAK_TOKEN=$(curl -d "client_id=admin-cli" -d "username=admin" -d "password=admin" -d "grant_type=password" "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" | jq -r .access_token)
   echo $KEYCLOAK_TOKEN
   ```

6. Use the admin token to configure Keycloak with the two users for testing purposes. If you get a `401 Unauthorized` error, run the previous command and try again.
   ```shell
   # Create initial token to register the client
   read -r client token <<<$(curl -H "Authorization: Bearer ${KEYCLOAK_TOKEN}" -X POST -H "Content-Type: application/json" -d '{"expiration": 0, "count": 1}' $KEYCLOAK_URL/admin/realms/master/clients-initial-access | jq -r '[.id, .token] | @tsv')
   export KEYCLOAK_CLIENT=${client}
   echo $KEYCLOAK_CLIENT

   # Register the client
   read -r id secret <<<$(curl -k -X POST -d "{ \"clientId\": \"${KEYCLOAK_CLIENT}\" }" -H "Content-Type:application/json" -H "Authorization: bearer ${token}" ${KEYCLOAK_URL}/realms/master/clients-registrations/default| jq -r '[.id, .secret] | @tsv')
   export KEYCLOAK_SECRET=${secret}
   echo $KEYCLOAK_SECRET

   # Add allowed redirect URIs
   curl -k -H "Authorization: Bearer ${KEYCLOAK_TOKEN}" -X PUT -H "Content-Type: application/json" -d '{"serviceAccountsEnabled": true, "directAccessGrantsEnabled": true, "authorizationServicesEnabled": true, "redirectUris": ["*"]}' $KEYCLOAK_URL/admin/realms/master/clients/${id}

   # Add the group attribute in the JWT token returned by Keycloak
   curl -H "Authorization: Bearer ${KEYCLOAK_TOKEN}" -X POST -H "Content-Type: application/json" -d '{"name": "group", "protocol": "openid-connect", "protocolMapper": "oidc-usermodel-attribute-mapper", "config": {"claim.name": "group", "jsonType.label": "String", "user.attribute": "group", "id.token.claim": "true", "access.token.claim": "true"}}' $KEYCLOAK_URL/admin/realms/master/clients/${id}/protocol-mappers/models

   # Create first user
   curl -H "Authorization: Bearer ${KEYCLOAK_TOKEN}" -X POST -H "Content-Type: application/json" -d '{"username": "user1", "email": "user1@example.com", "firstName": "Alice", "lastName": "Doe", "enabled": true, "attributes": {"group": "users"}, "credentials": [{"type": "password", "value": "password", "temporary": false}]}' $KEYCLOAK_URL/admin/realms/master/users

   # Create second user
   curl -H "Authorization: Bearer ${KEYCLOAK_TOKEN}" -X POST -H "Content-Type: application/json" -d '{"username": "user2", "email": "user2@solo.io", "firstName": "Bob", "lastName": "Doe", "enabled": true, "attributes": {"group": "users"}, "credentials": [{"type": "password", "value": "password", "temporary": false}]}' $KEYCLOAK_URL/admin/realms/master/users

   # Remove the trusted-hosts client registration policies (testing-purpose only)
   trusted_hosts=$(curl -v -H "Authorization: Bearer ${KEYCLOAK_TOKEN}" \
    "${KEYCLOAK_URL}/admin/realms/master/components?type=org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy" \
    | jq -r '
     if type=="array" then
       .[] | select(.providerId=="trusted-hosts") | .id
     else
       empty
    end
   ')

   curl -X DELETE \
     -H "Authorization: Bearer ${KEYCLOAK_TOKEN}" \
     "${KEYCLOAK_URL}/admin/realms/master/components/${trusted_hosts}"

   # Remove the allowed-client-templates client registration policies (testing-purpose only)

   allowed_client_templates=$(curl -v \
    -H "Authorization: Bearer ${KEYCLOAK_TOKEN}" \
    "${KEYCLOAK_URL}/admin/realms/master/components?type=org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy" \
    | jq -r '
    .[]
     | select(.providerId=="allowed-client-templates" and .subType=="anonymous")
     | .id
   ')

   curl -X DELETE \
     -H "Authorization: Bearer ${KEYCLOAK_TOKEN}" \
     "${KEYCLOAK_URL}/admin/realms/master/components/${allowed_client_templates}"
   ```

7. Open the Keycloak frontend.
   ```
   open $KEYCLOAK_URL
   ```

8. Log in to the admin console, and enter `admin` as the username and `admin` as your password. 

9. In the Keycloak admin console, go to **Users**, and verify that the users that created earlier are displayed. You might need to click on **View all users** to see them. 

10. In the Keycloak admin console, go to **Clients**, and verify that you can see a client ID that equals the output of `$KEYCLOAK_CLIENT`. 

## Retrieve JWKS path and issue URL {#configure}

You might integrate OIDC with your apps. In such cases, you might need particular details from the OIDC provider to fully set up your apps. To use Keycloak for OAuth protection of these apps, you need certain settings and information from Keycloak.

The following instructions assume that you are still logged into the **Administration Console** from the previous step.

1. Confirm that you have the following environmental variables set. If not, refer to [Step 1: Install Keycloak](#install-keycloak) section.
   ```shell
   echo $KEYCLOAK_URL
   ```

2. Get the issuer and JWKS path. The agentgateway proxy uses these values to validate the JWTs. 
    1. From the sidebar menu options, click **Realm Settings**.
    2. From the **General** tab, scroll down to the **Endpoints** section and open the **OpenID Endpoint Configuration** link. In a new tab, your browser opens to a URL similar to `http://$KEYCLOAK_URL:8080/realms/master/.well-known/openid-configuration`.
    3. In the OpenID configuration, search for the `issuer` field. Save the value as an environment variable, such as the following example. 
       ```sh
       export KEYCLOAK_ISSUER=$KEYCLOAK_URL/realms/master
       ```
    4. In the OpenID configuration, search for the `jwks_uri` field, and copy the path without the Keycloak URL that you retrieved earlier. For example, the path might be set to `/realms/master/protocol/openid-connect/certs`.
       ```shell
       export KEYCLOAK_JWKS_PATH=/realms/master/protocol/openid-connect/certs
       ```

## Next 

[Set up MCP auth]({{< link-hextra path="/mcp/auth/setup/" >}}).
 
## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```
kubectl delete namespace keycloak
```