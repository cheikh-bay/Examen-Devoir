from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, avg
from pyspark.sql.types import StructType, StringType, DoubleType, IntegerType
import json

spark = SparkSession.builder \
    .appName("FogNode1") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Schéma des données capteurs
schema = StructType() \
    .add("sensor_id", StringType()) \
    .add("temperature", DoubleType()) \
    .add("vibration", DoubleType()) \
    .add("label", IntegerType())

# Lecture Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:29092") \
    .option("subscribe", "sensor-data-node-1") \
    .load()

parsed = df.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

# Calcul du modèle local (moyenne)
model = parsed.groupBy().agg(
    avg("temperature").alias("avg_temp"),
    avg("vibration").alias("avg_vib")
)

def send_weights(batch_df, batch_id):
    if batch_df.count() == 0:
        return

    row = batch_df.collect()[0]
    #weight = (row.avg_temp + 100 * row.avg_vib) / 2
    weight = ((row.avg_temp or 0) +100 * (row.avg_vib or 0)) / 2


    output = {
        "node_id": "fog-1",
        "weight": round(weight, 4),
        "samples": batch_df.count()
    }

    spark.createDataFrame(
        [(json.dumps(output),)],
        ["value"]
    ).selectExpr("CAST(value AS STRING)") \
     .write \
     .format("kafka") \
     .option("kafka.bootstrap.servers", "kafka:29092") \
     .option("topic", "model-weights") \
     .save()

    print("Fog-1 -> poids envoyé:", output)

query = model.writeStream \
    .foreachBatch(send_weights) \
    .outputMode("complete") \
    .start()

query.awaitTermination()