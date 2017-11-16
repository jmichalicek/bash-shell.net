#!/bin/sh

docker rm bsdev
docker build --rm -f Dockerfile.dev -t bash-shell-net:dev .
docker run -ti --rm -v `pwd`:/home/developer/bash-shell.net/ \
    -v bsdev_virtulaenvs:/home/developer/.local/share/virtualenvs \
    --name=bsdev \
    -p 8000:8000 \
    bash-shell-net:dev bash -c 'bash /home/developer/docker_entrypoints/dev_entrypoint.sh'
