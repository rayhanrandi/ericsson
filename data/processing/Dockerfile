FROM python:3.11-slim

EXPOSE 8000

# Argument variables
ARG PORT
ARG LOG_LEVEL
ARG KAFKA_BROKER
ARG KAFKA_TOPIC
ARG CLICKHOUSE_HOST
ARG CLICKHOUSE_PORT
ARG CLICKHOUSE_USERNAME
ARG CLICKHOUSE_PASSWORD
ARG CLICKHOUSE_DATABASE
ARG CLICKHOUSE_SENSOR_TABLE

# Environment variables with defaults
ARG PORT=${PORT:-8000}
ARG LOG_LEVEL=${LOG_LEVEL:-DEBUG}
ARG KAFKA_BROKER=${KAFKA_BROKER}
ARG KAFKA_TOPIC=${KAFKA_TOPIC}
ARG CLICKHOUSE_HOST=${CLICKHOUSE_HOST}
ARG CLICKHOUSE_PORT=${CLICKHOUSE_PORT}
ARG CLICKHOUSE_USERNAME=${CLICKHOUSE_USERNAME}
ARG CLICKHOUSE_PASSWORD=${CLICKHOUSE_PASSWORD}
ARG CLICKHOUSE_DATABASE=${CLICKHOUSE_DATABASE}
ARG CLICKHOUSE_SENSOR_TABLE=${CLICKHOUSE_SENSOR_TABLE}

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000"]