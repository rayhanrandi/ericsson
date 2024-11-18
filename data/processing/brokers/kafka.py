import json

from kafka import KafkaConsumer
from kafka.errors import KafkaError

from config.logging import Logger
from config.utils import get_env_value
from config.db.postgresql import PostgreSQLClient
from config.db.clickhouse import ClickhouseClient



class Consumer:
    """
    Creates an instance of KafkaConsumer with additional methods to consume data.
    """
    def __init__(self, kafka_broker: str, kafka_topic: str, db: PostgreSQLClient | ClickhouseClient = None) -> None:
        self._kafka_server = kafka_broker
        self._kafka_topic = kafka_topic
        self._instance = None
        self._db = db
        self.logger = Logger().setup_logger(service_name='consumer')
    
    def create_instance(self) -> KafkaConsumer:
        """
        Creates new kafka consumer and returns an instance of KafkaConsumer.
        """
        self._instance = KafkaConsumer(
            self._kafka_topic,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            bootstrap_servers=self._kafka_server,
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
                self.logger.info(" [*] Kafka connection OK.")
                return True
            else:
                self.logger.error(" [X] Kafka not connected!")
                return False
        except KafkaError as e:
            self.logger.error(f" [X] Kafka connection error!: {e}")
            return False
    
    def consume(self) -> None:
        """
        Consume messages indefinitely.
        """
        self.logger.info(" [*] Starting Kafka consumer...")
        try:
            for message in self._instance:
                self.logger.info(f" [*] recv: {message}")
                # get message data, then process 
                data = message.value
                # query = f"""
                #     INSERT INTO {get_env_value('TABLE_NAME')} (sensor, time, temp, hum, gyro, accel)
                #     VALUES({data['sensor']}, '{data['time']}', {data['temp']}, '{data['hum']}', '{self._db.to_sql_array(data['gyro'])}', '{self._db.to_sql_array(data['accel'])}')
                # """
                # self._db.query(query)
                print(data)
        except Exception as e:
            self.logger.error(f" [x] Failed to consume message: {e}")
            self.logger.info(" [*] Stopping Kafka consumer...")
        finally:
            # close the consumer 
            self._instance.close()
