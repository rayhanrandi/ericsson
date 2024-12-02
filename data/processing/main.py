import threading

from dotenv import load_dotenv
from fastapi import FastAPI

from brokers.kafka import Consumer
from config.utils import get_env_value
from config.db.clickhouse import ClickhouseClient
from classification.model import Model

def consume(consumer: Consumer) -> None:
    """
    Run consumer instance.
    """
    try:
        consumer.create_instance()
        consumer.consume()
    except KeyboardInterrupt:
        consumer.logger.info(" [*] Stopping Kafka consumer...")
        exit(1)

load_dotenv()

ch_client = ClickhouseClient(
    host=get_env_value("CLICKHOUSE_HOST"),
    port=get_env_value("CLICKHOUSE_PORT"),
    user=get_env_value("CLICKHOUSE_USERNAME"),
    database=get_env_value("CLICKHOUSE_DATABASE"),
    table=get_env_value("CLICKHOUSE_SENSOR_TABLE")
)

model = Model(
    model_path="classification/fault_classifier_model.pkl",
    scaler_path="classification/scaler.save"
)
model.load_model()

consumer = Consumer(
    kafka_broker=get_env_value('KAFKA_BROKER'), 
    kafka_topic=get_env_value('KAFKA_TOPIC'),
    kafka_consumer_group=get_env_value('KAFKA_CONSUMER_GROUP'),
    model=model,
    db=ch_client
)

app = FastAPI()

@app.get("/ping")
async def healthcheck():
    return { "status": "healthy" }

consumer.logger.info(f' [*] Healthcheck running on port 8000.')

t_consumer = threading.Thread(
    target=consume,
    args=(consumer,),
    daemon=True
)
t_consumer.start()
