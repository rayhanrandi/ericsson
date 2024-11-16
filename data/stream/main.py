import os
import time

from dotenv import load_dotenv

from brokers.kafka import Producer


if __name__ == '__main__':

    load_dotenv()

    KAFKA_BROKER = os.getenv('KAFKA_BROKER')
    KAFKA_TOPIC = os.getenv('KAFKA_TOPIC')

    producer = Producer(
        'localhost:9093', 
        'sensor_data'
    )

    try:
        producer.create_instance()
        # allow client to connect
        time.sleep(3)
        if producer.is_kafka_connected():
            producer.produce()
    except KeyboardInterrupt:
        producer.logger.info(" [*] Stopping data generation.")
        exit(1)
