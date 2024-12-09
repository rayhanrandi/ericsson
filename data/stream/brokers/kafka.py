import json
import math
import random
import time
import csv

from datetime import (
    datetime, 
    timedelta
)

from config.logging import Logger

from kafka import KafkaProducer
from kafka.errors import KafkaError


class Producer:
    """
    Creates an instance of KafkaProducer with additional methods to produce dummy data.
    """
    def __init__(self, kafka_broker: str, kafka_topic: str) -> None:
        self._kafka_server = kafka_broker
        self._kafka_topic = kafka_topic
        self._instance = None
        self.logger = Logger().setup_logger(service_name='producer')
    

    def create_instance(self) -> KafkaProducer:
        """
        Creates new kafka producer and returns an instance of KafkaProducer.
        """
        self.logger.info(" [*] Starting Kafka producer...")
        self._instance = KafkaProducer(
            bootstrap_servers=self._kafka_server,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),  # JSON serialization
            api_version=(0,11,5)
        )
        return self._instance

    def is_kafka_connected(self) -> bool:
        """
        Check if the Kafka cluster is available by fetching metadata.
        """
        try:
            metadata = self._instance.bootstrap_connected()
            if metadata:
                self.logger.info(" [*] Connected to Kafka cluster successfully!")
                return True
            else:
                self.logger.error(" [X] Failed to connect to Kafka cluster.")
                return False
        except KafkaError as e:
            self.logger.error(f" [X] Kafka connection error: {e}")
            return False
        
    def ensure_bytes(self, message) -> bytes:
        """
        Ensure the message is in byte format.
        """
        if not isinstance(message, bytes):
            return bytes(message, encoding='utf-8')
        return message
    
    def produce(self) -> None:
        """
        Produces messages from a CSV file, simulating real-time data.
        """
        try:
            with open('dataset/csv/dataset.csv', mode='r') as file:
                reader = csv.DictReader(file)
                rows = list(reader)

            self.logger.info(" [*] Starting real-time Kafka producer.")
            while True:
                for row in rows:
                    # Update the timestamp to the current time for real-time simulation
                    row['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

                    # Send row to Kafka
                    self._instance.send(self._kafka_topic, value=row)
                    self.logger.info(f"[*] Sent: {row}")

                    # Simulate real-time delay
                    time.sleep(1)

                # Reset reader to simulate continuous data streaming
                file.seek(0)
                next(reader)  # Skip header row
        except Exception as e:
            self.logger.error(f" [X] {e}")
            self.logger.info(" [*] Stopping data generation.")
        finally:
            # close the kafka producer
            self._instance.close()
