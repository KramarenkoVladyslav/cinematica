.PHONY: build up down createsuperuser load-fixtures

build:
	docker compose up --build

up:
	docker compose up

down:
	docker compose down -v --remove-orphans

createsuperuser:
	docker compose exec backend python manage.py createsuperuser

load-fixtures:
	docker compose exec backend python manage.py loaddata fixtures/movies/categories.json
	docker compose exec backend python manage.py loaddata fixtures/movies/genres.json
	docker compose exec backend python manage.py loaddata fixtures/movies/countries.json
	docker compose exec backend python manage.py loaddata fixtures/movies/years.json
	docker compose exec backend python manage.py loaddata fixtures/movies/movies.json
