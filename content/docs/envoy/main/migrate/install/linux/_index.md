---
title: "Linux Installation"
weight: 20
---

## Install ingress2gateway on Linux

1. Set your environment variables.

    ```bash
    VERSION=v0.3.0
    OS=Linux
    # One of arm64|x86_64|i386
    ARCH=arm64
    ```

    Refer to the [releases page](https://github.com/kgateway-dev/ingress2gateway/releases) for a list of published ingress2gateway versions.

2. Download the release.

    ```bash
    curl -LO "https://github.com/kgateway-dev/ingress2gateway/releases/download/${VERSION}/ingress2gateway_${OS}_${ARCH}.tar.gz"
    ```

3. Validate the release tarball (optional).

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

5. Install ingress2gateway.

    ```bash
    sudo install -o root -g root -m 0755 ingress2gateway /usr/local/bin/ingress2gateway
    ```

    **Note:** If you do not have root access on the target system, you can still install ingress2gateway to the ~/.local/bin directory:

    ```bash
    chmod +x ingress2gateway
    mkdir -p ~/.local/bin
    mv ./ingress2gateway ~/.local/bin/ingress2gateway
    # and then append (or prepend) ~/.local/bin to $PATH
    ```

6. Test the installation by checking the version of the binary.

    ```bash
    ingress2gateway version
    ```

    **Note:** Make sure /usr/local/bin is in your PATH environment variable.
