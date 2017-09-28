#!/bin/sh

sudo service postgresql start
psql -U postgres -h 127.0.0.1 -tAc "SELECT 1 FROM pg_roles WHERE rolname='developer'" | grep -q 1 || sudo -u postgres createuser -s developer
psql -U postgres -h 127.0.0.1 -tAc "SELECT 1 from pg_database WHERE datname='bsdev'" | grep -q 1 || sudo -u postgres createdb bsdev -O developer
sudo chown developer:developer /home/developer/.local/share/virtualenvs/
cd ~/bash-shell.net/ && pipenv install --dev && pipenv run python manage.py migrate
exec $SHELL
