.PHONY: start stop logs backup migrate dev

start:
	docker-compose up -d

stop:
	docker-compose down

logs:
	docker-compose logs -f

backup:
	python -c "import shutil, time; shutil.copytree('data', f'data/backups/backup_{int(time.time())}')"

migrate:
	python -c "from database.features_schema import init_features_schema; init_features_schema()"

dev:
	uvicorn web.backend.app.main:app --reload --port 8000