.PHONY: requirements.txt

venv:
	 python -m venv app/.venv
	 pip install pip==21.2.4
	 pip install pip-tools

dev:
	docker compose --profile dev run --service-ports django /bin/bash

shell:
	docker compose --profile dev exec django /bin/bash