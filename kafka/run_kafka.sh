#!/bin/bash
set -e

echo "=== Creating Kafka topic: traffic-data ==="

/usr/local/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 \
  --create --if-not-exists \
  --topic traffic-data \
  --partitions 1 \
  --replication-factor 1

echo "=== Listing topics ==="
/usr/local/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list

echo "=== Starting Kafka Producer (kafkaproducer.py) ==="
python3 kafkaproducer.py
