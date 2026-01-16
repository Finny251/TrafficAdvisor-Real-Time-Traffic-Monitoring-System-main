#!/bin/bash
set -e

echo "=== Starting Spark Streaming (WSL local mode) ==="

# If you truly updated Spark to latest, Structured Streaming requires this package:
# NOTE: Change 3.5.1 to YOUR spark version if different.
SPARK_KAFKA_PACKAGE="org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1"

 /usr/local/spark/bin/spark-submit \
  --master local[*] \
  --packages $SPARK_KAFKA_PACKAGE \
  sparkstreaming.py
