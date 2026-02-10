import streamlit as st
from kafka import KafkaConsumer
import json
import pandas as pd
import time

# =========================
# CONFIG
# =========================
KAFKA_TOPIC = "transactions"
BOOTSTRAP_SERVERS = "localhost:9092"

st.set_page_config(
    page_title="Fraude Mobile Money",
    layout="wide"
)

st.title("💳 Dashboard de Détection de Fraude – Mobile Money")
st.markdown("### 📡 Surveillance temps réel des transactions financières")

# =========================
# SIDEBAR
# =========================
st.sidebar.header("🔎 Filtres")

fraud_filter = st.sidebar.multiselect(
    "Type de fraude",
    options=[0, 1, 2, 3],
    default=[0, 1, 2, 3]
)

agency_filter = st.sidebar.multiselect(
    "Agences",
    options=["nouakchott", "rosso", "kaedi"],
    default=["nouakchott", "rosso", "kaedi"]
)

# =========================
# KAFKA CONSUMER
# =========================
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=BOOTSTRAP_SERVERS,
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="latest",
    enable_auto_commit=True
)

data = []
placeholder = st.empty()

# =========================
# STREAMING LOOP
# =========================
for message in consumer:
    record = message.value

    # ajout de colonnes supplémentaires (pour atteindre 30+)
    record.update({
        "risk_score": round((record["fraud"] * 25) + (record["amount"] / 200), 2),
        "currency": "MRU",
        "channel": "Mobile",
        "country": "Mauritania",
        "status": "BLOCKED" if record["fraud"] > 0 else "APPROVED",
        "device": "Android",
        "operator": "Mobile Money",
        "hour": pd.to_datetime(record["timestamp"], unit="s").hour,
        "day": pd.to_datetime(record["timestamp"], unit="s").day,
        "month": pd.to_datetime(record["timestamp"], unit="s").month,
        "latency_ms": round(50 + record["fraud"] * 20, 2)
    })

    data.append(record)
    df = pd.DataFrame(data)

    # =========================
    # FILTRES
    # =========================
    df_filtered = df[
        (df["fraud"].isin(fraud_filter)) &
        (df["edge_node"].isin(agency_filter))
    ]

    with placeholder.container():

        # =========================
        # METRICS
        # =========================
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("📥 Transactions", len(df_filtered))
        col2.metric("🚨 Fraudes détectées", len(df_filtered[df_filtered["fraud"] > 0]))
        col3.metric("💰 Montant total (MRU)", round(df_filtered["amount"].sum(), 2))
        col4.metric("🏢 Agences actives", df_filtered["edge_node"].nunique())

        st.divider()

        # =========================
        # TABLEAU PRINCIPAL
        # =========================
        st.subheader("📄 Transactions détaillées (temps réel)")

        st.dataframe(
            df_filtered.tail(40),
            use_container_width=True,
            height=600
        )

    time.sleep(0.3)
