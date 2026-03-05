from datetime import datetime

from pyspark.conf import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from update import update_ts

PJAR = "/opt/homebrew/Cellar/apache-spark/4.1.1/libexec/jars/postgresql-42.7.10.jar"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "arb"

jdbc_url = "jdbc:postgresql://localhost:5432/arb"

spark = (
    SparkSession.builder.appName("CryptoAnalysis")
    .config("spark.jars", PJAR)
    .getOrCreate()
)
# Read etl state to extract the most recently analyzed data date (will use this so we don't analyse the same data twice)
etl_df = (
    spark.read.format("jdbc")
    .option("url", jdbc_url)
    .option("dbtable", "etl_state")
    .option("driver", "org.postgresql.Driver")
    .load()
    .filter(F.col("id") == "bars_and_cross_spread_1m")
)
etl_row = etl_df.select("last_processed").head(1)
if etl_row:
    last_processed_ts = etl_row[0]["last_processed"]
    # last_processed_ts = "1970-01-01 00:00:00+00"
else:
    default_date = datetime.fromtimestamp(0)
    last_processed_ts = default_date
    # last_processed_ts = "1970-01-01 00:00:00+00"

quotes_df = (
    spark.read.format("jdbc")
    .option("url", jdbc_url)
    .option("dbtable", "prices")
    .option("driver", "org.postgresql.Driver")
    .load()
)
# cutoff = "2026-03-03 19:48:00"

quotes_df_filtered = quotes_df.filter(F.col("TimeStamp") > last_processed_ts)

max_ts_row = quotes_df_filtered.agg(F.max("TimeStamp").alias("max_ts")).head(1)

if max_ts_row and max_ts_row[0]["max_ts"] is not None:
    new_last_ts = max_ts_row[0]["max_ts"]

    print("Updating last_processed to:", new_last_ts)
    update_ts(new_last_ts)
# table with derived columns
quotes_with_features = (
    quotes_df_filtered.withColumn(
        "mid_price", F.round(((F.col("Bid") + F.col("Ask")) / 2), 2)
    )
    .withColumn("spread", F.col("Ask") - F.col("Bid"))
    .withColumn(
        "rel_spread_bps", (F.col("spread") / F.col("mid_price")) * F.lit(10000.0)
    )
)

# bucket into minutes
quotes_bucketed = quotes_with_features.withColumn(
    "bar_ts", F.date_trunc("minute", F.col("TimeStamp"))
)

# use buckets to aggregate by exchange, asset, and time
bars_1m = quotes_bucketed.groupBy("ExchangeId", "SymbolId", "bar_ts").agg(
    F.first("mid_price").alias("open_mid"),
    F.max("mid_price").alias("high_mid"),
    F.min("mid_price").alias("low_mid"),
    F.last("mid_price").alias("close_mid"),
    F.avg("spread").alias("avg_spread"),
    F.avg("rel_spread_bps").alias("avg_rel_spread_bps"),
)

cross_ex_spread = (
    bars_1m.groupBy("SymbolId", "bar_ts")
    .agg(
        F.min("close_mid").alias("min_mid"),
        F.max("close_mid").alias("max_mid"),
    )
    .withColumn("cross_spread", F.col("max_mid") - F.col("min_mid"))
    .withColumn(
        "cross_spread_bps", (F.col("cross_spread") / F.col("min_mid")) * F.lit(10000.0)
    )
)


cross_ex_spread.show(10, truncate=False)

# bars_1m.show(10, truncate=False)
# quotes_with_features.printSchema()
# quotes_with_features.show(5, truncate=False)
quotes_bucketed.printSchema()
quotes_bucketed.show(5)


# Writes analysis tables to psql database
bars_1m.write.format("jdbc").option("url", jdbc_url).option(
    "dbtable", "bars_1m"
).option("driver", "org.postgresql.Driver").mode("append").save()


cross_ex_spread.write.format("jdbc").option("url", jdbc_url).option(
    "dbtable", "cross_ex_spread_1m"
).option("driver", "org.postgresql.Driver").mode("append").save()

bars = bars_1m.dropDuplicates()
c = cross_ex_spread.dropDuplicates()
spark.stop()
