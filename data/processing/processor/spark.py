from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json

from config.logging import Logger


class SparkProcessor:
    """
    Wrapper class for SparkSession processing pipeline.
    """
    def __init__(
        self, 
        kafka_bootstrap_servers: str, 
        kafka_topic: str, 
        batch_size: int = 100,
        checkpoint_path: str = "./processor/checkpoint"
    ) -> None:
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.kafka_topic = kafka_topic
        self.batch_size = batch_size
        self.checkpoint_path = checkpoint_path
        self._spark = SparkSession.builder \
            .appName("SparkDataProcessor") \
            .getOrCreate()
        self.logger = Logger().setup_logger('consumer')

    def process(self) -> None:
        """
        Start data processing pipeline.
        """
        # define data stream source
        self._df = self._spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", self.kafka_bootstrap_servers) \
            .option("subscribe", self.kafka_topic) \
            .option("startingOffsets", "latest") \
            .option("maxOffsetsPerTrigger", self.batch_size) \
            .load()
        # extract key & value as strings (default binary)
        self.df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
        print(self._df.head)
        # define sink
        self._query = self._df.writeStream \
            .outputMode("append") \
            .format("console") \
            .option("checkpointLocation", self.checkpoint_path) \
            .start()
        self._query.awaitTermination()