.DEFAULT_GOAL := help
VENV = venv

.PHONY: help
help: ## Print the help message
	@awk 'BEGIN {FS = ":.*?## "} /^[0-9a-zA-Z_-]+:.*?## / {printf "\033[36m%s\033[0m : %s\n", $$1, $$2}' $(MAKEFILE_LIST) | \
		sort | \
		column -s ':' -t

.PHONY: clean
clean: ## Clean all generated resources
	@git clean -X -d -f

venv:
	@virtualenv -p python3 $(VENV) && \
		. $(VENV)/bin/activate && \
		pip install -r requirements.txt

.PHONY: update
update: ## Update the requirements
	@pip-compile --no-header --generate-hashes -o requirements.txt requirements.in

.PHONY: check
check: venv ## Run the linters
	@. $(VENV)/bin/activate && \
		flake8 it_test

.PHONY: run
run: venv check ## Run the integration tests
	@. $(VENV)/bin/activate && \
		./it-test
