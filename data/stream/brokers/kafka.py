import json
import math
import random
import time

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
        Produces messages with a delay.
        """
        try:
            num_entries = 2880  # 24 hours with 30-second intervals
            interval_seconds = 30  # Interval between each entry in seconds
            start_time = datetime.now() - timedelta(hours=24)

            anomaly_rate = 0.05  # 5% anomaly rate

            def temperature(hour):
                return 15 + 10 * math.sin((hour / 24) * 2 * math.pi) + random.uniform(-3, 3)

            def humidity(hour):
                return 55 + 10 * math.cos((hour / 24) * 2 * math.pi) + random.uniform(-5, 5)

            while True:
                for i in range(num_entries):
                    # current_time = (start_time + timedelta(seconds=i * interval_seconds)).strftime("%Y-%m-%d %H:%M:%S")
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    hour = (start_time + timedelta(seconds=i * interval_seconds)).hour

                    temp = temperature(hour)
                    hum = humidity(hour)
                    
                    gyro = [round(random.uniform(0, 10), 2) for _ in range(3)]
                    accel = [round(random.uniform(0, 5), 2) for _ in range(3)]

                    sensor_data = {
                        "sensor": str(random.randint(1, 4)),
                        "time": current_time,
                        "temp": str(round(temp, 2)),
                        "hum": str(round(hum, 2)),
                        "gyro": gyro,
                        "accel": accel
                    }

                    if random.random() < anomaly_rate:
                        anomaly_type = random.choice(["temp_spike", "high_gyro", "high_accel", "combo"])
                        if anomaly_type == "temp_spike":
                            sensor_data["temp"] = str(round(random.uniform(100, 150), 2))  # Extreme temperature
                        elif anomaly_type == "high_gyro":
                            sensor_data["gyro"] = [round(random.uniform(100, 200), 2) for _ in range(3)]  # High gyro
                        elif anomaly_type == "high_accel":
                            sensor_data["accel"] = [round(random.uniform(10, 20), 2) for _ in range(3)]  # High accel
                        elif anomaly_type == "combo":
                            sensor_data["temp"] = str(round(random.uniform(80, 120), 2))
                            sensor_data["hum"] = str(round(random.uniform(60, 80), 2))
                            sensor_data["gyro"] = [round(random.uniform(50, 100), 2) for _ in range(3)]

                    # Send data to Kafka
                    self._instance.send(self._kafka_topic, value=sensor_data)
                    self.logger.info(f" [*] sent: {sensor_data}")

                    # simulate delays
                    # TODO: minimize delays
                    time.sleep(random.uniform(1, 30))
        except Exception as e:
            self.logger.error(f" [X] {e}")
            self.logger.info(" [*] Stopping data generation.")
        finally:
            # close the kafka producer
            self._instance.close()
