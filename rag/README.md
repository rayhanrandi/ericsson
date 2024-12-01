# Retrieval-Augmented Generation

## Prerequisites

Create `.env` file with key `ENVIRONMENT`. Set to `DEVELOPMENT` for local, else `PRODUCTION`. Fill other fields in `.env.dev` for local development.

### With Clickhouse
1. Run Clickhouse (docker image):

    ```
    docker run -d -p 8123:8123 -p9000:9000 --name langchain-clickhouse-server --ulimit nofile=262144:262144 clickhouse/clickhouse-server:latest
    ```

2. Connect to Clickhouse instance & create table (if not present):
   
    ```
    docker exec -it langchain-clickhouse-server clickhouse-client
    ```

    ```
    CREATE TABLE sensor_data
    (
        `sensor` String,
        `time` DateTime64(3),
        `temp` Float32,
        `hum` Float32,
        `gyro` Array(Float32),
        `accel` Array(Float32)
    )
    ENGINE = MergeTree
    ORDER BY (time, sensor)
    PRIMARY KEY (time);
    ```

### With SQL (PostgreSQL)
1. Create SQL table:
    ```
    CREATE TABLE sensor_embeddings (
        id UUID DEFAULT gen_random_uuid(),  
        sensor VARCHAR(50),                 
        time TIMESTAMP,                     
        temp REAL,                          
        hum REAL,                           
        gyro FLOAT8[],                      
        accel FLOAT8[],                                       
        PRIMARY KEY (id)
    );
    ```

    ```
    CREATE TABLE sensor_insights (
        id UUID DEFAULT gen_random_uuid(),  
        summary VARCHAR,                
        time TIMESTAMP,                                                            
        PRIMARY KEY (id)
    );
    ```

## Quickstart
1. Create virtual environment, activate, and install required packages:

    ```
    python -m venv .venv
    .venv\Scripts\activate
    ```
    or
    ```
    virtualenv .venv
    source .venv/bin/activate
    ```
    then
    ```
    pip install -r requirements.txt
    ```

2. Run cron job with:

    ```
    python cron.py
    ```

## References

https://hub.docker.com/r/clickhouse/clickhouse-server/

https://python.langchain.com/docs/integrations/vectorstores/clickhouse/

https://grafana.com/grafana/plugins/grafana-clickhouse-datasource/

https://clickhouse.com/docs/knowledgebase/vector-search

https://python.langchain.com/docs/integrations/llms/together/

https://python.langchain.com/docs/tutorials/rag/