.PHONY: up down logs test api worker

up:
	docker compose up --build

down:
	docker compose down -v

logs:
	docker compose logs -f api worker

test:
	docker compose exec api pytest -q

api:
	uvicorn app.main:app --reload

worker:
	celery -A app.workers.celery_app.celery_app worker --loglevel=info
