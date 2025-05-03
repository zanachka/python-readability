# Makefile to help automate tasks
WD := $(shell pwd)
PY := .venv/bin/python
PIP := .venv/bin/pip
PEP8 := .venv/bin/pep8
NOSE := .venv/bin/nosetests
TWINE := .venv/bin/twine

# ###########
# Tests rule!
# ###########
.PHONY: test
test: venv develop $(NOSE)
	$(NOSE) --with-id -s tests

$(NOSE): setup

# #######
# INSTALL
# #######
.PHONY: all
all: setup develop

venv: .venv/bin/python

setup: venv
	$(PIP) install -r requirements-dev.txt | grep -v "already satisfied" || true

.venv/bin/python:
	test -d .venv || which python3 && python3 -m venv .venv || virtualenv .venv

.PHONY: clean
clean:
	rm -rf .venv

develop: .venv/lib/python*/site-packages/readability-lxml.egg-link

.venv/lib/python*/site-packages/readability-lxml.egg-link:
	$(PY) setup.py develop


# ###########
# Development
# ###########
.PHONY: clean_all
clean_all: clean_venv

.PHONY: build
build:
	poetry build

# ###########
# Deploy
# ###########
.PHONY: dist
dist:
	$(PY) -m pip install wheel
	$(PY) setup.py sdist bdist_wheel
	$(TWINE) check dist/*

.PHONY: upload
upload:
	$(TWINE) upload dist/*

.PHONY: bump
bump:
	$(EDITOR) readability/__init__.py
	$(eval VERSION := $(shell grep "__version__" readability/__init__.py | cut -d'"' -f2))
	# fix first occurrence of version in pyproject.toml
	sed -i '0,/version = ".*"/s//version = "$(VERSION)"/' pyproject.toml
	git commit -m "Bump version to $(VERSION)" pyproject.toml readability/__init__.py
	git tag $(VERSION)
	git push --tags
