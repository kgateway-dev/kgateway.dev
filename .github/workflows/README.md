# GitHub Workflows

This directory contains the GitHub Actions workflows for the kgateway.dev website.

## update-api-docs.yml

This workflow is used to update the API and Helm reference docs for the kgateway.dev website, based on code in the kgateway repo.

### API reference

[Published page](https://kgateway.dev/docs/reference/api/)

Source files: 
* [Go code in the API directory](https://github.com/kgateway-dev/kgateway/tree/main/api/v1alpha1)

The workflow uses the [crd-ref-docs](https://github.com/elastic/crd-ref-docs) tool to generate Markdown documentation from the API types.

Process to generate markdown content from source files:

1. Update the comments in the .go files in the kgateway/api directory
2. Run `make generated-code`
3. Open a PR and merge your changes into the code repo
4. In the kgateway.dev docs repo, manually trigger the Update API Documentation GitHub Action
5. The Action updates the [markdown source file](https://github.com/kgateway-dev/kgateway.dev/blob/main/content/docs/reference/api.md)
6. The Action opens a PR with the updated content
7. Review and merge the PR
8. Upon merge, the docs should be automatically built and published

### Helm reference

[Published page](https://kgateway.dev/docs/reference/helm/)

Source files:
* [Helm files in the code repo](https://github.com/kgateway-dev/kgateway/tree/main/install/helm)

The workflow uses the [helm docs](https://github.com/norwoodj/helm-docs/) tool to generate Markdown documentation from the API types.

Process to generate markdown content from source files: (same as the API docs process)

1. Update the comments in the `values.yaml` files in the `kgateway/install/helm` directory for each field: 
   * [kgateway values](https://github.com/kgateway-dev/kgateway/blob/main/install/helm/kgateway/values.yaml)
   * [CRD values (currently none)](https://github.com/kgateway-dev/kgateway/blob/main/install/helm/kgateway-crds/values.yaml)
2. Run `make generated-code`
3. Open a PR and merge your changes into the code repo
4. In the kgateway.dev docs repo, manually trigger the Update API Documentation GitHub Action
5. The Action updates the markdown source file conrefs for both Helm charts:
   * [kgateway values](https://github.com/kgateway-dev/kgateway.dev/blob/main/content/docs/reference/helm/helm.md)
   * [CRD values](https://github.com/kgateway-dev/kgateway.dev/blob/main/content/docs/reference/helm/crds.md)
6. The Action opens a PR with the updated content
7. Review and merge the PR
8. Upon merge, the docs should be automatically built and published

## card-check.yml

This workflow is used to check the `_index.md` docs files to make sure that the cards include the right links to subpages in that directory.

For more information on how this works, see the [card-check.py](../../scripts/card-check.py) script.
