import json
import random
import time
from kafka import KafkaProducer

# Configuration Kafka
KAFKA_BROKER = "localhost:9092"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def generate_sensor_data(sensor_id):
    temperature = round(random.uniform(60, 90), 2)
    vibration = round(random.uniform(0.01, 0.1), 3)

    # Anomalie rare
    label = 1 if temperature > 85 or vibration > 0.08 else 0

    return {
        "sensor_id": sensor_id,
        "temperature": temperature,
        "vibration": vibration,
        "label": label
    }

print("🚀 Envoi des données capteurs vers Kafka...")

while True:
    data_node_1 = generate_sensor_data("node-1")
    data_node_2 = generate_sensor_data("node-2")

    producer.send("sensor-data-node-1", value=data_node_1)
    producer.send("sensor-data-node-2", value=data_node_2)

    print("Node-1:", data_node_1)
    print("Node-2:", data_node_2)
    print("-" * 50)

    time.sleep(2)