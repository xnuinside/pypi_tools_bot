FROM python:3.7.7 as base
RUN pip install poetry
WORKDIR /app
COPY pyproject.toml poetry.lock /app/

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi
RUN export PYTHONPATH=/app
COPY pypi_tools /app/pypi_tools
WORKDIR /app/pypi_tools
FROM base as main
CMD export PYTHONPATH=$PYTHONPATH:/app && python main.py

FROM base as scheduler
CMD export PYTHONPATH=$PYTHONPATH:/app && python scheduler.py