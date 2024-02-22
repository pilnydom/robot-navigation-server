PYTHON = python3
SRC_DIR = src
TEST_DIR = tests
PORT = 3999

all: run test

clean:
	@echo "Cleaning up..."
	rm -rf $(SRC_DIR)/__pycache__

run:
	@echo "Running the project..."
	$(PYTHON) $(SRC_DIR)/__init__.py $(PORT)

.DEFAULT_GOAL := run
.PHONY: all clean run test