docker rm bsdev
docker build --rm -f Dockerfile.dev -t bash-shell-net:dev .

set code_dir=%CD%

docker run -ti --rm ^
    -v %code_dir%:/home/developer/bash-shell.net/ ^
    -v bsdev_virtulaenvs:/home/developer/.local/share/virtualenvs ^
    --name=bsdev ^
    -p 8000:8000 ^
    bash-shell-net:dev bash -c "bash /home/developer/docker_entrypoints/dev_entrypoint.sh"
