.PHONY: requirements.txt

setup-and-run:	venv install migrate run

venv:
	 python -m venv app/.venv
	 pip install pip==21.2.4
	 pip install pip-tools

run:
	honcho start

migrate:
	python app/manage.py migrate

dev:
	docker compose run --service-ports django /bin/bash

docker_django:
	docker compose exec django python manage.py runserver 0.0.0.0:8000

docker_migrate:
	docker compose exec django python manage.py migrate ${args}

docker_test:
	docker compose exec django python manage.py test ${args}

requirements.txt:
	# See https://stackoverflow.com/questions/58843905/what-is-the-proper-way-to-decide-whether-to-allow-unsafe-package-versions-in-pip
	# about allow-unsafe. In this case, to pin setuptools.
	pip-compile app/requirements.in --generate-hashes --upgrade --allow-unsafe
	pip-compile app/requirements.dev.in --generate-hashes --upgrade --allow-unsafe

install:
	 pip-sync app/requirements.txt app/requirements.dev.txt --pip-args '--no-cache-dir --no-deps'

djhtml:
	find . -path */.venv -prune -o -path node_modules -prune -o -wholename '*/templates*.html' -exec djhtml -t2 -i '{}' +

djhtml-check:
	find . -path */.venv -prune -path node_modules -prune -o -wholename '*/templates*.html' -exec djhtml -t2 -c '{}' +
