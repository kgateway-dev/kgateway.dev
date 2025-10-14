1. Set up kgateway by following the [Quick start]({{< link-hextra path="/quickstart/" >}}) or [Installation]({{< link-hextra path="/install/" >}}) guides.

2. [Deploy the httpbin sample app]({{< link-hextra path="/install/sample-app/" >}}).

3. Make sure that you have the OpenSSL version of `openssl`, not LibreSSL. The `openssl` version must be at least 1.1.
   1. Check the `openssl` version that is installed. If you see LibreSSL in the output, continue to the next step.
      ```sh
      openssl version
      ```
   2. Install the OpenSSL version (not LibreSSL). For example, you might use Homebrew.
      ```sh
      brew install openssl
      ```
      
   3. Review the output of the OpenSSL installation for the path of the binary file. You can choose to export the binary to your path, or call the entire path whenever the following steps use an openssl command.
      - For example, openssl might be installed along the following path: `/usr/local/opt/openssl@3/bin/`
      - To run commands, you can append the path so that your terminal uses this installed version of OpenSSL, and not the default LibreSSL. `/usr/local/opt/openssl@3/bin/openssl req -new -newkey rsa:4096 -x509 -sha256 -days 3650...`

4. {{< reuse "docs/snippets/prereq-listenerset.md" >}}

   **ListenerSets**: {{< reuse "docs/versions/warn-2-1-only.md" >}} Also, you must install the experimental channel of the Kubernetes Gateway API at version 1.3 or later.