import datetime
import threading

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from brokers.kafka import Consumer
from config.utils import get_env_value
from config.db.clickhouse import ClickhouseClient
from classification.model import Model
from processor.spark import SparkProcessor


def consume(consumer: Consumer) -> None:
    """
    # ! DEPRECATED !
    Run consumer instance.
    """
    try:
        consumer.create_instance()
        consumer.consume()
    except KeyboardInterrupt:
        consumer.logger.info(" [*] Stopping Kafka consumer...")
        exit(1)

def process(processor: SparkProcessor) -> None:
    """
    Process data with pipeline defined in SparkProcessor.
    """
    try:
        processor.process()
    except Exception as e:
        processor.logger.error(f" [X] Error while processing data: {e}")
        exit(1)


load_dotenv()

ch_client = ClickhouseClient(
    host=get_env_value("CLICKHOUSE_HOST"),
    port=get_env_value("CLICKHOUSE_PORT"),
    user=get_env_value("CLICKHOUSE_USERNAME"),
    database=get_env_value("CLICKHOUSE_DATABASE"),
    table=get_env_value("CLICKHOUSE_SENSOR_TABLE")
)

# model = Model(
#     model_path="classification/fault_classifier_model.pkl",
#     scaler_path="classification/scaler.save"
# )
# model.load_model()

# consumer = Consumer(
#     kafka_broker=get_env_value('KAFKA_BROKER'), 
#     kafka_topic=get_env_value('KAFKA_TOPIC'),
#     kafka_consumer_group=get_env_value('KAFKA_CONSUMER_GROUP'),
#     model=model,
#     db=ch_client
# )

processor = SparkProcessor(
    kafka_bootstrap_servers=get_env_value("KAFKA_BOOTSTRAP_SERVERS"),
    kafka_topic=get_env_value("KAFKA_TOPIC"),
)

t_processor = threading.Thread(
    target=process,
    args=(processor,),
    daemon=True
).start()

app = FastAPI()

@app.get("/ping")
async def healthcheck():
    """
    Service is healthy if processor thread is running.
    """
    if t_processor.is_alive():
        return JSONResponse(
            status_code=200,
            content={ "status": "healthy" }
        )
    return JSONResponse(
        status_code=500,
        content={
            "status": "unhealthy",
            "message": "Processing thread not running.",
            "timestamp": datetime.datetime.now().isoformat(),
        })


processor.logger.info(f' [*] Healthcheck running on port 8000.')

