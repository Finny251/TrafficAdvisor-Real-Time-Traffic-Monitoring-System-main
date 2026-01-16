# TrafficAdvisor – Real-Time Traffic Monitoring System (Kafka + Spark Streaming + PostGIS + Flask)
TrafficAdvisor is a real-time traffic monitoring system that visualizes live traffic sensor data on a web map.
Users can click any location on the map to query the nearest traffic sensor and retrieve:
- Nearest sensor ID
- Current traffic volume (Kafka real-time stream)
- Historical traffic volume (simulated)
- Predicted traffic volume (simulated)
- Traffic level (simulated)
- Road details (type/highway/lanes)
■ This repository is configured for LOCAL execution using WSL (Ubuntu).
---
## Project Flow
Kafka Producer
➡ Kafka Topic `traffic-data`
➡ Spark Structured Streaming (Kafka → Transform → PostgreSQL)
➡ PostgreSQL + PostGIS (table: `realtimetraffic`)
➡ Flask Web Service (`/search`)
➡ Leaflet Map UI (Browser)
---
## Tech Stack
- Kafka (Confluent local setup)
- Spark 4.1.1 (Structured Streaming)
- PostgreSQL 16 + PostGIS
- Flask (Python)
- Leaflet.js + OpenStreetMap
---
# Setup & Installation (WSL)
## 1) Start PostgreSQL
sudo service postgresql start
sudo service postgresql status
## 2) Install PostGIS + Enable Extension
sudo apt update
sudo apt install postgresql postgis postgresql-16-postgis-3 -y
sudo -u postgres psql -d postgres -c "CREATE EXTENSION IF NOT EXISTS postgis;"
## 3) Create Database Table
sudo -u postgres psql -d postgres
DROP TABLE IF EXISTS realtimetraffic;
CREATE TABLE realtimetraffic (
id SERIAL PRIMARY KEY,
location TEXT,
latitude DOUBLE PRECISION,
longitude DOUBLE PRECISION,
direction TEXT,
lane INTEGER,
type TEXT,
highway TEXT,
current INTEGER,
historical DOUBLE PRECISION,
predicted INTEGER,
level TEXT,
geom geometry(Point, 4326)
);
CREATE INDEX realtimetraffic_geom_idx ON realtimetraffic USING GIST (geom);
## 4) Create Python Virtual Environment
cd /mnt/c/Users/HP/TrafficAdvisor-Real-Time-Traffic-Monitoring-System-main
sudo apt install python3.12-venv -y
python3 -m venv venv
source venv/bin/activate
pip install -U pip
pip install flask kafka-python shapely psycopg2-binary
## 5) Download PostgreSQL JDBC Driver (Spark requirement)
cd ~
mkdir -p jars
cd jars
wget https://jdbc.postgresql.org/download/postgresql-42.7.3.jar
---
# Execution Steps (WSL)
■■ Keep these terminals running.
## Terminal 1: Start ZooKeeper
/home/finny_123/confluent-7.6.0/bin/zookeeper-server-start /home/finny_123/confluent-7.6.0/etc/ka## Terminal 2: Start Kafka Broker
/home/finny_123/confluent-7.6.0/bin/kafka-server-start /home/finny_123/confluent-7.6.0/etc/kafka/## Terminal 3: Create Kafka Topic (run once)
/home/finny_123/confluent-7.6.0/bin/kafka-topics --bootstrap-server localhost:9092 --create --if-## Terminal 4: Run Kafka Producer
cd /mnt/c/Users/HP/TrafficAdvisor-Real-Time-Traffic-Monitoring-System-main
source venv/bin/activate
cd kafka
python3 kafkaproducer.py
## Terminal 5: Run Spark Streaming (Kafka → PostgreSQL)
cd /mnt/c/Users/HP/TrafficAdvisor-Real-Time-Traffic-Monitoring-System-main/sparkstreaming
/opt/spark/bin/spark-submit \
--master local[*] \
--packages org.apache.spark:spark-sql-kafka-0-10_2.13:4.1.1 \
--jars ~/jars/postgresql-42.7.3.jar \
sparkstreaming.py
## Terminal 6: Generate PostGIS geom points (required)
sudo -u postgres psql -d postgres -c "
UPDATE realtimetraffic
SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
WHERE geom IS NULL;
"
## Terminal 7: Run Flask Web App
cd /mnt/c/Users/HP/TrafficAdvisor-Real-Time-Traffic-Monitoring-System-main
source venv/bin/activate
cd flask
python3 traffic.py
Open in browser:
■ http://localhost:8080
---
# Debug Commands
## View Kafka topic messages
/home/finny_123/confluent-7.6.0/bin/kafka-console-consumer --bootstrap-server localhost:9092 --to## Check PostgreSQL row count
sudo -u postgres psql -d postgres -c "SELECT COUNT(*) FROM realtimetraffic;"
---
