FROM python:3.10.7-alpine

RUN apk update 
RUN apk add bash curl git postgresql-dev gcc python3-dev musl-dev 
RUN pip install poetry

WORKDIR /app

# Install dependencies directly on the container
RUN poetry config virtualenvs.create false

# Install dependencies
COPY poetry.lock pyproject.toml ./
COPY src/__init__.py src/__init__.py
RUN poetry lock --check && poetry install -vvv
