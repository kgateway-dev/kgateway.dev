{{< callout type="info" >}} The default `openssl` version that is included in macOS is LibreSSL, which does not work with these instructions. Make sure that you have the OpenSSL version of `openssl`, not LibreSSL. {{< /callout >}} The `openssl` version must be at least 1.1.
   1. Check your `openssl` version. If you see **LibreSSL** in the output, continue to the next step.
      ```shell
      openssl version
      ```
   2. Install the OpenSSL version (not LibreSSL). For example, you might use Homebrew.
      ```shell
      brew install openssl
      ```
   3. Review the output of the OpenSSL installation for the path of the binary file. You can choose to export the binary to your path, or call the entire path whenever the following steps use an `openssl` command. 
      * For example, `openssl` might be installed along the following path: `/usr/local/opt/openssl@3/bin/`
      * To run commands, you can append the path so that your terminal uses this installed version of OpenSSL, and not the default LibreSSL. `/usr/local/opt/openssl@3/bin/openssl req -new -newkey rsa:4096 -x509 -sha256 -days 3650...`