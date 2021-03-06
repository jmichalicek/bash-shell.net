.PHONY: requirements.txt

setup-and-run:	setup migrate run

venv:
	 python -m venv .venv
	 pip install pip==21.0.1

run:
	python manage.py runserver 0.0.0.0:8000

setup:
	pipenv sync

migrate:
	python manage.py migrate

dev:
	docker-compose run --service-ports django /bin/bash

docker_django:
	docker-compose exec django python manage.py runserver 0.0.0.0:8000

docker_migrate:
	docker-compose exec django python manage.py migrate ${args}

docker_test:
	docker-compose exec django python manage.py test ${args}

requirements.txt:
	# See https://stackoverflow.com/questions/58843905/what-is-the-proper-way-to-decide-whether-to-allow-unsafe-package-versions-in-pip
	# about allow-unsafe. In this case, to pin setuptools.
	pip-compile requirements.in --generate-hashes --upgrade --allow-unsafe
	pip-compile requirements.dev.in --generate-hashes --upgrade --allow-unsafe
