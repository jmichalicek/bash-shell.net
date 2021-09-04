FROM python:3.9.7-bullseye AS dev
LABEL maintainer="Justin Michalicek <jmichalicek@gmail.com>"
ENV PYTHONUNBUFFERED=1 DEBIAN_FRONTEND=noninteractive

RUN wget -q https://www.postgresql.org/media/keys/ACCC4CF8.asc -O - | apt-key add - \
    && echo "deb http://apt.postgresql.org/pub/repos/apt/ bullseye-pgdg main" >> /etc/apt/sources.list.d/pgdg.list

RUN curl -sL https://deb.nodesource.com/setup_16.x | bash

RUN apt-get update && apt-get install -y --allow-unauthenticated \
  software-properties-common \
  sudo \
  vim \
  telnet \
  postgresql-client \
  nodejs \
  bash-completion \
  && apt-get autoremove && apt-get clean

RUN pip install pip==21.2.4
RUN useradd -ms /bin/bash -d /django django && echo "django ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
USER django
ENV HOME=/django/ \
    PATH=/django/bash-shell.net/app/.venv/bin:/django/.local/bin:/django/bash-shell.net/node_modules/.bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    PYTHONIOENCODING=utf-8
EXPOSE 8000

FROM dev AS build
# need the venv not in /app/ so that we can relocate it
RUN mkdir -p /django/bash-shell.net/ && python -m venv /django/bash-shell.net/.venv
ENV PATH=/django/bash-shell.net/.venv/bin:$PATH
# https://stackoverflow.com/a/28210626
# python -m venv only copies the bundled pip, even if you've done a pip install -U pip to get
# a newer version installed, so update it in the virtualenv
RUN pip install pip==21.2.3
RUN pip install pip-tools
COPY --chown=django ./app/requirements.txt ./app/requirements.dev.txt /django/bash-shell.net/
WORKDIR /django/bash-shell.net/
# I am being lazy and installing dev requirements here to make it easy to run my tests on the prod image
# since they don't add much size
RUN pip-sync requirements.txt requirements.dev.txt --pip-args '--no-cache-dir --no-deps'
COPY --chown=django ./app/package.json ./app/package-lock.json /django/bash-shell.net/
RUN npm ci
RUN mkdir -p /django/bash-shell.net/config/static
COPY --chown=django ./app/config/static/ /django/bash-shell.net/config/static
COPY --chown=django ./app/webpack.config.js ./.stylelintrc.json /django/bash-shell.net/
RUN webpack build --mode=production --stats-children

COPY --chown=django ./app /django/bash-shell.net/
RUN DJANGO_SETTINGS_MODULE=config.settings.production python manage.py collectstatic -l --noinput -i *.scss -i *.map -i index.js
RUN rm -rf webpack_assets ./config/static/scss/ ./config/static/js/index.js node_modules
COPY --chown=django ./wait-for-it.sh /django/bash-shell.net/wait-for-it.sh

# Production image
FROM python:3.9.7-slim-bullseye AS prod
RUN useradd -ms /bin/bash -d /django django
# Instead of copying the whole dir, just copy the known needed bits
COPY --chown=django --from=build /django/bash-shell.net /django/bash-shell.net/
USER django
ENV DJANGO_SETTINGS_MODULE=config.settings.production \
    HOME=/django/.local/bin:/django PATH=/django/bash-shell.net/.venv/bin:$PATH \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    PYTHONIOENCODING=utf-8 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive
WORKDIR /django/bash-shell.net/
EXPOSE 8000
