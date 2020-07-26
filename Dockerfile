FROM python:3.7.7 as base
RUN pip install poetry
WORKDIR /app
COPY pyproject.toml poetry.lock /app/

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi
RUN export PYTHONPATH=/app
COPY pypi_tools /app/pypi_tools
COPY pypi_observer_gcp_key.json /app/pypi_observer_gcp_key.json
WORKDIR /app/pypi_tools
CMD python listner.py