# kgateway.dev Contribution Guide

## Getting Started

#### Dependencies:
* `Node.js v18.18.2 or greater`
* `hugo extended v0.160.1`

#### To run `kgateway.dev` locally:
1. `git clone git@github.com:kgateway-dev/kgateway.dev.git`
2. `cd kgateway.dev`
3. `npm install`
4. `hugo server`
5. Visit http://localhost:1313/

## Contributing

### General Pull Request Guidelines
When opening a pull request, each of your commits must contain a `Signed-off-by` trailer to adhere to [DCO](https://developercertificate.org/) requirements. This can be done by one of the following methods:
- Running `make init-git-hooks` which will configure your repo to use the version-controlled [Git hooks](/.githooks) from this repo (preferred)
- Manually copying the [.githooks/prepare-commit-msg](/.githooks/prepare-commit-msg) file to `.git/hooks/prepare-commit-msg` in your copy of this repo
- Making sure to use the `-s` / `--signoff` [flag](https://git-scm.com/docs/git-commit#Documentation/git-commit.txt--s) on each commit

### Contributing to the Documentation

Refer to the [Documentation Contributor Guide](https://kgateway.dev/docs/reference/contribution/) for details on adding documentation, previewing locally, and a style guide.

### Framework tests

The `framework-test*` Makefile targets run a Playwright-based structural quality harness against the built HTML. The harness checks for things like leaked shortcode syntax, unrendered markdown, missing image alt text, console errors in JS, broken theme-toggle behavior, contrast violations, and other regressions that look fine in source but break when rendered.

The harness itself lives in [`solo-io/docs-theme-extras`](https://github.com/solo-io/docs-theme-extras). It's not vendored into this repo — `.docs-test.toml` at the repo root configures the harness (where the built HTML lives, which versions to scan, which warnings to allowlist), and the Makefile targets shell out to the extras checkout to run Playwright against it.

#### Setup (one time)

1. Clone `docs-theme-extras` as a sibling directory of this repo:
   ```sh
   git clone https://github.com/solo-io/docs-theme-extras.git ../docs-theme-extras
   ```
   If you want to put it elsewhere, every `framework-test*` target accepts `FRAMEWORK_EXTRAS_DIR=/abs/path` to override.
2. Install Playwright and the browser binaries (chromium, firefox, webkit) inside that checkout:
   ```sh
   make framework-test-install
   ```
   This is a ~120-180 MB download and runs once.

#### Running the harness

| Target                           | What it does                                                                                                  |
|----------------------------------|---------------------------------------------------------------------------------------------------------------|
| `make framework-test`            | Build the site, run all specs (static + browser + cross-browser), open the HTML report.                       |
| `make framework-test-static`     | Build the site, run only the static specs. Fastest loop — no browser is launched. Good for tight iteration.   |
| `make framework-test-browser`    | Build the site, run the chromium browser specs (tabs, mermaid, theme toggle, copy-md, console errors, etc.).  |
| `make framework-test-cross-browser` | Run the browser specs across chromium, firefox, and webkit. Slowest — use for release-shaped verification. |
| `make framework-test-report`     | Re-open the most recent Playwright HTML report (handy after an earlier run was interrupted).                  |

Each `framework-test*` target builds the site fresh via `hugo160 --gc --minify` and writes to `./public` before Playwright runs. The harness reads `.docs-test.toml` to find that build, the version regex, and the allowlists for known-benign noise.

If a spec fails, the HTML report points at the offending page, captures a screenshot for browser-mode failures, and links to the source. Tighten `.docs-test.toml`'s `allowlists` block as content stabilizes.

### Adding a Lab
1. Add an entry to `data/labs.yaml` with a title, description, and href
2. Verify that the new lab appears correctly at http://localhost:1313/resources/labs/

### Adding a Video
1. Create a thumbnail and add it to the `static/thumbnails` folder. The image should be 960px by 540px (or an equivalent aspect ratio). Use [kebab-case](https://developer.mozilla.org/en-US/docs/Glossary/Kebab_case) for the file name.
2. Add an entry to `data/videos.yaml` with a description, href, and thumbnailHref. The thumbnailHref should be `/thumbnails/<your-image-name>`
3. Verify that the new video appears correctly at http://localhost:1313/resources/videos/

### Modifying a learning path
1. Edit `data/learningpaths.yaml` as appropriate, for example, to add a lab for a specific lesson that doesn't currently reference one.
2. Verify that the change is reflected, by navigating to http://localhost:1313/learn/ and selecting the corresponding learning path.

### Adding a Blog
1. Create a new file in `content/blog`. Use the blog title in [kebab-case](https://developer.mozilla.org/en-US/docs/Glossary/Kebab_case) as the file name.
2. Fill out the blog with content in [Markdown](https://www.markdownguide.org/tools/hugo/). You can use other blogs as an example of specific styling/features but more details are below.
3. Verify that the new blog appears correctly at http://localhost:1313/blog/

#### Blog Requirements and Details

Each blog is required to begin with the following header:
```
---
title: Your Title Here
toc: false
publishDate: 2025-01-28T00:00:00-00:00
author: Author Name
---
```

Note that a `publishDate` in the future will allow for an article to be available only after that date. This allows for multiple articles to be pushed/merged and go live at specific dates.

Blogs have full support for Markdown including headers, code blocks, quotes, ordered and unordered lists, etc. 

To add an image to a blog:
1. Add the image to `assets/blog`. Use [kebab-case](https://developer.mozilla.org/en-US/docs/Glossary/Kebab_case) for the file name. Common convention is to use a short version of the blog title followed by a number for where the image appears in the blog.
2. Add `{{< reuse-image src="blog/<your-image-name>" width="750px" >}}` to your blog where the image should appear. If you want to change the size of the image, you can modify the `width` property.
