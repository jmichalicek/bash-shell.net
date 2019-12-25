FROM python:3.8-buster AS dev
LABEL maintainer="Justin Michalicek <jmichalicek@gmail.com>"
ENV PYTHONUNBUFFERED 1

RUN DEBIAN_FRONTEND=noninteractive apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --allow-unauthenticated \
  inotify-tools \
  software-properties-common \
  sudo \
  vim \
  telnet \
  && apt-get autoremove && apt-get clean

RUN pip install pip==19.3.1
RUN useradd -ms /bin/bash -d /django django && echo "django ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
USER django
ENV HOME=/django PATH=/django/bash-shell.net/.venv/bin:/django/.local/bin:$PATH LC_ALL=C.UTF-8 LANG=C.UTF-8 PYTHONIOENCODING=utf-8
EXPOSE 8000

FROM dev AS build
RUN mkdir /django/bash-shell.net/ && python -m venv /django/bash-shell.net/.venv
ENV PIP_CONFIG_FILE=/django/pip.conf
RUN echo "[global]\n# This actually enables --no-cache-dir\nno-cache-dir = false" >> /django/pip.conf
# https://stackoverflow.com/a/28210626
# python -m venv only copies the bundled pip, even if you've done a pip install -U pip to get
# a newer version installed, so update it in the virtualenv
RUN pip install pip==19.3.1
RUN pip install pip-tools
COPY --chown=django ./requirements.txt /django/bash-shell.net/
WORKDIR /django/bash-shell.net/
RUN pip-sync
COPY --chown=django ./ /django/bash-shell.net
RUN DJANGO_SETTINGS_MODULE=bash_shell_net.settings.production python manage.py collectstatic -l --noinput -i *.scss

FROM python:3.8-slim-buster AS prod
RUN useradd -ms /bin/bash -d /django django
COPY --from=build /django/bash-shell.net /django/bash-shell.net
ENV DJANGO_SETTINGS_MODULE=bash_shell_net.settings.production HOME=/django PATH=/django/bash-shell.net/.venv/bin:/django/.local/bin:$PATH LC_ALL=C.UTF-8 LANG=C.UTF-8 PYTHONIOENCODING=utf-8
WORKDIR /django/bash-shell.net/
EXPOSE 8000
