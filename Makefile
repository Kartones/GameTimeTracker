.PHONY: venv _build build export

VENV_DIR = .venv
PYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip
PYINSTALLER = $(VENV_DIR)/bin/pyinstaller

venv:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv $(VENV_DIR); \
		echo "Installing dependencies..."; \
		$(PIP) install --upgrade pip; \
		$(PIP) install -r requirements.txt; \
	else \
		echo "Virtual environment already exists"; \
	fi

_build: venv
	@echo "Building executable with PyInstaller..."
	$(PYINSTALLER) --onefile gtt.py

build: _build
	@echo "Cleaning up intermediate build artifacts..."
	rm -rf build __pycache__ *.spec

export: venv
	@echo "Exporting game time data..."
	$(PYTHON) export_to_fg_game_time.py queries
