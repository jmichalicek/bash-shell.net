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

ruff-check:
	ruff check .

isort-check:
	isort --check -q --sg **/migrations/* bash_shell_net/

isort:
	isort -q --sg **/migrations/* bash_shell_net/

black:
	black .

black-check:
	black --check . --diff

lint: ruff-check black-check isort-check djhtml-check mypy

pyupgrade:
	find ./ -path '**/.venv' -prune -o -path node_modules -prune -o -path '**/migrations' -prune -o -wholename '*/*.py' -exec pyupgrade --py313-plus '{}' +

django-upgrade:
	find . -path '**/.venv' -prune -o -path node_modules -prune -o -path '**/migrations' -prune -o -wholename '*/*.py' -exec django-upgrade --target-version=5.2 '{}' +

test:
	python manage.py test --parallel --failfast
