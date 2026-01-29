# Scripts

This directory contains scripts or other tools that are used to help improve the kgateway website and documentation.

## generate-ref-docs.py

Generates API, Helm, and metrics reference documentation from the upstream **kgateway** repository. The script clones kgateway at a given tag or branch, runs [crd-ref-docs](https://github.com/elastic/crd-ref-docs) and [helm-docs](https://github.com/norwoodj/helm-docs) plus a metrics tool, and writes reference docs into this site (kgateway.dev) and, when `AGENTGATEWAY_WEBSITE_DIR` is set, into the agentgateway docs repo.

**Workflow location:** The workflow that runs this script lives in the **upstream [kgateway](https://github.com/kgateway-dev/kgateway) repository**, not in this repo. It is tied to kgateway releases and runs automatically when a release is published, and can also be triggered manually. See `kgateway/.github/workflows/update-api-docs.yml` in the kgateway repo.

## card-check.py

A script to check the `_index.md` docs files to make sure that the cards include the right links to subpages in that directory.

This script is used by the `/github/workflows/card-check.yml` GitHub Action.

You can also run this script locally from the root directory:

```shell
python3 scripts/card-check.py
```

Example cards shortcode:

```shell
{{< cards >}}
  {{< card link="http" title="HTTP listener" >}}
  {{< card link="https" title="HTTPS listener" >}}
  {{< card link="tcp" title="TCP listener" >}}
  {{< card link="experimental" title="Experimental API" >}}
  {{< card link="typo" title="Example typos" >}}
{{< /cards >}}
```

Example directory structure with how the cards shortcode passes or fails:

```
content/docs/
├── listeners/
│   ├── _index.md  ✅ Contains cards shortcode
│   ├── http.md    ✅ Valid link
│   ├── https.md   ✅ Valid link
│   ├── tcp.md     ✅ Valid link
│   ├── errors.md  ❌ Not listed in cards
│   ├── experimental/ ✅ Valid (has `_index.md` and `test.md`)
│   │   ├── _index.md
│   │   ├── test.md
│   ├── typp.md    ❌ Should be `typp.md` in cards
│   ├── ../../traffic-management/direct-response ✅ Valid (relative link exists)
│   ├── ../../invalid/path ❌ Invalid (doesn't exist)
```

Example output:

```
Checking directories under: /Users/yourname/kgateway.dev/content/docs
Scanning: /Users/yourname/kgateway.dev/content/docs/listeners
⚠️ Missing cards in content/docs/listeners/_index.md: {'errors'}
❌ Extra cards in content/docs/listeners/_index.md that don’t match any local .md file, valid subdirectory, or valid relative path: {'typp', '../../invalid/path'}
```