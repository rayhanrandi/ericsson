# Data Stream

A placeholder service in place of actual edge devices from on premises machinery. This service generates data in real-time, either from a `.csv` dataset or continuously generated data points, into a Kafka topic message broker. 



## Contributing


### Prerequisites

1. Ensure docker & and docker compose are installed. Validate by running `docker` and `docker compose` in CLI.
2. Create a `.env` file in current directory: `../<root_project_dir>/data/stream/.env`.
3. Fill in the values from `.env.example` appropriately according to desired values, or use provided values.
4. From `../<root_project_dir>/data/stream`, run:
   
   ```
   docker compose -f docker-compose up -d
   ```


### Quickstart

1. In current directory, run:
   
    ```
    uvicorn main:app --reload 
    ```
