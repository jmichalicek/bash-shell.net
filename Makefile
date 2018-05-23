dev:
	docker-compose run --service-ports django

docker_build:
	docker build --rm -f Dockerfile.dev -t bash-shell-net:dev .

docker_django:
	docker-compose exec django pipenv run python manage.py runserver 0.0.0.0:8000

docker_migrate:
	docker-compose exec django pipenv run python manage.py migrate ${args}

docker_pip:
	docker-compose exec django pipenv install --dev --three

docker_test:
	docker-compose exec django pipenv run python manage.py test ${args}
