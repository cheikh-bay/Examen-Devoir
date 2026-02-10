import pandas as pd
import json
import time
import random
from kafka import KafkaProducer

# =====================
# CONFIG
# =====================
TOPIC = "transactions"
BOOTSTRAP_SERVERS = "localhost:9092"

EDGE_FILES = {
    "nouakchott": "data/transactions_nouakchott.csv",
    "rosso": "data/transactions_rosso.csv",
    "kaedi": "data/transactions_kaedi.csv"
}

BURST_SIZE = 40        # 🔥 nombre de transactions envoyées d’un coup
PAUSE_BETWEEN_BURSTS = 2  # pause entre rafales (secondes)

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

print("🚀 Génération massive de transactions...")

transaction_id = 0

while True:  # streaming continu

    for edge_node, file_path in EDGE_FILES.items():

        df = pd.read_csv(file_path).sample(BURST_SIZE, replace=True)

        for _, row in df.iterrows():

            fraud = random.choice([0, 0, 0, 1, 2, 3])  

            message = {
                "transaction_id": transaction_id,
                "amount": round(random.uniform(50, 5000), 2),
                "edge_node": edge_node,
                "fraud": fraud,
                "score": round(random.uniform(0, 1) + fraud * 0.8, 2),
                "timestamp": time.time()
            }

            producer.send(TOPIC, value=message)
            transaction_id += 1

        print(f"✅ {BURST_SIZE} transactions envoyées depuis {edge_node}")

    producer.flush()
    time.sleep(PAUSE_BETWEEN_BURSTS)
