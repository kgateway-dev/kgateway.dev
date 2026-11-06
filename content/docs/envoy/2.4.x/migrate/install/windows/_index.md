---
title: "Windows Installation"
description: Install the ingress2gateway CLI on Windows.
weight: 30
---

## Install ingress2gateway on Windows

Choose the shell to run the commands in. If you use Windows Subsystem for Linux (WSL), follow the [Linux installation](../linux/) instead.

{{< tabs >}}
{{% tab name="PowerShell" %}}

1. Set the environment variables.

    ```powershell
    $VERSION = "v0.5.0"
    $OS = "Windows"
    # One of x86_64|arm64|i386
    $ARCH = "x86_64"
    # Hide the Invoke-WebRequest progress bar, which slows downloads in Windows PowerShell 5.1
    $ProgressPreference = 'SilentlyContinue'
    ```

    Refer to the [releases page](https://github.com/kgateway-dev/ingress2gateway/releases) for a list of published ingress2gateway versions.

2. Download the release.

    ```powershell
    Invoke-WebRequest -Uri "https://github.com/kgateway-dev/ingress2gateway/releases/download/$VERSION/ingress2gateway_${OS}_${ARCH}.zip" -OutFile "ingress2gateway_${OS}_${ARCH}.zip"
    ```

3. Optional: Validate the release archive.

    Download the ingress2gateway checksum file.

    ```powershell
    Invoke-WebRequest -Uri "https://github.com/kgateway-dev/ingress2gateway/releases/download/$VERSION/checksums.txt" -OutFile "checksums.txt"
    ```

    Compare the archive's SHA256 hash with the value in the checksum file.

    ```powershell
    $expected = (Select-String -Path checksums.txt -Pattern "ingress2gateway_${OS}_${ARCH}.zip" -SimpleMatch).Line.Split(" ")[0]
    $actual = (Get-FileHash -Path "ingress2gateway_${OS}_${ARCH}.zip" -Algorithm SHA256).Hash
    if ($actual -eq $expected) { "ingress2gateway_${OS}_${ARCH}.zip: OK" } else { "ingress2gateway_${OS}_${ARCH}.zip: checksum mismatch" }
    ```

    If valid, the output is:

    ```console
    ingress2gateway_Windows_x86_64.zip: OK
    ```

4. Extract the archive into an `ingress2gateway` folder.

    ```powershell
    Expand-Archive -Path "ingress2gateway_${OS}_${ARCH}.zip" -DestinationPath ingress2gateway
    ```

5. Add the folder to your PATH. The following command updates the PATH for the current PowerShell session. To keep the change in new sessions, add the folder to your user PATH in **System Properties** > **Environment Variables**.

    ```powershell
    $env:Path = "$PWD\ingress2gateway;$env:Path"
    ```

6. Test the installation by checking the version of the binary.

    ```powershell
    ingress2gateway version
    ```

{{% /tab %}}
{{% tab name="Git Bash" %}}

1. Set the environment variables.

    ```bash
    VERSION=v0.5.0
    OS=Windows
    # One of x86_64|arm64|i386
    ARCH=x86_64
    ```

    Refer to the [releases page](https://github.com/kgateway-dev/ingress2gateway/releases) for a list of published ingress2gateway versions.

2. Download the release.

    ```bash
    curl -LO "https://github.com/kgateway-dev/ingress2gateway/releases/download/${VERSION}/ingress2gateway_${OS}_${ARCH}.zip"
    ```

3. Optional: Validate the release archive.

    Download the ingress2gateway checksum file.

    ```bash
    curl -LO "https://github.com/kgateway-dev/ingress2gateway/releases/download/${VERSION}/checksums.txt"
    ```

    Validate the archive against the checksum file.

    ```bash
    grep -F "  ingress2gateway_${OS}_${ARCH}.zip" checksums.txt | sha256sum --check
    ```

    If valid, the output is:

    ```console
    ingress2gateway_Windows_x86_64.zip: OK
    ```

4. Extract the archive into an `ingress2gateway` folder.

    ```bash
    unzip -o "ingress2gateway_${OS}_${ARCH}.zip" -d ingress2gateway
    ```

5. Add the folder to your PATH. The following command updates the PATH for the current Git Bash session. To keep the change in new sessions, add the command to your `~/.bashrc` file with the full folder path.

    ```bash
    export PATH="$PWD/ingress2gateway:$PATH"
    ```

6. Test the installation by checking the version of the binary.

    ```bash
    ingress2gateway version
    ```

{{% /tab %}}
{{< /tabs >}}
