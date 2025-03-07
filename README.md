# kgateway.dev Contribution Guide

## Getting Started

#### Dependencies:
* `Node.js v18.18.2 or greater`
* `hugo v0.134.2 or greater`

#### To run `kgateway.dev` locally:
1. `git@github.com:kgateway-dev/kgateway.dev.git`
2. `cd kgateway.dev`
3. `npm install`
4. `hugo server`
5. Visit http://localhost:1313/

## Contributing
### Adding a Lab
1. Add an entry to `data/labs.yaml` with a title, description, and href
2. Verify that the new lab appears correctly at http://localhost:1313/resources/labs/

### Adding a Video
1. Create a thumbnail and add it to the `static/thumbnails` folder. The image should be 960px by 540px (or an equivalent aspect ratio). Use [kebab-case](https://developer.mozilla.org/en-US/docs/Glossary/Kebab_case) for the file name.
2. Add an entry to `data/videos.yaml` with a description, href, and thumbnailHref. The thumbnailHref should be `/thumbnails/<your-image-name>`
3. Verify that the new video appears correctly at http://localhost:1313/resources/videos/

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