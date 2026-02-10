from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType

# --- CONFIGURATION ---
KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "transactions"

# --- SCHEMA DES TRANSACTIONS ---
schema = StructType([
    StructField("Time", DoubleType(), True),
    StructField("Amount", DoubleType(), True),
    StructField("Class", IntegerType(), True),
    StructField("edge_node", StringType(), True)
])

# --- SESSION SPARK ---
spark = SparkSession.builder \
    .appName("FraudeTransactionsConsumer") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# --- LECTURE DU TOPIC KAFKA ---
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "latest") \
    .load()

# --- CONVERSION DE LA VALEUR EN JSON ---
df_parsed = df.selectExpr("CAST(value AS STRING) as json") \
    .select(from_json(col("json"), schema).alias("data")) \
    .select("data.*")

# --- AFFICHAGE EN TEMPS RÉEL ---
query = df_parsed.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", "false") \
    .start()

query.awaitTermination()
