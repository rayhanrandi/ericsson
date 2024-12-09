from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType
from config.logging import Logger
import pandas as pd

from config.db.clickhouse import ClickhouseClient
from classification.model import Model


class SparkProcessor:
    """
    Wrapper class for SparkSession processing pipeline.
    """
    
    # Class-level schema definition
    SCHEMA = StructType([
        StructField("timestamp", StringType(), True),
        StructField("machine_id", StringType(), True),
        StructField("temperature", StringType(), True),
        StructField("humidity", StringType(), True),
        StructField("vibration", StringType(), True),
        StructField("gyro_x", StringType(), True),
        StructField("gyro_y", StringType(), True),
        StructField("gyro_z", StringType(), True),
        StructField("accel_x", StringType(), True),
        StructField("accel_y", StringType(), True),
        StructField("accel_z", StringType(), True),
        StructField("cycle_time", StringType(), True),
        StructField("hour", StringType(), True),
        StructField("day_of_week", StringType(), True),
        StructField("month", StringType(), True),
        StructField("shift", StringType(), True),
        StructField("machine_type", StringType(), True),
        StructField("machine_age", StringType(), True),
        StructField("operator_id", StringType(), True),
        StructField("material_type", StringType(), True),
        StructField("days_since_last_maintenance", StringType(), True)
    ])


    def __init__(
        self,
        kafka_bootstrap_servers: str,
        kafka_topic: str,
        batch_size: int = 100,
        checkpoint_path: str = "./processor/checkpoint",
        model: Model =None,
        db: ClickhouseClient =None
    ) -> None:
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.kafka_topic = kafka_topic
        self.batch_size = batch_size
        self.checkpoint_path = checkpoint_path
        self.model = model
        self.db_client = db
        self._spark = SparkSession.builder \
            .appName("SparkDataProcessor") \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3") \
            .getOrCreate()
        self.logger = Logger().setup_logger('consumer')

    def process(self) -> None:
        """
        Start data processing pipeline for updated JSON format.
        """
        # Read data from Kafka
        self._df = self._spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", self.kafka_bootstrap_servers) \
            .option("subscribe", self.kafka_topic) \
            .option("startingOffsets", "latest") \
            .option("maxOffsetsPerTrigger", self.batch_size) \
            .option("failOnDataLoss", "false") \
            .load()

        # Parse JSON messages
        kafka_df = self._df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
        parsed_df = kafka_df.select(
            col("key"),
            from_json(col("value"), SparkProcessor.SCHEMA).alias("data")
        )

        # Flatten columns
        flat_df = parsed_df.select(
            col("data.*")
        )

        # Add predictions
        def predict_batch(batch_df, batch_id):
            # Convert Spark DataFrame to Pandas
            pandas_df = batch_df.toPandas()

            # Process and predict
            results = []
            for _, row in pandas_df.iterrows():
                message = row.to_dict()
                        # Format timestamp
                if "timestamp" in message:
                    try:
                        message["timestamp"] = datetime.strptime(message["timestamp"], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")
                    except ValueError as e:
                        print(f"Error parsing timestamp for message {message}: {e}")
                        continue
                    
                prediction = self.model.process_message(message)
                message["prediction"] = prediction
                results.append(message)
            try:
                self.db_client.execute_insert_batch(results)
                self.logger.info("Batch data successfully inserted.")
            except Exception as e:
                self.logger.error(f"Error during batch insertion: {e}")


        # Use foreachBatch to process predictions
        self._query = flat_df.writeStream \
            .outputMode("append") \
            .foreachBatch(predict_batch) \
            .option("checkpointLocation", self.checkpoint_path) \
            .start()

        self._query.awaitTermination()
