#----------------------------------------------------------------------------------
# Repo setup
#----------------------------------------------------------------------------------

.PHONY: init-git-hooks
init-git-hooks:  ## Use the tracked version of Git hooks from this repo
	git config core.hooksPath .githooks


#----------------------------------------------------------------------------------
# Hugo
#----------------------------------------------------------------------------------

# Production build (GC, minify), plus the docs-section PDF (see `pdf` target
# below) so a build always ships a current /downloads/kgateway-envoy-latest.pdf
# alongside the site. Requires `npm install` once beforehand (playwright/pdf-lib).
.PHONY: build
build: pdf

# Local dev server. Hugo's dev server renders entirely in memory, so it never
# sees a `public/` build to pull the PDF from — this does one disk build + PDF
# render up front, written to static/ (which the live server serves verbatim
# regardless of renderToDisk), then hands off to the normal live server. That
# download link is therefore a snapshot as of server startup: edits made
# during the session won't appear in it until you rerun `make pdf` (or
# restart `make serve`).
.PHONY: serve
serve:
	hugo160 --gc --minify
	PDF_OUTPUT=static/downloads/kgateway-envoy-latest.pdf $(MAKE) render-pdf
	hugo160 server

# Alias
.PHONY: server
server: serve

# Remove Hugo output and cache.
.PHONY: clean
clean:
	rm -rf public public-* resources static/downloads .pdf-tools


#----------------------------------------------------------------------------------
# Playwright HTML harness from github.com/solo-io/docs-theme-extras.
#
# The harness checks structural quality of the built HTML (no leaked
# shortcode syntax, no markdown bleed, image alt text, console errors,
# theme-toggle behavior, etc.). It runs against a pre-built ./public
# tree — these targets build the site first via Hugo, then point
# Playwright at the result through .docs-test.toml.
#
# The harness lives in the extras repo and is NOT vendored here. By
# default we look for a sibling checkout at ../docs-theme-extras (matching
# the local-dev replace directive in go.mod). Override on the command
# line: `make framework-test FRAMEWORK_EXTRAS_DIR=/abs/path`.
#----------------------------------------------------------------------------------

FRAMEWORK_EXTRAS_DIR ?= ../docs-theme-extras

# One-time install: npm packages and Playwright browser binaries
# (chromium, firefox, webkit) inside the docs-theme-extras checkout.
# ~120-180 MB of downloads, ~1-3 minutes.
# Serving the HTML report binds a port and BLOCKS until interrupted, so it must
# never run unattended: in CI it hangs the job, and in any scripted/non-tty run
# it hangs the caller. Gate it on an interactive terminal AND the absence of CI.
# The report is still written to playwright-report/ either way — view it with
# `make framework-test-report`.
SHOW_REPORT = if [ -t 1 ] && [ -z "$$CI" ]; then npx playwright show-report; fi

.PHONY: framework-test-install
framework-test-install:  ## Install Playwright + browsers in the extras checkout (one-time)
	@if [ ! -d "$(FRAMEWORK_EXTRAS_DIR)" ]; then \
		echo "docs-theme-extras checkout not found at $(FRAMEWORK_EXTRAS_DIR)." >&2; \
		echo "Clone it as a sibling, or set FRAMEWORK_EXTRAS_DIR=/path/to/docs-theme-extras." >&2; \
		exit 1; \
	fi
	cd $(FRAMEWORK_EXTRAS_DIR) && npm install
	cd $(FRAMEWORK_EXTRAS_DIR) && npx playwright install --with-deps chromium firefox webkit

# Build the site and run the full framework suite (static + browser +
# cross-browser). Opens the HTML report after the run.
.PHONY: framework-test
framework-test:  ## Build, then run the full Playwright harness (static + browser + cross-browser)
	@$(MAKE) _framework_test_preflight
	rm -rf public
	hugo160 --gc --minify > .build.log 2>&1
	cd $(FRAMEWORK_EXTRAS_DIR) && \
		(DOCS_TEST_CONFIG=$(abspath ./.docs-test.toml) npx playwright test; \
		result=$$?; $(SHOW_REPORT); exit $$result)

# Build the site and run only the static specs. Fastest iteration loop —
# no browser launch.
.PHONY: framework-test-static
framework-test-static:  ## Build, then run only the static (no-browser) specs — fastest loop
	@$(MAKE) _framework_test_preflight
	rm -rf public
	hugo160 --gc --minify > .build.log 2>&1
	cd $(FRAMEWORK_EXTRAS_DIR) && \
		(DOCS_TEST_CONFIG=$(abspath ./.docs-test.toml) npx playwright test --project=static; \
		result=$$?; $(SHOW_REPORT); exit $$result)

# Build the site and run only the content specs — author-side lints and
# rendered-HTML integrity against the built content tree (no browser).
.PHONY: framework-test-content
framework-test-content:  ## Build, then run only the content specs
	@$(MAKE) _framework_test_preflight
	rm -rf public
	hugo160 --gc --minify > .build.log 2>&1
	cd $(FRAMEWORK_EXTRAS_DIR) && \
		(DOCS_TEST_CONFIG=$(abspath ./.docs-test.toml) npx playwright test --project=content; \
		result=$$?; $(SHOW_REPORT); exit $$result)

# Build the site and run chromium browser specs (tabs, mermaid, theme
# toggle, copy-md, console errors, viewport, contrast).
.PHONY: framework-test-browser
framework-test-browser:  ## Build, then run the chromium browser specs
	@$(MAKE) _framework_test_preflight
	rm -rf public
	hugo160 --gc --minify > .build.log 2>&1
	cd $(FRAMEWORK_EXTRAS_DIR) && \
		(DOCS_TEST_CONFIG=$(abspath ./.docs-test.toml) npx playwright test --project=browser; \
		result=$$?; $(SHOW_REPORT); exit $$result)

# Build the site and run cross-browser desktop specs across chromium,
# firefox, and webkit.
.PHONY: framework-test-cross-browser
framework-test-cross-browser:  ## Build, then run cross-browser specs (chromium + firefox + webkit)
	@$(MAKE) _framework_test_preflight
	rm -rf public
	hugo160 --gc --minify > .build.log 2>&1
	cd $(FRAMEWORK_EXTRAS_DIR) && \
		(DOCS_TEST_CONFIG=$(abspath ./.docs-test.toml) npx playwright test \
			--project=cross-browser-chromium \
			--project=cross-browser-firefox \
			--project=cross-browser-webkit; \
		result=$$?; $(SHOW_REPORT); exit $$result)

# Open the most recent Playwright HTML report. Handy when an earlier
# framework-test target was interrupted before reaching the report step.
.PHONY: framework-test-report
framework-test-report:  ## Open the most recent Playwright HTML report
	@if [ ! -d "$(FRAMEWORK_EXTRAS_DIR)" ]; then \
		echo "docs-theme-extras checkout not found at $(FRAMEWORK_EXTRAS_DIR)." >&2; \
		exit 1; \
	fi
	cd $(FRAMEWORK_EXTRAS_DIR) && npx playwright show-report

# Shared preflight for the framework-test-* targets.
.PHONY: _framework_test_preflight
_framework_test_preflight:
	@if [ ! -d "$(FRAMEWORK_EXTRAS_DIR)" ]; then \
		echo "docs-theme-extras checkout not found at $(FRAMEWORK_EXTRAS_DIR)." >&2; \
		echo "Clone it as a sibling, or set FRAMEWORK_EXTRAS_DIR=/path/to/docs-theme-extras." >&2; \
		exit 1; \
	fi
	@if [ ! -d "$(FRAMEWORK_EXTRAS_DIR)/node_modules" ]; then \
		echo "Run 'make framework-test-install' first." >&2; exit 1; \
	fi

#----------------------------------------------------------------------------------
# PDF export for the "latest" version of the envoy docs tree.
#
# The whole tree (253 pages, 7.3MB stitched HTML) is past Paged.js's real
# pagination ceiling (~150-200 pages) — confirmed by hand, pagination never
# completed even given 5 minutes. Chunked by top-level SECTION instead: each
# direct child of content/docs/envoy/latest/_index.md opts into the `book`
# output format (outputs: ["html", "book"] + bookChunkRoot: true) via that
# page's own `cascade` front matter (target.path: "/docs/envoy/latest/*",
# a SINGLE-segment glob — matches direct children only, not grandchildren
# like setup/listeners/), not hand-edited into each section's own _index.md.
# render-pdf.mjs merges all of them into one PDF with a continuous,
# per-section bookmark tree. See docs-theme-extras CHANGELOG.md for the full
# design and its trade-offs (no cross-chunk in-PDF jumps; no continuous page
# numbers in each chunk's own printed footer).
#
# PDF_CHUNKS still has to list one path per section BY HAND, in the order
# they should appear in the merged PDF — the cascade above controls which
# pages GET a book.html, not which of them render-pdf.mjs actually fetches
# and merges (that has to be an explicit, ordered list; Hugo has no "list
# every section that opted into an output format" query to generate it
# from). A new top-level section under content/docs/envoy/latest/ picks up
# outputs/bookChunkRoot automatically from the cascade, but still needs a
# manual entry here to actually appear in the PDF.
#
# render-pdf.mjs isn't vendored here — docs-theme-extras' module.mounts only
# covers layouts/assets/data, so a Node script can't ride in as a Hugo
# import. Instead this curls it straight from GitHub, pinned to the exact
# version already in go.mod, so that file is the ONLY version pin; bumping it
# (`hugo160 mod get github.com/solo-io/docs-theme-extras@<version>`) is what
# invalidates the cache below and pulls the matching render-pdf.mjs.
#
# PDF_PROD_HOST reads hugo.yaml's own params.themeExtras.prodHost (requires
# yq) instead of a hardcoded literal, same as ambientmesh.io's Makefile.
#----------------------------------------------------------------------------------
RENDER_PDF_VERSION := $(shell awk '/solo-io\/docs-theme-extras/ {print $$3}' go.mod)
RENDER_PDF_SCRIPT  := .pdf-tools/render-pdf-$(RENDER_PDF_VERSION).mjs
PDF_PROD_HOST       := $(shell yq '.params.themeExtras.prodHost' hugo.yaml)
PDF_CHUNKS := quickstart about install setup traffic-management resiliency security observability operations reference integrations migrate faqs ai
PDF_BOOK_PATHS := $(shell echo "$(PDF_CHUNKS)" | tr ' ' '\n' | sed 's|^|/docs/envoy/latest/|; s|$$|/book.html|' | paste -sd, -)

.PHONY: render-pdf
render-pdf:
	mkdir -p .pdf-tools
	test -f $(RENDER_PDF_SCRIPT) || curl -fsSL https://raw.githubusercontent.com/solo-io/docs-theme-extras/$(RENDER_PDF_VERSION)/scripts/render-pdf.mjs -o $(RENDER_PDF_SCRIPT)
	PDF_PROD_HOST=$(PDF_PROD_HOST) PDF_BOOK_PATHS=$(PDF_BOOK_PATHS) PDF_OUTPUT=public/downloads/kgateway-envoy-latest.pdf node $(RENDER_PDF_SCRIPT)

.PHONY: pdf
pdf:
	hugo160 --gc --minify
	$(MAKE) render-pdf
