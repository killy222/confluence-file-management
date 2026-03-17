DC := docker compose

.PHONY: up up-build down restart stop start ps logs backend-logs frontend-logs app-shell test migrate

up:
	$(DC) up -d

up-build:
	$(DC) up -d --build

down:
	$(DC) down

restart:
	$(DC) down
	$(DC) up -d

stop:
	$(DC) stop

start:
	$(DC) start

ps:
	$(DC) ps

logs:
	$(DC) logs -f

backend-logs:
	$(DC) logs -f backend

frontend-logs:
	$(DC) logs -f frontend

app-shell:
	$(DC) --profile tools run --rm app bash

test:
	$(DC) --profile tools run --rm app pytest tests/ -v

migrate:
	$(DC) run --rm -w /app/backend backend python -m alembic upgrade head

