.PHONY: requirements.txt

venv:
	 python -m venv app/.venv
	 pip install -U pip
	 pip install pip-tools

dev:
	docker compose run --service-ports django /bin/bash

shell:
	docker compose exec django /bin/bash
