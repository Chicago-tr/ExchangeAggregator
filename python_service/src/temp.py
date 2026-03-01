from pyspark.conf import SparkConf
from pyspark.sql import SparkSession

PJAR = "path to postgresql.jar in apache-spark directory"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "arb"
DB_URL = "url to database"
jdbc_url = "jdbc:postgresql://localhost:5432/arb"

spark = (
    SparkSession.builder.appName("CryptoAnalysis")
    .config("spark.jars", PJAR)
    .getOrCreate()
)


quotes_df = (
    spark.read.format("jdbc")
    .option("url", jdbc_url)
    .option("dbtable", "prices")
    .option("driver", "org.postgresql.Driver")
    .load()
)

# test code
quotes_df.printSchema()
quotes_df.show(5)
spark.stop()
