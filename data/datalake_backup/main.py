import threading
import time

from dotenv import load_dotenv
from fastapi import FastAPI

from brokers.kafka import DatalakeBackup
from config.utils import get_env_value


def consume_backup(consumer: DatalakeBackup) -> None:
    """
    Run producer instance.
    """
    try:
        consumer.create_instance()
        # allow client to connect
        # time.sleep(3)
        # if producer.is_kafka_connected():
        consumer.consume_backup()
    except KeyboardInterrupt:
        consumer.logger.info(" [*] Stopping data backup.")
        exit(1)


load_dotenv()

# run healthcheck server
app = FastAPI()

@app.get("/ping")
async def healthcheck():
    return { "status": "healthy" }

kafka_broker = get_env_value('KAFKA_BROKER')
kafka_topic = get_env_value('KAFKA_TOPIC')

consumer = DatalakeBackup(
    kafka_broker=get_env_value('KAFKA_BROKER'), 
    kafka_topic=get_env_value('KAFKA_TOPIC'),
    kafka_consumer_group=get_env_value('KAFKA_CONSUMER_GROUP'),
    bucket_name=get_env_value('BUCKET_NAME'),
    batch_size=int(get_env_value('BATCH_SIZE')),
    time_interval=int(get_env_value('TIME_INTERVAL'))
)


consumer.logger.info(f' [*] Healthcheck running on port 8000.')

# run
t_consumer = threading.Thread(
    target=consume_backup,
    args=(consumer,),
    daemon=True
)
t_consumer.start()

