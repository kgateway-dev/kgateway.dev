---
title: "Windows Installation"
weight: 30
---

## Install ingress2gateway on Windows

1. Set your environment variables.

    ```bash
    VERSION=v0.3.0
    OS=Windows
    # One of arm64|x86_64|i386
    ARCH=arm64
    ```

    Refer to the [releases page](https://github.com/kgateway-dev/ingress2gateway/releases) for a list of published ingress2gateway versions.

2. Download the release.

    ```bash
    curl -LO "https://github.com/kgateway-dev/ingress2gateway/releases/download/${VERSION}/ingress2gateway_${OS}_${ARCH}.zip"
    ```

3. Optional: Validate the release tarball.

    Download the ingress2gateway checksum file.

    ```bash
    curl -LO https://github.com/kgateway-dev/ingress2gateway/releases/download/${VERSION}/checksums.txt
    ```

    Validate the binary against the checksum file.

    Using Command Prompt, manually compare CertUtil's output to the downloaded checksum file.

    ```bash
    CertUtil -hashfile ingress2gateway_${OS}_${ARCH}.zip SHA256
    ```

    If valid, the output is:

    ```bash
    ingress2gateway_$OS_$ARCH.zip: OK
    ```

4. Extract the tarball.

    ```bash
    tar -xvf ingress2gateway_${OS}_${ARCH}.zip
    ```

5. Append or prepend the binary to your PATH environment variable.

6. Test the installation by checking the version of the binary.

    ```bash
    ingress2gateway version
    ```
