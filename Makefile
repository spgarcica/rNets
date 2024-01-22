VENV_NAME := .venv
PYTHON := python3

.PHONY: venv install test pyright clean

all: venv install test pyright

venv:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		$(PYTHON) -m venv $(VENV_NAME); \
	fi

install:
	$(VENV_NAME)/bin/pip install -e .

test:
	$(VENV_NAME)/bin/python -m unittest discover -s tests -p "*_test.py"

pyright:
	$(VENV_NAME)/bin/pip install pyright
	$(VENV_NAME)/bin/pyright src/rnets

clean:
	rm -rf $(VENV_NAME)
	find . -name "*.egg-info" -exec rm -rf {} +
	find . -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -exec rm -f {} +
