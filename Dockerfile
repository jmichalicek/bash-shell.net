ARG PYTHON_VERSION=3.13.3
ARG DISTRO=bookworm
FROM python:$PYTHON_VERSION-$DISTRO AS dev
LABEL maintainer="Justin Michalicek <jmichalicek@gmail.com>"
ENV PYTHONUNBUFFERED=1 DEBIAN_FRONTEND=noninteractive PYTHONFAULTHANDLER=1

RUN apt-get update && apt-get upgrade -y \
  && apt-get install -y --allow-unauthenticated \
  lsb-release \
  postgresql-common \
  bash-completion \
  software-properties-common \
  sudo \
  vim \
  telnet \
  && apt-get autoremove \
  && apt-get clean

RUN curl -sL https://deb.nodesource.com/setup_20.x | bash
RUN YES=1 /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh
RUN apt-get update && apt-get install -y --allow-unauthenticated \
  postgresql-client \
  nodejs \
  && apt-get autoremove && apt-get clean
RUN pip install -U pip
RUN useradd -ms /bin/bash -d /django django && echo "django ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
USER django
ADD --chown=django https://astral.sh/uv/0.7.5/install.sh /django/uv-installer.sh
RUN sh /django/uv-installer.sh && rm /django/uv-installer.sh
ENV HOME=/django/ \
    PATH=/django/bash-shell.net/app/.venv/bin:/django/.local/bin:/django/bash-shell.net/node_modules/.bin:$PATH \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    PYTHONIOENCODING=utf-8

FROM dev AS build
RUN mkdir -p /django/bash-shell.net/ && uv venv /django/bash-shell.net/.venv
ENV PATH=/django/bash-shell.net/.venv/bin:$PATH
WORKDIR /django/bash-shell.net/
# need the venv not in /app/ so that we can relocate it
COPY ./app/pyproject.toml /django/bash-shell.net/pyproject.toml
COPY ./app/uv.lock /django/bash-shell.net/uv.lock
# I am being lazy and installing dev requirements here to make it easy to run my tests on the prod image
# since they don't add much size
RUN uv sync --locked --no-cache
COPY --chown=django ./app/package.json ./app/package-lock.json /django/bash-shell.net/
RUN npm ci
RUN mkdir -p /django/bash-shell.net/config/static
COPY --chown=django ./app/config/static/ /django/bash-shell.net/config/static
COPY --chown=django ./app/webpack.config.js ./.stylelintrc.json /django/bash-shell.net/
RUN webpack build --mode=production --stats-children

COPY --chown=django ./app /django/bash-shell.net/
# Cannot ignore *.map anymore, wagtail has changed things so their *.map files get referenced and so need to exist
RUN DJANGO_SETTINGS_MODULE=config.settings.production python manage.py collectstatic -l --noinput -i *.scss -i index.js
RUN rm -rf webpack_assets ./config/static/scss/ ./config/static/js/index.js node_modules
COPY --chown=django ./.flake8 /django/bash-shell.net/.flake8
RUN ls -a

# Production image
FROM python:$PYTHON_VERSION-slim-$DISTRO AS prod
LABEL maintainer="Justin Michalicek <jmichalicek@gmail.com>"
RUN apt-get update && apt-get install -y --no-install-recommends \
  make \
  libpq5 \
  && apt-get autoremove && apt-get clean
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
    DEBIAN_FRONTEND=noninteractive \
    PYTHONFAULTHANDLER=1

WORKDIR /django/bash-shell.net/
EXPOSE 8000
