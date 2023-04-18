# These can be overidden with env vars.
REGISTRY ?= konveyor
IMAGE_NAME ?= dgi
IMAGE_TAG ?= 1.0.0
IMAGE ?= $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)
LATEST ?= $(REGISTRY)/$(IMAGE_NAME):latest
PLATFORM ?= "linux/amd64,linux/arm64"

.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

.PHONY: all
all: help

##@ Development

.PHONY: env
venv: ## Create a Python virtual environment
	$(info Creating Python 3 virtual environment...)
	python3 -m venv .venv
	$(info To use: source .venv/bin/activate)

.PHONY: install
install: ## Install development version of DGI
	$(info Installing development version of DGI...)
	sudo pip install -e '.[dev]'

.PHONY: lint
lint: ## Run the linter
	$(info Running linting...)
	flake8 dgi --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 dgi --count --max-complexity=10 --max-line-length=127 --statistics
	pylint dgi --disable=R0801,R0913,R0914 --max-line-length=127 --max-args=6 --ignore=sqlparse.py

.PHONY: test
test: ## Run the unit tests
	$(info Running tests...)
	nosetests --with-spec --spec-color

##@ Runtime

.PHONY: neo4j
neo4j: ## Start Neo4J in Docker
	$(info Starting Neo4J server...)
	export NEO4J_BOLT_URL="neo4j://neo4j:konveyor@localhost:7687"
	docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH="neo4j/konveyor" neo4j:4.4.17

.PHONY: build
build: ## Build a Docker image for running DGI
	$(info Building multi-platform Docker image...)
	-docker buildx create --name=qemu
	docker buildx use qemu 
	docker buildx build --pull --platform=$(PLATFORM) --tag $(IMAGE) --tag $(LATEST) --push .
