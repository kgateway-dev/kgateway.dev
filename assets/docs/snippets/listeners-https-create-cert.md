1. Create a directory to store your TLS credentials in. 
   ```sh
   mkdir example_certs
   ```

2. Create a self-signed root certificate. The following command creates a root certificate that is valid for a year and can serve any hostname. You use this certificate to sign the server certificate for the gateway later. For other command options, see the [OpenSSL docs](https://www.openssl.org/docs/manmaster/man1/openssl-req.html).
   ```sh
   # root cert
   openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -subj '/O=any domain/CN=*' -keyout example_certs/root.key -out example_certs/root.crt
   ```

3. Create an OpenSSL configuration that matches the HTTPS hostname you plan to use. Replace every `example.com` reference with the base domain that your listener serves.
   ```sh
   cat <<'EOF' > example_certs/gateway.cnf
   [ req ]
   default_bits = 2048
   prompt = no
   default_md = sha256
   distinguished_name = dn
   req_extensions = req_ext

   [ dn ]
   CN = *.example.com
   O = any domain

   [ req_ext ]
   subjectAltName = @alt_names

   [ alt_names ]
   DNS.1 = *.example.com
   DNS.2 = example.com
   EOF
   ```

4. Use the configuration and root certificate to create and sign the gateway certificate.
   ```sh
   openssl req -new -nodes -keyout example_certs/gateway.key -out example_certs/gateway.csr -config example_certs/gateway.cnf
   openssl x509 -req -sha256 -days 365 \
     -CA example_certs/root.crt -CAkey example_certs/root.key -set_serial 0 \
     -in example_certs/gateway.csr -out example_certs/gateway.crt \
     -extfile example_certs/gateway.cnf -extensions req_ext
   ```

5. Create a Kubernetes secret to store your server TLS certificate. You create the secret in the same cluster and namespace that the gateway is deployed to.
   ```sh
   kubectl create secret tls -n {{< reuse "docs/snippets/namespace.md" >}} https \
     --key example_certs/gateway.key \
     --cert example_certs/gateway.crt
   kubectl label secret https gateway=https --namespace {{< reuse "docs/snippets/namespace.md" >}}
   ```
