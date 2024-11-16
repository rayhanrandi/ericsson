import os

from dotenv import load_dotenv

from brokers.kafka import Producer


if __name__ == '__main__':

    load_dotenv()

    KAFKA_BROKER = os.getenv('KAFKA_BROKER')
    KAFKA_TOPIC = os.getenv('KAFKA_TOPIC')

    producer = Producer(
        kafka_broker=KAFKA_BROKER, 
        kafka_topic=KAFKA_TOPIC
    )

    try:
        producer.create_instance()
        producer.produce()
    except KeyboardInterrupt:
        exit(1)
