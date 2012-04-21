# Makefile to help automate tasks
WD := $(shell pwd)
PY := bin/python
PIP := bin/pip
PEP8 := bin/pep8
NOSE := bin/nosetests


# ###########
# Tests rule!
# ###########
.PHONY: test
test: venv $(NOSE)
	$(NOSE) --with-id -s src/tests

$(NOSE):
	$(PY) setup.py test

.PHONY: regression_test
regression_test:
	$(PY) src/tests/regression.py
	$(PY) -m webbrowser src/tests/regression_test_output/index.html


# #######
# INSTALL
# #######
.PHONY: all
all: venv develop

venv: bin/python
bin/python:
	virtualenv .

.PHONY: clean_venv
clean_venv:
	rm -rf bin include lib local man share

.PHONY: develop
develop: lib/python*/site-packages/readability_lxml.egg-link
lib/python*/site-packages/readability_lxml.egg-link:
	$(PY) setup.py develop


# ###########
# Development
# ###########
.PHONY: clean_all
clean_all: clean_venv
	if [ -d dist ]; then \
		rm -r dist; \
    fi


# ###########
# Deploy
# ###########
.PHONY: dist
dist:
	$(PY) setup.py sdist

.PHONY: upload
upload:
	$(PY) setup.py sdist upload

.PHONY: version_update
version_update:
	$(EDITOR) setup.py src/readability_lxml/__init__.py
