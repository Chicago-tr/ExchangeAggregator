import logging
import multiprocessing as mp
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "python_service" / "src"))
os.chdir(Path(__file__).parent)


def run_api():
    """TypeScript api via subprocess (runs continuously)"""

    try:
        subprocess.run(
            ["npm", "run", "start", "--prefix=typescript_service"], check=True
        )
    except Exception:
        subprocess.run(["npm", "run", "dev", "--prefix=typescript_service"], check=True)


def run_spark_analysis():
    """Spark analysis every 2 minutes"""
    from python_service.src.main import main as spark_main

    while True:
        try:
            spark_main()
            print("Spark analysis complete. Next run in 2min...")
            time.sleep(120)  # 2 minutes
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Spark error: {e}")
            time.sleep(10)


def run_dash():
    """Dash app hosting"""
    print("📈 Starting Dash Dashboard (:8050)...")
    process = subprocess.Popen(
        ["python", "python_service/src/dash/app.py"],
        cwd=os.getcwd(),
        stdout=subprocess.DEVNULL,  # Hides messages
        stderr=subprocess.DEVNULL,
    )
    print(f"✅ Dash running - http://127.0.0.1:8050/")

    process.wait()


def signal_handler(signum, frame):
    """Shutdown on Ctrl+C"""
    print("\n Shutting down all services...")
    sys.exit(0)


logging.getLogger().setLevel(logging.WARNING)
logging.getLogger("pyspark").setLevel(logging.WARNING)
logging.getLogger("dash").setLevel(logging.WARNING)
logging.getLogger("werkzeug").setLevel(logging.WARNING)
logging.getLogger("psycopg2").setLevel(logging.WARNING)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    print("Starting Cross-Exchange Analytics Platform (Ctrl+C to stop)")
    print("=" * 60)
    print("ETL (TypeScript)  | Spark Analysis | Dash (:8050)")
    print("=" * 60)

    processes = [
        mp.Process(target=run_api, name="ETL", daemon=True),
        mp.Process(target=run_spark_analysis, name="Spark", daemon=True),
        mp.Process(target=run_dash, name="Dash", daemon=True),
    ]

    for p in processes:
        p.start()
        print(f"{p.name} process started (PID: {p.pid})")

    try:
        # this should wait for processes
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("\n All services stopped cleanly!")
