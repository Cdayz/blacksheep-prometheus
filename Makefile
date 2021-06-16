deps:
	pip install -U pip poetry
	touch deps

.PHONY: install
install: deps
	poetry install

.PHONY: build
build: deps
	poetry build

isort-check: deps
	poetry run isort blacksheep_prometheus --check-only

flake8-lint: deps
	poetry run flake8 blacksheep_prometheus

.PHONY: tests
tests: deps
	poetry run pytest

publish-to-pypi: deps
	poetry publish --build --username ${PYPI_USERNAME} --password ${PYPI_PUBLISH_TOKEN}
