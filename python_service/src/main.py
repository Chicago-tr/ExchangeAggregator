import os
import time

from spark import run_spark

os.environ["SPARK_LOG_LEVEL"] = "ERROR"
os.environ["PYSPARK_LOG_LEVEL"] = "ERROR"


def main():

    print("==========================================")
    print("Running analysis...")
    print("==========================================")
    run_spark()
    # print("==========================================")
    # print("Analysis can be viewed with command: 'python3 dashapp.py'")
    # print("==========================================")

    return


if __name__ == "__main__":
    main()
