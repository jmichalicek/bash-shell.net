.PHONY: requirements.txt

setup-and-run:	install migrate run

venv:
	 uv venv

pip-sync:
	uv sync --locked

npm-ci:
	npm ci

run:
	python manage.py runserver 0.0.0.0:8000

install: venv pip-sync npm-ci

requirements.txt:
	# See https://stackoverflow.com/questions/58843905/what-is-the-proper-way-to-decide-whether-to-allow-unsafe-package-versions-in-pip
	# about allow-unsafe. In this case, to pin setuptools.
	pip-compile requirements.in requirements.dev.in --generate-hashes --upgrade --allow-unsafe --resolver=backtracking --output-file=requirements.txt
	# pip-compile requirements.dev.in --generate-hashes --upgrade --allow-unsafe --resolver=backtracking

djhtml:
	find . -path ./.venv -prune -o -path node_modules -prune -o -wholename '*/templates*.html' -exec djhtml -t2 '{}' +

djhtml-check:
	find . -path ./.venv -prune -path ./node_modules -prune -o -wholename '*/templates*.html' -exec djhtml -t2 -c '{}' +

mypy:
	mypy --check-untyped-defs .

ruff:
	ruff check . --fix

ruff-fix: ruff-check-fix ruff-format

ruff-check:
	ruff check .

ruff-format:
	ruff format .

ruff-format-check:
	ruff format --diff .

ruff-check-fix:
	ruff check --fix .

lint: ruff-check ruff-format-check djhtml-check mypy

format: ruff-check-fix ruff-format djhtml

pyupgrade:
	find ./ -path '**/.venv' -prune -o -path node_modules -prune -o -path '**/migrations' -prune -o -wholename '*/*.py' -exec pyupgrade --py313-plus '{}' +

django-upgrade:
	find . -path '**/.venv' -prune -o -path node_modules -prune -o -path '**/migrations' -prune -o -wholename '*/*.py' -exec django-upgrade --target-version=5.2 '{}' +

test:
	python manage.py test --parallel --failfast
