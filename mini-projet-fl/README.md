---

#  Federated Learning Architecture: Edge–Fog–Cloud

### Projet de Streaming de Données Distribué avec Apache Kafka & Spark

##  Présentation du Projet

Ce projet implémente une pipeline de **Federated Learning** simplifiée, structurée sur trois niveaux (Edge, Fog, Cloud). L'objectif est de démontrer comment traiter des flux de données IoT en temps réel de manière décentralisée pour minimiser la latence et préserver la bande passante.

---

##  Architecture du Système

Le schéma ci-dessous illustre le flux de données, depuis la génération au niveau des capteurs jusqu'à l'agrégation globale dans le Cloud.

![Architecture du Projet](images/architecture.png)

---

##  Stack Technique

* **Message Broker :** Apache Kafka (Inter-node communication)
* **Orchestration :** Zookeeper
* **Processing :** Spark Structured Streaming 3.5.1
* **Containerisation :** Docker & Docker Compose
* **Langage :** Python (PySpark)

---

##  Structure du Répertoire

```text
mini-projet-fl/
├── docker-compose.yml       # Infrastructure (Kafka, Zookeeper, Spark)
├── producer/
│   └── sensor_producer.py   # Simulation de capteurs (Edge)
├── fog/
│   ├── fog_node_1.py        # Worker Spark local 1
│   └── fog_node_2.py        # Worker Spark local 2
├── cloud/
│   └── aggregator.py        # Agrégateur central (Cloud)
└── README.md

```

---

##  Guide de Déploiement

### 1. Initialisation de l'Infrastructure

Lancez l'ensemble des services définis dans le fichier Compose :

```bash
docker compose up -d

```

### 2. Configuration du Messaging (Kafka)

Créez les topics nécessaires pour isoler les flux de données brutes et les poids des modèles :

```bash
# Données des capteurs
docker exec -it kafka kafka-topics --bootstrap-server kafka:29092 --create --topic sensor-data --partitions 1 --replication-factor 1

# Poids des modèles locaux
docker exec -it kafka kafka-topics --bootstrap-server kafka:29092 --create --topic model-weights --partitions 1 --replication-factor 1

```

### 3. Exécution de la Pipeline

**Étape A : Lancer la production Edge**

```bash
docker exec -it kafka python /app/producer/sensor_producer.py

```

**Étape B : Lancer les Fog Nodes (Spark)**

```bash
docker exec -it spark /opt/spark/bin/spark-submit \
  --conf spark.jars.ivy=/tmp/ivy \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 \
  /app/fog/fog_node_1.py

```

**Étape C : Lancer l'agrégateur Cloud**

```bash
docker exec -it spark /opt/spark/bin/spark-submit \
  --conf spark.jars.ivy=/tmp/ivy \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 \
  /app/cloud/aggregator.py

```

---

##  Gestion des Erreurs & Optimisations

Lors du développement, plusieurs défis techniques ont été relevés :

* **Connectivité Kafka-Spark :** Résolu par l'injection dynamique du package `--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1`.
* **Sécurité Docker :** Correction des permissions d'écriture du cache Ivy via `--conf spark.jars.ivy=/tmp/ivy`.
* **Data Quality :** Implémentation d'une logique de nettoyage pour éviter les erreurs `NoneType` lors des calculs arithmétiques sur les moyennes.

---

##  Améliorations Futures

* [ ] **Persistance :** Intégration d'une base de données NoSQL (Cassandra/MongoDB) pour l'historique des modèles globaux.
* [ ] **Monitoring :** Ajout d'un tableau de bord Grafana via Prometheus pour visualiser les métriques de performance.

---

**Auteur :** Cheikh Bay Oudaa

**Année :** 2026