1. Create a directory to store your TLS credentials in. 
   ```sh
   mkdir example_certs
   ```

2. Create a self-signed root certificate. The following command creates a root certificate that is valid for a year and can serve any hostname. You use this certificate to sign the server certificate for the gateway later. For other command options, see the [OpenSSL docs](https://www.openssl.org/docs/manmaster/man1/openssl-req.html).
   ```sh
   # root cert
   openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -subj '/O=any domain/CN=*' -keyout example_certs/root.key -out example_certs/root.crt
   ```

3. Use the root certificate to sign the gateway certificate.
   ```sh
   openssl req -out example_certs/gateway.csr -newkey rsa:2048 -nodes -keyout example_certs/gateway.key -subj "/CN=*/O=any domain"
   openssl x509 -req -sha256 -days 365 -CA example_certs/root.crt -CAkey example_certs/root.key -set_serial 0 -in example_certs/gateway.csr -out example_certs/gateway.crt
   ```

4. Create a Kubernetes secret to store your server TLS certificate. You create the secret in the same cluster and namespace that the gateway is deployed to.
   ```sh
   kubectl create secret tls -n {{< reuse "docs/snippets/ns-system.md" >}} https \
     --key example_certs/gateway.key \
     --cert example_certs/gateway.crt
   kubectl label secret https gateway=https --namespace {{< reuse "docs/snippets/ns-system.md" >}}
   ```