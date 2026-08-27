# Product targets for l9-observability-core. The canonical command facade stays in Makefile.
GOV_ROOT ?= $(HOME)/.cursor-governance
OPEN_PR ?= 0

ifneq ($(wildcard $(CURDIR)/.venv/bin/python),)
PYTHON := $(CURDIR)/.venv/bin/python
endif
PYTHON ?= python3

.PHONY: help install-dev lint typecheck inventory-check hygiene-check schema-check \
	check-config reconcile-config check-rules render-rules \
	compile-check verify ci pr-check build regenerate-manifest \
	gov-pr-check gov-pr gov-start gov-wiring-check

help:
	@echo "Core facade (tools.l9_repo):"
	@$(L9_REPO) help
	@echo ""
	@echo "Product / governance wrappers:"
	@grep -E '^[a-zA-Z0-9_-]+:.*?## ' Repo.mk \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

install-dev: ## Install the library and declared development dependencies
	@if command -v uv >/dev/null 2>&1; then \
		uv sync --extra dev; \
	else \
		$(PYTHON) -m pip install -e ".[dev]"; \
	fi
	$(PYTHON) -m pip install -r requirements-repo-runtime.txt

lint: ## Run Ruff lint and format checks
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

typecheck: ## Run strict mypy for the library package
	$(PYTHON) -m mypy src

inventory-check: ## Validate the utility-library repository inventory
	$(PYTHON) scripts/inventory_check.py

hygiene-check: ## Validate generic utility-library source hygiene
	$(PYTHON) scripts/repo_hygiene_audit.py

schema-check: ## Validate the canonical observability JSON Schemas and fixtures
	$(PYTHON) -m pytest -q tests/test_json_schemas.py

compile-check: ## Compile source and tests without writing bytecode into the repository
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m compileall -q src tests tools scripts

check-config: ## Fail if plugin-config.yaml claims what this repository is not
	$(PYTHON) scripts/reconcile_plugin_config.py --check

reconcile-config: ## Rewrite plugin-config.yaml to describe this repository
	$(PYTHON) scripts/reconcile_plugin_config.py

check-rules: ## Fail if the generated Cursor rules drift from templates + config
	$(PYTHON) scripts/render_cursor_rules.py --check

render-rules: ## Render .cursor/rules/*.mdc from templates + plugin-config.yaml
	$(PYTHON) scripts/render_cursor_rules.py

verify: validate check test schema-check compile-check check-config check-rules ## Full deterministic local repository verification

ci: verify ## Repository-local execution alias; organization CI remains externally owned

pr-check: verify ## Local pre-PR gate; never opens a pull request
	uv lock --check
	@if [ "$(OPEN_PR)" != "0" ]; then \
		echo "OPEN_PR=$(OPEN_PR): pr-check is local-only; use make gov-pr for remote PR actions" >&2; \
	fi

build: ## Build wheel and sdist
	$(PYTHON) -m build

regenerate-manifest: ## Regenerate the repository-runtime checksum manifest
	$(PYTHON) scripts/regenerate_runtime_manifest.py

# Cursor-Governance remains the external governance control plane. These wrappers are optional.
gov-pr-check: ## Run Cursor-Governance pr-check against this workspace
	@if [ ! -d "$(GOV_ROOT)" ]; then \
		echo "gov: skip - GOV_ROOT missing ($(GOV_ROOT)); wire Cursor-Governance then retry"; \
	else \
		$(MAKE) -C "$(GOV_ROOT)" pr-check WS="$(CURDIR)"; \
	fi

gov-pr: ## Ask Cursor-Governance to open/remediate a PR for this workspace
	@if [ ! -d "$(GOV_ROOT)" ]; then \
		echo "gov: skip - GOV_ROOT missing ($(GOV_ROOT)); wire Cursor-Governance then retry"; \
	else \
		$(MAKE) -C "$(GOV_ROOT)" pr WS="$(CURDIR)"; \
	fi

gov-start: ## Start Cursor-Governance for this workspace
	@if [ ! -d "$(GOV_ROOT)" ]; then \
		echo "gov: skip - GOV_ROOT missing ($(GOV_ROOT)); wire Cursor-Governance then retry"; \
	else \
		$(MAKE) -C "$(GOV_ROOT)" start WS="$(CURDIR)"; \
	fi

gov-wiring-check: ## Check Cursor-Governance wiring for this workspace
	@if [ ! -d "$(GOV_ROOT)" ]; then \
		echo "gov: skip - GOV_ROOT missing ($(GOV_ROOT)); wire Cursor-Governance then retry"; \
	else \
		$(MAKE) -C "$(GOV_ROOT)" wiring-check WS="$(CURDIR)"; \
	fi
