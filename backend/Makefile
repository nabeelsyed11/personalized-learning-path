.PHONY: seed run

# Initialize virtual environment and install dependencies
init:
	python -m venv .venv
	.venv\Scripts\activate && \
	pip install --upgrade pip && \
	pip install -r requirements.txt

# Seed the database with initial data
seed:
	python -m scripts.seed_db

# Run the FastAPI development server
run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
test:
	pytest tests/ -v

# Format code with black
format:
	black .

# Check code style
lint:
	black --check .
	flake8

# Run all checks
check: lint test
