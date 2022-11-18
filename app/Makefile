.PHONY: requirements.txt

setup-and-run:	install migrate run

venv:
	 python -m venv .venv
	 pip install pip -U
	 pip install pip-tools wheel

pip-sync:
	pip-sync requirements.txt requirements.dev.txt

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
	pip-compile requirements.in --generate-hashes --upgrade --allow-unsafe
	pip-compile requirements.dev.in --generate-hashes --upgrade --allow-unsafe

install:
	 pip-sync requirements.txt requirements.dev.txt --pip-args '--no-cache-dir --no-deps'

djhtml:
	find . -path ./.venv -prune -o -path node_modules -prune -o -wholename '*/templates*.html' -exec djhtml -t2 -i '{}' +

djhtml-check:
	find . -path ./.venv -prune -path ./node_modules -prune -o -wholename '*/templates*.html' -exec djhtml -t2 -c '{}' +

mypy:
	mypy .

flake8:
	flake8 . --select=E9,F63,F7,F82 --show-source --exclude="documentation, .venv, node_modules, media, .parcel-cache, .git, __pycache__, webpack_assets"
	flake8 --ignore=E501,E123,E126,E128,E124,E133,W503,E121 --max-line-length=120 --exclude="documentation, .venv, node_modules, media, .parcel-cache, .git, __pycache__, webpack_assets, migrations" bash_shell_net/

isort-check:
	isort --check -q --sg **/migrations/* bash_shell_net/

lint: flake8 isort-check djhtml-check mypy

pyupgrade:
	find ./ -path '**/.venv' -prune -o -path node_modules -prune -o -path '**/migrations' -prune -o -wholename '*/*.py' -exec pyupgrade --py39-plus '{}' +

django-upgrade:
	find . -path '**/.venv' -prune -o -path node_modules -prune -o -path '**/migrations' -prune -o -wholename '*/*.py' -exec django-upgrade --target-version=3.2 '{}' +

test:
	python manage.py test --parallel --failfast