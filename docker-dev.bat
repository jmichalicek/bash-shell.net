docker rm bsdev
docker build --rm -f docker/Dockerfile.dev -t bash-shell-net:dev .
docker run -ti --rm -v %CD%:/home/developer/bash-shell.net/ ^
    -v bsdev_pyenv:/home/developer/.pyenv ^
    --name=bsdev ^
    -p 8000:8000 ^
    bash-shell-net:dev ^
    bash -c 'bash $HOME/docker_entrypoints/dev_entrypoint.sh'
