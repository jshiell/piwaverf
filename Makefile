.DEFAULT: help
.PHONY: clean-pyc help init

PROJECT_NAME=piwaverf
VENV_NAME?=venv
VENV_ACTIVATE=. $(VENV_NAME)/bin/activate
PYTHON=${VENV_NAME}/bin/python3

ifeq ($(PREFIX),)
    PREFIX := /usr/local
endif

help:
	@echo "make init"
	@echo "    ensure venv is set up, install dependencies"

clean: clean-pyc

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

venv: $(VENV_NAME)/bin/activate
$(VENV_NAME)/bin/activate: setup.py
	test -d $(VENV_NAME) || virtualenv -p python3 $(VENV_NAME)
	${PYTHON} -m pip install -U pip
	${PYTHON} -m pip install -e .
	touch $(VENV_NAME)/bin/activate

init: venv
	pip3 install -r requirements.txt

install: clean-pyc
	pip3 install -r requirements.txt
	install -t "$(DESTDIR)$(PREFIX)/$(PROJECT_NAME)/" -D piwaverf/*
	install -m 644 "piwaverf.service" "/lib/systemd/system/"
