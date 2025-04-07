---
title: Preview and build locally
weight: 20
---

The kgateway documentation is built by using the static site generator Hugo. As you write your content, you can locally preview your changes. 

## Before you begin

1. Download and install the [`hugo` CLI](https://github.com/gohugoio/hugo/releases/tag/v0.135.0) version 0.135.0. Make sure to download the `extended` version to ensure all features are available that are required to build the site. 

2. Make sure that `hugo` is installed. 
   ```sh
   hugo version
   ```
   
   Example output: 
   ```
   hugo v0.135.0-f30603c47f5205e30ef83c70419f57d7eb7175ab+extended darwin/arm64 BuildDate=2024-09-27T13:17:08Z VendorInfo=gohugoio
   ```

3. Install the Node.js dependencies. If you do not have Node.js and `npm` installed on your machine, follow the instructions [here](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) to install them. 
   ```sh
   npm install
   ```
   
## Build the site locally

1. Build the site locally. 
   ```sh
   hugo server -D
   ```

2. Open the site. The local preview is available at [localhost:1313](localhost:1313). 