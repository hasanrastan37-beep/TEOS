.PHONY: build run test lint backup

build:
docker compose build

run:
docker compose up -d

test:
pytest tests/ -v

lint:
flake8 src/

backup:
./scripts/backup.sh

restore:
./scripts/restore.sh $(FILE)
