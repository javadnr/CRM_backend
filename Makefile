up:
	docker compose up --build

down:
	docker compose down

restart:
	docker compose down && docker compose up --build

logs:
	docker compose logs -f

api:
	docker compose exec api bash

worker:
	docker compose exec worker bash

db:
	docker compose exec db psql -U postgres -d crm

migrate:
	docker compose exec api alembic upgrade head

makemigration:
	docker compose exec api alembic revision --autogenerate -m "$(msg)"

clean:
	docker compose down -v\

test:
	pytest