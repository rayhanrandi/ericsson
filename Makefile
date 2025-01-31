# Production
GRAFANA_COMPOSE_PATH := ./grafana/docker-compose.yml
WAREHOUSE_COMPOSE_PATH := ./warehouse/docker-compose.yml
LAKE_COMPOSE_PATH := ./data/docker-compose.yml
PROC_COMPOSE_PATH := ./data/processing/docker-compose.yml
STREAM_COMPOSE_PATH := ./data/stream/docker-compose.yml
RAG_COMPOSE_PATH := ./rag/docker-compose.yml

# Local
GRAFANA_DEV_COMPOSE_PATH := ./grafana/docker-compose.dev.yml
WAREHOUSE_DEV_COMPOSE_PATH := ./warehouse/docker-compose.dev.yml
LAKE_DEV_COMPOSE_PATH := ./data/docker-compose.dev.yml
PROC_DEV_COMPOSE_PATH := ./data/processing/docker-compose.dev.yml
STREAM_DEV_COMPOSE_PATH := ./data/stream/docker-compose.dev.yml
RAG_DEV_COMPOSE_PATH := ./rag/docker-compose.dev.yml


# Production
# run grafana service
grafana-up:
	docker compose -f $(GRAFANA_COMPOSE_PATH) up -d
# stop grafana service
grafana-down:
	docker compose -f $(GRAFANA_COMPOSE_PATH) down
# restart grafana service
grafana-restart: 
	grafana-down 
	grafana-up
# view grafana logs
grafana-logs:
	docker compose -f $(GRAFANA_COMPOSE_PATH) logs
# Local
# run grafana service
grafana-up-dev:
	docker compose -f $(GRAFANA_DEV_COMPOSE_PATH) up -d
# stop grafana service
grafana-down-dev:
	docker compose -f $(GRAFANA_DEV_COMPOSE_PATH) down
# restart grafana service
grafana-restart-dev: 
	grafana-down-dev 
	grafana-up-dev
# view grafana logs
grafana-logs-dev:
	docker compose -f $(GRAFANA_DEV_COMPOSE_PATH) logs


# Production
# run warehouse service
wh-up:
	docker compose -f $(WAREHOUSE_COMPOSE_PATH) up -d
# stop warehouse service
wh-down:
	docker compose -f $(WAREHOUSE_COMPOSE_PATH) down
# restart warehouse service
wh-restart: 
	wh-down 
	wh-up
# view warehouse logs
wh-logs:
	docker compose -f $(WAREHOUSE_COMPOSE_PATH) logs
# Local
# run warehouse service
wh-up-dev:
	docker compose -f $(WAREHOUSE_DEV_COMPOSE_PATH) up -d
# stop warehouse service
wh-down-dev:
	docker compose -f $(WAREHOUSE_DEV_COMPOSE_PATH) down
# restart warehouse service
wh-restart-dev: 
	wh-down-dev 
	wh-up-dev
# view warehouse logs
wh-logs-dev:
	docker compose -f $(WAREHOUSE_DEV_COMPOSE_PATH) logs


# Production
# start data-lake service
lake-up:
	docker compose -f $(LAKE_COMPOSE_PATH) up -d
# stop data-lake service
lake-down:
	docker compose -f $(LAKE_COMPOSE_PATH) down
# restart data-lake service
lake-restart: 
	lake-down 
	lake-up
# view data-lake logs
lake-logs:
	docker compose -f $(LAKE_COMPOSE_PATH) logs
# Local
# start data-lake service
lake-up-dev:
	docker compose -f $(LAKE_DEV_COMPOSE_PATH) up -d
# stop data-lake service
lake-down-dev:
	docker compose -f $(LAKE_DEV_COMPOSE_PATH) down
# restart data-lake service
lake-restart-dev: 
	lake-down-dev 
	lake-up-dev
# view data-lake logs
lake-logs-dev:
	docker compose -f $(LAKE_DEV_COMPOSE_PATH) logs


# Production
# run data-proc service
proc-up:
	docker compose -f $(PROC_COMPOSE_PATH) up -d
# stop data-proc service
proc-down:
	docker compose -f $(PROC_COMPOSE_PATH) down
# restart data-proc service
proc-restart: 
	proc-down 
	proc-up
# view data-proc logs
proc-logs:
	docker compose -f $(PROC_COMPOSE_PATH) logs
# Local
# run data-proc service
proc-up-dev:
	docker compose -f $(PROC_DEV_COMPOSE_PATH) up -d
# stop data-proc service
proc-down-dev:
	docker compose -f $(PROC_DEV_COMPOSE_PATH) down
# restart data-proc service
proc-restart-dev: 
	proc-down-dev 
	proc-up-dev
# view data-proc logs
proc-logs-dev:
	docker compose -f $(PROC_DEV_COMPOSE_PATH) logs


# Production
# run data-stream service
stream-up:
	docker compose -f $(STREAM_COMPOSE_PATH) up --build -d
# stop data-stream service
stream-down:
	docker compose -f $(STREAM_COMPOSE_PATH) down
# restart data-stream service
stream-restart: 
	stream-down 
	stream-up
# view data-stream logs
stream-logs:
	docker compose -f $(STREAM_COMPOSE_PATH) logs
# Local
# run data-stream service
stream-up-dev:
	docker compose -f $(STREAM_DEV_COMPOSE_PATH) up --build -d
# stop data-stream service
stream-down-dev:
	docker compose -f $(STREAM_DEV_COMPOSE_PATH) down
# restart data-stream service
stream-restart-dev: 
	stream-down-dev 
	stream-up-dev
# view data-stream logs
stream-logs-dev:
	docker compose -f $(STREAM_DEV_COMPOSE_PATH) logs


# Production
# run rag service
rag-up:
	docker compose -f $(RAG_COMPOSE_PATH) up --build -d
# stop rag service
rag-down:
	docker compose -f $(RAG_COMPOSE_PATH) down
# restart rag service
rag-restart: 
	rag-down 
	rag-up
# view rag logs
rag-logs:
	docker compose -f $(RAG_COMPOSE_PATH) logs
# Local
# run rag service
rag-up-dev:
	docker compose -f $(RAG_DEV_COMPOSE_PATH) up --build -d
# stop rag service
rag-down-dev:
	docker compose -f $(RAG_DEV_COMPOSE_PATH) down
# restart rag service
rag-restart-dev: 
	rag-down-dev 
	rag-up-dev
# view rag logs
rag-logs-dev:
	docker compose -f $(RAG_DEV_COMPOSE_PATH) lo

	
# help
help:
	@echo "Available services: grafana, wh, lake, proc, stream"
	@echo ""
	@echo "Service description:"
	@echo "grafana:"
	@echo "  Main monitoring dashboard."
	@echo "wh:"
	@echo "  Data warehouse to store processed data for observablity & monitoring."
	@echo "lake:"
	@echo "  Data lake to store raw data for batch processes."
	@echo "proc:"
	@echo "  Data processing platform to process raw data."
	@echo "stream:"
	@echo "  Data streaming platform to simulate real-time data inputs."
	@echo "rag:"
	@echo "  LLM based RAG service to generate insights from real-time data.
	@echo ""
	@echo "Usage (Use `-dev` suffix for local development e.g. make rag-up-dev):"
	@echo "  make <service>-up    		- Start services with docker compose."
	@echo "  make <service>-down  		- Stop and remove docker compose services."
	@echo "  make <service>-restart 	- Restart docker compose services."
	@echo "  make <service>-logs		- View docker compose service logs."
	@echo "  make help            		- Show this help message."
