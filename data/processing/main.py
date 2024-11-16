import os
import time

from dotenv import load_dotenv

from brokers.kafka import Consumer


if __name__ == '__main__':

    load_dotenv()

    kafka_broker = os.getenv('KAFKA_BROKER')
    kafka_topic = os.getenv('KAFKA_TOPIC')

    consumer = Consumer(
        kafka_broker, 
        kafka_topic 
    )

    try:
        consumer.create_instance()
        # allow client to connect
        # time.sleep(3)
        # while consumer.is_kafka_connected():
        consumer.consume()
    except KeyboardInterrupt:
        consumer.logger.info(" [*] Stopping Kafka consumer...")
        exit(1)
