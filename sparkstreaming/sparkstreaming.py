from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, lit
from pyspark.sql.types import StructType, StructField, IntegerType, LongType, DoubleType

def main():
    spark = SparkSession.builder \
        .appName("TrafficAdvisorStreamingToPostgres") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    # Kafka JSON schema
    schema = StructType([
        StructField("sensor_id", IntegerType(), True),
        StructField("speed", IntegerType(), True),
        StructField("volume", IntegerType(), True),
        StructField("timestamp", LongType(), True)
    ])

    # Read stream from Kafka
    kafka_df = spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "traffic-data") \
        .option("startingOffsets", "latest") \
        .load()

    parsed = kafka_df.select(from_json(col("value").cast("string"), schema).alias("data")) \
                     .select("data.*")

    # Transform into DB schema expected by Flask
    out = parsed \
        .withColumn("location", col("sensor_id").cast("string")) \
        .withColumnRenamed("volume", "current") \
        .withColumn("historical", col("current").cast(DoubleType())) \
        .withColumn("predicted", col("current")) \
        .withColumn("level", lit("High")) \
        .withColumn("latitude", lit(37.40) + (col("sensor_id") * lit(0.001))) \
        .withColumn("longitude", lit(-122.10) - (col("sensor_id") * lit(0.001))) \
        .withColumn("direction", lit("N")) \
        .withColumn("lane", lit(2)) \
        .withColumn("type", lit("Road")) \
        .withColumn("highway", lit("Yes")) \
        .select(
            "location", "latitude", "longitude", "direction", "lane",
            "type", "highway", "current", "historical", "predicted", "level"
        )

    # Write micro-batch to PostgreSQL
    def write_to_postgres(batch_df, batch_id):
        if batch_df.rdd.isEmpty():
            return

        jdbc_url = "jdbc:postgresql://127.0.0.1:5432/postgres"
        props = {
            "user": "postgres",
            "password": "postgres",
            "driver": "org.postgresql.Driver"
        }

        # ✅ Write directly into main table used by Flask
        batch_df.write.jdbc(
            url=jdbc_url,
            table="realtimetraffic",
            mode="append",
            properties=props
        )

    query = out.writeStream \
        .foreachBatch(write_to_postgres) \
        .outputMode("append") \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    main()
