.PHONY: requirements.txt

setup-and-run:	install migrate run

venv:
	 python -m venv .venv
	 pip install pip -U
	 pip install pip-tools wheel

pip-sync:
	pip-sync requirements.txt

npm-ci:
	npm ci

run:
	honcho start

install: venv pip-sync npm-ci

migrate:
	python manage.py migrate

requirements.txt:
	# See https://stackoverflow.com/questions/58843905/what-is-the-proper-way-to-decide-whether-to-allow-unsafe-package-versions-in-pip
	# about allow-unsafe. In this case, to pin setuptools.
	pip-compile requirements.in requirements.dev.in --generate-hashes --upgrade --allow-unsafe --resolver=backtracking --output-file=requirements.txt
	# pip-compile requirements.dev.in --generate-hashes --upgrade --allow-unsafe --resolver=backtracking 

install:
	 pip-sync requirements.txt --pip-args '--no-cache-dir --no-deps'

djhtml:
	find . -path ./.venv -prune -o -path node_modules -prune -o -wholename '*/templates*.html' -exec djhtml -t2 '{}' +

djhtml-check:
	find . -path ./.venv -prune -path ./node_modules -prune -o -wholename '*/templates*.html' -exec djhtml -t2 -c '{}' +

mypy:
	mypy --check-untyped-defs .

ruff:
	ruff check .

isort-check:
	isort --check -q --sg **/migrations/* bash_shell_net/

lint: ruff isort-check djhtml-check mypy

pyupgrade:
	find ./ -path '**/.venv' -prune -o -path node_modules -prune -o -path '**/migrations' -prune -o -wholename '*/*.py' -exec pyupgrade --py39-plus '{}' +

django-upgrade:
	find . -path '**/.venv' -prune -o -path node_modules -prune -o -path '**/migrations' -prune -o -wholename '*/*.py' -exec django-upgrade --target-version=3.2 '{}' +

test:
	python manage.py test --parallel --failfast
