---
linkTitle: "Kgateway 2.4.x"
title: Kgateway 2.4.x
description: Kgateway is a Kubernetes-native API gateway built on Envoy and the Gateway API.
# PDF export. This one page opting into `book` is the whole opt-in: the format
# stitches this page plus its entire .Pages subtree into one print document, so
# the PDF is scoped to this version tree by where the opt-in lives.
#
# LIST THE WHOLE SET, not just html and book. Hugo's `outputs` REPLACES a page's
# defaults rather than adding to them, so `["html", "book"]` silently drops this
# page's .md, RSS and llms.txt — nothing fails, and only this one page is
# affected, which is exactly why it survives review. These four are `outputs.section`
# from hugo.yaml, copied, plus `book`.
#
# No cascade, and no `bookChunkRoot`. Both belonged to the earlier Paged.js
# pipeline, which could not paginate the tree as one document and so built one
# book per top-level section. The PDF is rendered by WeasyPrint now (solo-io/docs
# .github/workflows/pdf-export.yml), which renders the whole tree in one pass, and
# the cascade's `outputs` was reaching all 14 section roots and stripping their
# .md and llms.txt files along the way.
#
# The book is not built by an ordinary build: docs-theme-extras gates it behind
# `HUGO_PARAMS_BUILDBOOK=true`, which only the PDF workflow sets. See the module's
# docs/configuration/pdf-export.md.
outputs: ["html", "rss", "markdown", "llms", "book"]
---

Welcome to the documentation for the kgateway open source project!
