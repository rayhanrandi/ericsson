import threading
import time

from dotenv import load_dotenv
from fastapi import FastAPI

from brokers.kafka import Producer
from config.utils import get_env_value


def produce(producer: Producer) -> None:
    """
    Run producer instance.
    """
    try:
        producer.create_instance()
        # allow client to connect
        # time.sleep(3)
        # if producer.is_kafka_connected():
        producer.produce()
    except KeyboardInterrupt:
        producer.logger.info(" [*] Stopping data generation.")
        exit(1)


load_dotenv()

# run healthcheck server
app = FastAPI()

@app.get("/ping")
async def healthcheck():
    return { "status": "healthy" }

kafka_broker = get_env_value('KAFKA_BROKER')
kafka_topic = get_env_value('KAFKA_TOPIC')

producer = Producer(
    kafka_broker, 
    kafka_topic
)

producer.logger.info(f' [*] Healthcheck running on port 8000.')

# run producer
t_producer = threading.Thread(
    target=produce,
    args=(producer,),
    daemon=True
)
t_producer.start()

