init:
    python -m venv venv
    source venv/bin/activate && pip install -r requirements.txt

test:
    pytest tests/ -v

run:
    python -m src.main

lint:
    flake8 src/ tests/ 