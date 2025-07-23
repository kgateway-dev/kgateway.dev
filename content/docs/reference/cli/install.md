---
title: Install the kgwctl CLI
weight: 10
description:
---

Use the `kgwctl` CLI to quickly assess the health of your kgateway control and data plane components. 

1. Save the version of the kgwctl CLI that you want to install as an environment variable. 
   ```sh
   export VERSION=v{{< reuse "docs/versions/kgwctl.md" >}}
   ```
   
2. Create a personal access token in GitHub. For more information, see the [GitHub documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens). 

3. Install the `kgwctl` CLI. 
   ```sh
   curl -sL -H "Authorization: token ${GITHUB_TOKEN}" https://raw.githubusercontent.com/solo-io/kgwctl-temp/refs/heads/main/scripts/install.sh | sh -
   ```
   
   Example output: 
   ```sh
   Downloading kgwctl-darwin-arm64 from release v{{< reuse "docs/versions/kgwctl.md" >}}...
   Verifying checksum...
   Checksum verified successfully
   Download successful: kgwctl-darwin-arm64
   kgwctl CLI was successfully installed 🎉

   Add the kgwctl CLI to your path with:
   export PATH=$HOME/.kgwctl/bin:$PATH
   ```

4. Add the CLI to your path. 
   ```sh
   export PATH=$HOME/.kgwctl/bin:$PATH
   ```

5. Try out the CLI. For example, you can list all supported commands with the following command. 
   ```sh
   kgwctl --help 
   ```
   
   Example output: 
   ```console
   Commands for interacting with kgateway installations.

   Usage:
    kgwctl [command]

   Available Commands:
     analyze     Analyze kgateway resource manifests by file names or directory to find configuration issues and impacts on other resources. 
     check       Check the health of the kgateway control and data plane. 
     completion  Generate the autocompletion script for the `kgwctl` CLI for the specified shell.
     describe    Get the details of one or more kgateway resources. 
     get         List one or more kgateway resources. 
     help        List all supported commands for the `kgwctl` CLI. 
   ...
   ```
   