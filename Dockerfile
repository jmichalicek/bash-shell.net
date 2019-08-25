FROM python:3.7.4-stretch
MAINTAINER Justin Michalicek <jmichalicek@gmail.com>
ENV PYTHONUNBUFFERED 1

RUN DEBIAN_FRONTEND=noninteractive apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --allow-unauthenticated \
  inotify-tools \
  software-properties-common \
#  sudo \
  vim \
  telnet \
  && apt-get autoremove && apt-get clean

RUN pip install pip --upgrade
RUN useradd -ms /bin/bash django
# && echo "django ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER django
ENV HOME=/home/django PATH=/home/django/.local/bin:$PATH
RUN pip install pipenv --user
RUN mkdir /home/django/bash-shell.net/
COPY --chown=django ./Pipfile ./Pipfile.lock /home/django/bash-shell.net/
WORKDIR /home/django/bash-shell.net/
ENV PIPENV_VENV_IN_PROJECT=1 PIPENV_NOSPIN=1 PIPENV_DONT_USE_PYENV=1 PIPENV_HIDE_EMOJIS=1 PIP_CONFIG_FILE=/home/django/pip.conf
RUN echo "[global]\n# This actually enables --no-cache-dir\nno-cache-dir = false" >> /home/django/pip.conf
ENV LC_ALL=C.UTF-8 LANG=C.UTF-8 PYTHONIOENCODING=utf-8 DJANGO_SETTINGS_MODULE=bash_shell_net.settings.local
RUN pipenv install --deploy --ignore-pipfile
# Too bad there's no way to exclude the files which were already copied
COPY --chown=django . /home/django/bash-shell.net
EXPOSE 8000

# TODO: use this as a base on codeship and then
# have a separate 2 step dockerfile which pulls in the image made from this
# and then step 2 will use the code and a much smaller base image
