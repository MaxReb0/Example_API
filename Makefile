SHELL := /bin/bash
.ONESHELL:
.PHONY: clean clean-test clean-pyc clean-build
.DEFAULT_GOAL := setup

setup: venv activate-venv install-dev install

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr ldist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

venv:
	@if [ ! -d .venv ]; then echo "Creating virtualenv"; python3 -m venv .venv; fi
	@echo "virtualenv created"
	
activate-venv:
	@echo "Activating virtual env"
	. .venv/bin/activate

install:
	@echo "Installing package"
	pip install .

install-dev:
	@echo "Installing development requirements"
	pip install --upgrade pip
	pip install -e ".[dev]"

test:
	pytest

run:
	@flask run
