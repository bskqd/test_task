FROM python:3.10

ARG GID=101
ENV USER=user
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get -y update && adduser --gid ${GID} --shell /bin/bash --disabled-password ${USER}

COPY --chown=${USER}:${GID} gunicorn.conf.py /gunicorn/gunicorn.conf.py
COPY --chown=${USER}:${GID} ./alembic.ini /src/

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY --chown=${USER}:${GID} ./alembic /src/alembic
COPY --chown=${USER}:${GID} ./src /src

WORKDIR /src

USER ${USER}:${GID}

EXPOSE 8000
CMD ["sh", "-c", "gunicorn main:app --config /gunicorn/gunicorn.conf.py"]