FROM python:3.11-slim

EXPOSE 8000

# Argument variables
ARG LOG_LEVEL
ARG DATA_INTERVAL
ARG CRON_SLICES

ARG TOGETHER_ENDPOINT
ARG TOGETHER_API_KEY
ARG TOGETHER_LLM_MODEL

ARG CLICKHOUSE_HOST
ARG CLICKHOUSE_PORT
ARG CLICKHOUSE_USERNAME
# ARG CLICKHOUSE_PASSWORD
ARG CLICKHOUSE_DATABASE
ARG CLICKHOUSE_ANALYSIS_TABLE
ARG CLICKHOUSE_SUMMARY_TABLE

ARG VECTOR_AGGREGATOR_SINK_ADDR

# Required environment variables as build arguments here
ARG LOG_LEVEL=${LOG_LEVEL}
ARG DATA_INTERVAL=${DATA_INTERVAL}
ARG CRON_SLICES=${CRON_SLICES}

ARG TOGETHER_ENDPOINT=${TOGETHER_ENDPOINT}
ARG TOGETHER_API_KEY=${TOGETHER_API_KEY}
ARG TOGETHER_LLM_MODEL=${TOGETHER_LLM_MODEL}

ARG CLICKHOUSE_HOST=${CLICKHOUSE_HOST}
ARG CLICKHOUSE_PORT=${CLICKHOUSE_PORT}
ARG CLICKHOUSE_USERNAME=${CLICKHOUSE_USERNAME}
# ARG CLICKHOUSE_PASSWORD=${CLICKHOUSE_PASSWORD}
ARG CLICKHOUSE_DATABASE=${CLICKHOUSE_DATABASE}
ARG CLICKHOUSE_ANALYSIS_TABLE=${CLICKHOUSE_ANALYSIS_TABLE}
ARG CLICKHOUSE_SUMMARY_TABLE=${CLICKHOUSE_SUMMARY_TABLE}

ARG VECTOR_AGGREGATOR_SINK_ADDR=${VECTOR_AGGREGATOR_SINK_ADDR}

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

# Install cron and busybox
RUN sudo apt-get update \
  && sudo apt-get install -y \
    cron

# https://stackoverflow.com/a/37458519
RUN chmod 0744 ./main.py

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000"]