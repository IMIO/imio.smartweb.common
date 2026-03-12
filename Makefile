#!/usr/bin/make
.PHONY: buildout cleanall help release test start

help: ## Display this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

bin/pip:
	python3.12 -m venv .
	touch $@

bin/buildout: bin/pip
	./bin/pip install -r requirements.txt
	touch $@

buildout: bin/buildout ## Install dependencies with buildout
	./bin/buildout -t 7

release: ## Run full release with uvx zest.releaser
	uvx --from zest.releaser fullrelease

test: buildout ## Run tests
	./bin/test

start: buildout ## Start the development server
	ALLOWED_DISTRIBUTIONS=classic ./bin/instance fg

cleanall: ## Clean development environment
	rm -rf bin develop-eggs downloads include lib lib64 parts .installed.cfg .mr.developer.cfg bootstrap.py parts/omelette local share
