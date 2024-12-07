FROM python:3.11-slim

EXPOSE 8000

# Argument variables
ARG LOG_LEVEL
ARG PORT
ARG KAFKA_BROKER
ARG KAFKA_TOPIC
ARG VECTOR_AGGREGATOR_SINK_ADDR

# Required environment variables as build arguments here
ARG LOG_LEVEL=${LOG_LEVEL:-DEBUG}
ARG PORT=${PORT}
ARG KAFKA_BROKER=${KAFKA_BROKER}
ARG KAFKA_TOPIC=${KAFKA_TOPIC}
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

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port", ${PORT}]