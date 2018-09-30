rem because mingw make refuses to play nicely on windows
docker-compose run --service-ports django /usr/bin/zsh -ic "pipenv shell"
