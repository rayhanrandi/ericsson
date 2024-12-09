from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType, ArrayType, DoubleType, TimestampType
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
        checkpoint_path: str = "./processor/checkpoint",
        model=None
    ) -> None:
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.kafka_topic = kafka_topic
        self.batch_size = batch_size
        self.checkpoint_path = checkpoint_path
        self.model = model
        self._spark = SparkSession.builder \
            .appName("SparkDataProcessor") \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3") \
            .getOrCreate()
        self.logger = Logger().setup_logger('consumer')

    def process(self) -> None:
        """
        Start data processing pipeline.
        """
        # Define the schema of the JSON payload
        schema = StructType([
            StructField("sensor", StringType(), True),
            StructField("time", StringType(), True),  # Parse as string initially
            StructField("temp", StringType(), True),  # Keep as string if needed
            StructField("hum", StringType(), True),   # Keep as string if needed
            StructField("gyro", ArrayType(DoubleType()), True),
            StructField("accel", ArrayType(DoubleType()), True)
        ])

        # Define data stream source
        self._df = self._spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", self.kafka_bootstrap_servers) \
            .option("subscribe", self.kafka_topic) \
            .option("startingOffsets", "latest") \
            .option("maxOffsetsPerTrigger", self.batch_size) \
            .load()

        # Extract key & value as strings and parse JSON
        kafka_df = self._df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
        
        # Parse JSON into a structured DataFrame
        parsed_df = kafka_df.select(
            col("key"),
            from_json(col("value"), schema).alias("data")
        )

        # Flatten the structure into individual columns
        final_df = parsed_df.select(
            col("key"),
            col("data.sensor").alias("sensor_id"),
            col("data.time").alias("event_time"),
            col("data.temp").alias("temperature"),
            col("data.hum").alias("humidity"),
            col("data.gyro")[0].alias("gyro_x"),
            col("data.gyro")[1].alias("gyro_y"),
            col("data.gyro")[2].alias("gyro_z"),
            col("data.accel")[0].alias("accel_x"),
            col("data.accel")[1].alias("accel_y"),
            col("data.accel")[2].alias("accel_z")
        )

        # Define sink
        self._query = final_df.writeStream \
            .outputMode("append") \
            .format("console") \
            .option("truncate", "false") \
            .start()
        self._query.awaitTermination()
