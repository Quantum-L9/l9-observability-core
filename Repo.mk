# Repository-owned implementation of the make-v2 execution phases, plus the
# product and governance wrappers this repository has always exposed.
#
# CI parity:
#   setup     -> "Sync the locked environment" in ci.yml and deep-plan.yml
#   validate  -> inventory, hygiene, plugin-config and Cursor-rule checks
#   check     -> ruff lint, ruff format --check and strict mypy
#   test-fast -> the four contract-shape suites ci.yml runs on a pull request
#   test      -> the whole pytest suite deep-plan.yml runs on an apply
#
# Core runs each phase as its own make process, so every recipe resolves the
# environment it needs rather than relying on state a previous phase exported.
# The help recipe lives in the facade: it lists every target below that carries
# a `## ` description.
GOV_ROOT ?= $(HOME)/.cursor-governance
OPEN_PR ?= 0

ifneq ($(wildcard $(CURDIR)/.venv/bin/python),)
PYTHON := $(CURDIR)/.venv/bin/python
endif
PYTHON ?= python3

.PHONY: repo-setup repo-validate repo-check repo-test-fast repo-test \
	install-dev lint typecheck inventory-check hygiene-check schema-check \
	check-config reconcile-config check-rules render-rules \
	compile-check verify ci pr-check build regenerate-manifest \
	gov-pr-check gov-pr gov-start gov-wiring-check

repo-setup: ## Create .venv and install the library, its development extra and the runtime pins
	@test -x "$(PYTHON)" || $(PYTHON) -m venv .venv
	@.venv/bin/python -m pip install --quiet --upgrade pip
	@.venv/bin/python -m pip install --quiet -e ".[dev]"
	@.venv/bin/python -m pip install --quiet -r requirements-repo-runtime.txt

repo-validate: ## Validate the inventory, source hygiene, plugin config and generated rules
	$(PYTHON) scripts/inventory_check.py
	$(PYTHON) scripts/repo_hygiene_audit.py
	$(PYTHON) scripts/reconcile_plugin_config.py --check
	$(PYTHON) scripts/render_cursor_rules.py --check
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m compileall -q src tests tools scripts

repo-check: ## Ruff lint, ruff format check and strict mypy for the library package
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .
	$(PYTHON) -m mypy src

repo-test-fast: ## Bounded pull-request test selection
	$(PYTHON) -m pytest -q -p no:cacheprovider \
		tests/test_canonical.py \
		tests/test_json_schemas.py \
		tests/test_model_integrity.py \
		tests/test_registry.py

repo-test: ## Whole pytest suite
	$(PYTHON) -m pytest -q -p no:cacheprovider

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

# Local repository policy from the vendored Core tooling. Publication verbs
# (push, pr) are deliberately absent: Git publication belongs to
# Cursor-Governance, never to the repository-execution facade.
L9_REPO = $(PYTHON) -m tools.l9_repo --workspace "$(CURDIR)"

.PHONY: doctor change-policy agent-check status clean reconcile

doctor: ## Check the workspace prerequisites the vendored Core tooling expects
	@$(L9_REPO) doctor

change-policy: ## Report the change policy for the current diff
	@$(L9_REPO) change-policy

agent-check: ## Run the evidence-bearing agent check
	@$(L9_REPO) agent-check

status: ## Show the repository-execution status
	@$(L9_REPO) status

clean: ## Remove generated residue from the workspace
	@$(L9_REPO) clean

reconcile: ## Reconcile the vendored Core tooling against this workspace
	@$(L9_REPO) reconcile
