---
title: "macOS Installation"
weight: 10
---

## Install ingress2gateway on macOS

1. Set the environment variables.

    ```bash
    VERSION=v0.4.0
    OS=Darwin
    # One of arm64|x86_64
    ARCH=arm64
    ```

    Refer to the [releases page](https://github.com/kgateway-dev/ingress2gateway/releases) for a list of published ingress2gateway versions.

2. Download the release.

    ```bash
    curl -LO "https://github.com/kgateway-dev/ingress2gateway/releases/download/${VERSION}/ingress2gateway_${OS}_${ARCH}.tar.gz"
    ```

3. Optional: Validate the release tarball.

    Download the ingress2gateway checksum file.

    ```bash
    curl -LO https://github.com/kgateway-dev/ingress2gateway/releases/download/${VERSION}/checksums.txt
    ```

    Validate the binary against the checksum file.

    ```bash
    echo "$(cat checksums.txt)  ingress2gateway" | shasum -a 256 --check
    ```

    If valid, the output is:

    ```bash
    ingress2gateway_$OS_$ARCH.tar.gz: OK
    ```

4. Extract the tarball.

    ```bash
    tar -xvf ingress2gateway_${OS}_${ARCH}.tar.gz
    ```

5. Move the binary to a file location on your system PATH.

    ```bash
    sudo mv ./ingress2gateway /usr/local/bin/ingress2gateway
    sudo chown root: /usr/local/bin/ingress2gateway
    ```

    **Note:** Make sure /usr/local/bin is in your PATH environment variable.

6. Test the installation by checking the version of the binary.

    ```bash
    ingress2gateway version
    ```

    Example output.

    ```console
    ingress2gateway version: v0.3.0
    Built with Go version: go1.25.3
    ```
