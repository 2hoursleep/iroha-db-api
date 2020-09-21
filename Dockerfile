FROM tiangolo/uwsgi-nginx-flask:python3.8

ENV PIP_DISABLE_PIP_VERSION_CHECK=on

RUN pip install poetry

WORKDIR /app
COPY poetry.lock pyproject.toml /app/

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction

COPY iroha_db_api /app

EXPOSE 80