FROM python:3.9.6-buster AS dev
LABEL maintainer="Justin Michalicek <jmichalicek@gmail.com>"
ENV PYTHONUNBUFFERED 1

RUN wget -q https://www.postgresql.org/media/keys/ACCC4CF8.asc -O - | apt-key add - \
    && echo "deb http://apt.postgresql.org/pub/repos/apt/ buster-pgdg main" >> /etc/apt/sources.list.d/pgdg.list

RUN curl -sL https://deb.nodesource.com/setup_16.x | bash

RUN DEBIAN_FRONTEND=noninteractive apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --allow-unauthenticated \
  software-properties-common \
  sudo \
  vim \
  telnet \
  postgresql-client \
  nodejs \
  bash-completion \
  && apt-get autoremove && apt-get clean

RUN pip install pip==21.1.2
RUN useradd -ms /bin/bash -d /django django && echo "django ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
USER django
ENV HOME=/django/ \
    PATH=/django/bash-shell.net/.venv/bin:/django/.local/bin:/django/bash-shell.net/node_modules/.bin:$PATH \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    PYTHONIOENCODING=utf-8
EXPOSE 8000

FROM dev AS build
RUN mkdir /django/bash-shell.net/ && python -m venv /django/bash-shell.net/.venv
# https://stackoverflow.com/a/28210626
# python -m venv only copies the bundled pip, even if you've done a pip install -U pip to get
# a newer version installed, so update it in the virtualenv
RUN pip install pip==21.1.2
RUN pip install pip-tools
# TODO: Consider moving requirements files, package*.json, and virtualenv inside the app dir
# I prefer having those at the root, but they also make sense in there and provide a clean
# separation for using this same layout as a monorepo (which I won't do with this) and
# makes the image build simpler. Now I have to muck about with paths while copying and
# try to keep a bunch of stuff straight.
COPY --chown=django ./requirements.txt ./requirements.dev.txt /django/bash-shell.net/
WORKDIR /django/bash-shell.net/
# I am being lazy and installing dev requirements here to make it easy to run my tests on the prod image
# since they don't add much size
RUN pip-sync requirements.txt requirements.dev.txt --pip-args '--no-cache-dir --no-deps'
COPY --chown=django ./package.json ./package-lock.json /django/bash-shell.net/
RUN npm ci
RUN mkdir -p /django/bash-shell.net/app/config/static
COPY --chown=django ./app/config/static/ /django/bash-shell.net/app/config/static
COPY --chown=django ./webpack.config.js ./.stylelintrc.json /django/bash-shell.net/
RUN webpack build --mode=production --stats-children

COPY --chown=django ./app /django/bash-shell.net/app
WORKDIR /django/bash-shell.net/app/
RUN DJANGO_SETTINGS_MODULE=config.settings.production python manage.py collectstatic -l --noinput -i *.scss
RUN rm -rf webpack_assets ./config/static/scss/
COPY --chown=django ./wait-for-it.sh /django/bash-shell.net/app/wait-for-it.sh

# Production image
FROM python:3.9.6-slim-buster AS prod
RUN useradd -ms /bin/bash -d /django django
COPY --chown=django --from=build /django/bash-shell.net/app /django/bash-shell.net
COPY --chown=django --from=build /django/bash-shell.net/.venv/ /django/bash-shell.net/.venv
USER django
ENV DJANGO_SETTINGS_MODULE=config.settings.production HOME=/django/.local/bin:/django PATH=/django/bash-shell.net/.venv/bin:$PATH LC_ALL=C.UTF-8 LANG=C.UTF-8 PYTHONIOENCODING=utf-8
WORKDIR /django/bash-shell.net/
EXPOSE 8000
