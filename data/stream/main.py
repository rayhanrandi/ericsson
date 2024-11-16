import os
import time

from dotenv import load_dotenv

from brokers.kafka import Producer


if __name__ == '__main__':

    load_dotenv()

    kafka_broker = os.getenv('KAFKA_BROKER')
    kafka_topic = os.getenv('KAFKA_TOPIC')

    producer = Producer(
        kafka_broker, 
        kafka_topic
    )

    try:
        producer.create_instance()
        # allow client to connect
        # time.sleep(3)
        # if producer.is_kafka_connected():
        producer.produce()
    except KeyboardInterrupt:
        producer.logger.info(" [*] Stopping data generation.")
        exit(1)
