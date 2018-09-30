FROM python:3.7.0-stretch
MAINTAINER Justin Michalicek <jmichalicek@gmail.com>
ENV PYTHONUNBUFFERED 1

RUN DEBIAN_FRONTEND=noninteractive apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --allow-unauthenticated \
  inotify-tools \
  software-properties-common \
#  sudo \
  vim \
  telnet \
#  postgresql \
#  postgresql-client \
#  postgresql-server-dev-all \
  && apt-get autoremove && apt-get clean

RUN pip install pip --upgrade
RUN useradd -ms /bin/bash django
# && echo "django ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER django
ENV HOME /home/django
RUN pip install pipenv --user
COPY --chown=django . /home/django/bash-shell.net/
WORKDIR /home/django/bash-shell.net/
ENV PATH=/home/django/.local/bin:$PATH
ENV PIPENV_VENV_IN_PROJECT=1 PIPENV_NOSPIN=1 PIPENV_DONT_USE_PYENV=1 PIPENV_HIDE_EMOJIS=1 PIP_CONFIG_FILE=/home/django/pip.conf
RUN echo "[global]\n# This actually enables --no-cache-dir\nno-cache-dir = false" >> /home/django/pip.conf
ENV LC_ALL=C.UTF-8 LANG=C.UTF-8 PYTHONIOENCODING=utf-8 DJANGO_SETTINGS_MODULE=bash_shell_net.settings.local
RUN pipenv install
EXPOSE 8000
