.PHONY: requirements.txt

venv:
	 python -m venv app/.venv
	 pip install pip==21.2.4
	 pip install pip-tools

dev:
	docker compose run --service-ports django /bin/bash

docker_django:
	docker compose exec django python manage.py runserver 0.0.0.0:8000

docker_migrate:
	docker compose exec django python manage.py migrate ${args}

docker_test:
	docker compose exec django python manage.py test ${args}

shell:
	docker compose exec django /bin/bash