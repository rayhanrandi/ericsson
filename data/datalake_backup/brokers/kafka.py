import json
import math
import random
import time

from datetime import (
    datetime, 
    timedelta
)
from config.logging import Logger
from google.cloud import storage
from kafka import KafkaConsumer, TopicPartition
from kafka.errors import KafkaError
from kafka.structs import OffsetAndMetadata



class DatalakeBackup:
    """
    Creates an instance of KafkaProducer with additional methods to produce dummy data.
    """
    def __init__(self, kafka_broker: str, kafka_topic: str, kafka_consumer_group: str,
                 bucket_name: str, batch_size: int, time_interval:int) -> None:
        self._kafka_server = kafka_broker
        self._kafka_topic = kafka_topic
        self._kafka_consumer_group = kafka_consumer_group
        self._instance = None
        self._batch_size = batch_size # number of messages to backup in a batch
        self._time_interval = time_interval # time interval to backup messages
        self.logger = Logger().setup_logger(service_name='DatalakeBackup')
        self._gcs_client = storage.Client()
        self._bucket = self._gcs_client.bucket(bucket_name)
    

    def create_instance(self) -> KafkaConsumer:
        """
        Creates new kafka producer and returns an instance of KafkaProducer.
        """
        self.logger.info(" [*] Starting Kafka producer...")
        self.logger.info(f"bucket: {self._bucket}")
        self.logger.info(f"batch_size: {self._batch_size}")
        self.logger.info(f"time_interval: {self._time_interval}")
        self._instance = KafkaConsumer(
            self._kafka_topic,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            bootstrap_servers=self._kafka_server,
            group_id=self._kafka_consumer_group,
            enable_auto_commit=False,  # Disable auto-commit to manage offsets manually
            api_version=(0,9) # enables full group coordination features with automatic partition assignment and rebalancing,
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
    
    # Function to write batch to GCS
    def write_to_gcs(self, batch, partition, last_offset) -> None:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        # Use datetime to get year, month, and day components
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month
        day = current_date.day

        self.logger.info(f"Backing up {len(batch)} messages... at {timestamp}")
        file_name = f'raw-data/{year}/{month:02d}/{day:02d}/partition-{partition}-offset-{last_offset}.json'

        blob = self._bucket.blob(file_name)
        json_data = '[' + ',\n'.join(batch) + ']'
        blob.upload_from_string(json_data)
        self.logger.info(f"Backup successful: {file_name}")
        return None
 
    def consume_backup(self) -> None:
        """
        Consume and backup messages from Kafka topic.
        """
        self.logger.info(f" [*] Consuming messages from topic: {self._kafka_topic}")
        
        batch = []
        start_time = time.time()
        last_offsets = {}
        no_messages_count = 0  # Counter to track how many times we've seen no messages

        while True:
            try:  # Infinite loop to continuously consume messages
            # Poll for messages
                records = self._instance.poll(timeout_ms=1000)  # Poll Kafka every 1 second

                if not records:  # If no messages were consumed
                    no_messages_count += 1
                    self.logger.info(" [*] No new messages. Waiting for new messages.")
                else:
                    no_messages_count = 0  # Reset counter if new messages arrived

                # Process consumed messages if any
                for tp, messages in records.items():
                    for message in messages:
                        self.logger.info(f"Batch size: {len(batch)}")
                        partition = message.partition
                        offset = message.offset
                        value = json.dumps(message.value)

                        # Add message to batch
                        batch.append(value)
                        last_offsets[partition] = offset
                # Check if conditions for backup are met
                if len(batch) >= self._batch_size or (time.time() - start_time) >= self._time_interval:
                    if batch:  # Only process if there are messages
                        try:
                            # Write batch to GCS
                            self.write_to_gcs(batch, list(last_offsets.keys())[0], list(last_offsets.values())[0])

                            # Commit offsets for all processed partitions
                            for p, o in last_offsets.items():
                                self._instance.commit({
                                    TopicPartition(self._kafka_topic, p): OffsetAndMetadata(o + 1, None)
                                })
                            self.logger.info(f"Offsets committed: {last_offsets}")

                        except Exception as e:
                            self.logger.error(f"Error during backup: {str(e)}", exc_info=True)
                        finally:
                            # Reset batch and timer
                            batch = []
                            start_time = time.time()
            except KeyboardInterrupt:
                self.logger.info(" [*] Stopping data backup.")
            finally:
            
                self._instance.close()
                
                # Check for termination or idle condition (optional)
            # if no_messages_count > 5 and (time.time() - start_time) >= self._time_interval:
            #     self.logger.info("No messages and time interval reached. Exiting loop.")
            #     break

        