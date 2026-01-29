# kgateway.dev Contribution Guide

## Getting Started

#### Dependencies:
* `Node.js v18.18.2 or greater`
* `hugo extended v0.135.0`

#### To run `kgateway.dev` locally:
1. `git@github.com:kgateway-dev/kgateway.dev.git`
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

Refer to the [Documentation Contributor Guide](https://kgateway.dev/docs/envoy/latest/reference/contribution/) for details on adding documentation, previewing locally, and a style guide.

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
1. Add the image to `assets/blog`. Use [kebab-case](https://developer.mozilla.org/en-US/docs/Glossary/Kebab_case) for the file name. I generally use a short version of the blog title followed by a number for where the image appears in the blog.
2. Add `{{< reuse-image src="blog/<your-image-name>" width="750px" >}}` to your blog where the image should appear. If you want to change the size of the image, you can modify the `width` property.
