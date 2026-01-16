To run Spark Streaming job (Local WSL):
1. Ensure Kafka is running and producer is sending messages to topic `traffic-data`
2. Run Spark structured streaming:

/opt/spark/bin/spark-submit \
  --master local[*] \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.13:4.1.1 \
  --jars ~/jars/postgresql-42.7.3.jar \
  sparkstreaming.py

3. Verify PostgreSQL inserts:
   SELECT COUNT(*) FROM realtimetraffic;

