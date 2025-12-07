FROM python:3.12

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_VIRTUALENVS_IN_PROJECT=1

ARG work_dir="/event_management_server/"

WORKDIR $work_dir

RUN apt update
RUN     apt install -y --no-install-recommends \
    binutils gettext libproj-dev gdal-bin


RUN  pip install "poetry==$POETRY_VERSION"

COPY poetry.lock pyproject.toml ./

RUN poetry install --no-interaction --no-ansi --no-root