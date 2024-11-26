GRAFANA_COMPOSE_PATH := ./grafana/docker-compose.yml
WAREHOUSE_COMPOSE_PATH := ./warehouse/docker-compose.yml
LAKE_COMPOSE_PATH := ./data/docker-compose.yml
PROC_COMPOSE_PATH := ./data/processing/docker-compose.yml
STREAM_COMPOSE_PATH := ./data/stream/docker-compose.yml


# run grafana service
grafana-up:
	docker compose -f $(GRAFANA_COMPOSE_PATH) up
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


# run warehouse service
wh-up:
	docker compose -f $(WAREHOUSE_COMPOSE_PATH) up
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


# start data-lake service
lake-up:
	docker compose -f $(LAKE_COMPOSE_PATH) up
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


# run data-proc service
proc-up:
	docker compose -f $(PROC_COMPOSE_PATH) up
# stop data-proc service
proc-down:
	docker-compose -f $(PROC_COMPOSE_PATH) 
# restart data-proc service
proc-restart: 
	proc-down 
	proc-up
# view data-proc logs
proc-logs:
	docker compose -f $(PROC_COMPOSE_PATH) logs


# run data-stream service
stream-up:
	docker compose -f $(STREAM_COMPOSE_PATH) up
# stop data-stream service
stream-down:
	docker-compose -f $(STREAM_COMPOSE_PATH) 
# restart data-stream service
stream-restart: 
	stream-down 
	stream-up
# view data-stream logs
stream-logs:
	docker compose -f $(STREAM_COMPOSE_PATH) logs

	
# help
help:
	@echo "Available services: grafana, wh, lake, proc, stream"
	@echo "grafana:"
	@echo "  Main monitoring dashboard."
	@echo "wh:"
	@echo "  Data warehouse to store processed data for observablity & monitoring."
	@echo "lake:"
	@echo "  Data lake to store raw data for batch processes."
	@echo "proc:"
	@echo "	 Data processing platform to process raw data."
	@echo "stream:"
	@echo "  Data streaming platform to simulate real-time data inputs."
	@echo "Usage:"
	@echo "  make <service>-up    		- Start services with docker compose."
	@echo "  make <service>-down  		- Stop and remove docker compose services."
	@echo "  make <service>-restart 	- Restart docker compose services."
	@echo "  make <service>-logs		- View docker compose service logs."
	@echo "  make help            		- Show this help message."
