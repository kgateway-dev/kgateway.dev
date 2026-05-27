#----------------------------------------------------------------------------------
# Repo setup
#----------------------------------------------------------------------------------

.PHONY: init-git-hooks
init-git-hooks:  ## Use the tracked version of Git hooks from this repo
	git config core.hooksPath .githooks


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
	hugo160 --gc --minify > .build.log 2>&1
	cd $(FRAMEWORK_EXTRAS_DIR) && \
		(DOCS_TEST_CONFIG=$(abspath ./.docs-test.toml) npx playwright test; \
		result=$$?; npx playwright show-report; exit $$result)

# Build the site and run only the static specs. Fastest iteration loop —
# no browser launch.
.PHONY: framework-test-static
framework-test-static:  ## Build, then run only the static (no-browser) specs — fastest loop
	@$(MAKE) _framework_test_preflight
	hugo160 --gc --minify > .build.log 2>&1
	cd $(FRAMEWORK_EXTRAS_DIR) && \
		(DOCS_TEST_CONFIG=$(abspath ./.docs-test.toml) npx playwright test --project=static; \
		result=$$?; npx playwright show-report; exit $$result)

# Build the site and run chromium browser specs (tabs, mermaid, theme
# toggle, copy-md, console errors, viewport, contrast).
.PHONY: framework-test-browser
framework-test-browser:  ## Build, then run the chromium browser specs
	@$(MAKE) _framework_test_preflight
	hugo160 --gc --minify > .build.log 2>&1
	cd $(FRAMEWORK_EXTRAS_DIR) && \
		(DOCS_TEST_CONFIG=$(abspath ./.docs-test.toml) npx playwright test --project=browser; \
		result=$$?; npx playwright show-report; exit $$result)

# Build the site and run cross-browser desktop specs across chromium,
# firefox, and webkit.
.PHONY: framework-test-cross-browser
framework-test-cross-browser:  ## Build, then run cross-browser specs (chromium + firefox + webkit)
	@$(MAKE) _framework_test_preflight
	hugo160 --gc --minify > .build.log 2>&1
	cd $(FRAMEWORK_EXTRAS_DIR) && \
		(DOCS_TEST_CONFIG=$(abspath ./.docs-test.toml) npx playwright test \
			--project=cross-browser-chromium \
			--project=cross-browser-firefox \
			--project=cross-browser-webkit; \
		result=$$?; npx playwright show-report; exit $$result)

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
