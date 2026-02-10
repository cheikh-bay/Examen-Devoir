from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, avg
from pyspark.sql.types import StructType, StringType, DoubleType

# 1️⃣ Spark Session
spark = SparkSession.builder \
    .appName("CloudAggregator") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 2️⃣ Schéma des messages Kafka
schema = StructType() \
    .add("fog_id", StringType()) \
    .add("weight", DoubleType())

# 3️⃣ Lecture depuis Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:29092") \
    .option("subscribe", "model-weights") \
    .option("startingOffsets", "latest") \
    .load()

# 4️⃣ Parsing JSON
parsed_df = df.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

# 5️⃣ Agrégation globale (moyenne des poids)
global_model = parsed_df.groupBy().agg(
    avg("weight").alias("global_weight")
)

# 6️⃣ Sortie console (pour le TP)
query = global_model.writeStream \
    .outputMode("complete") \
    .format("console") \
    .option("truncate", False) \
    .start()

query.awaitTermination()