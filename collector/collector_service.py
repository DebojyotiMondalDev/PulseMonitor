import time
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from collector.system_monitor import get_system_metrics
from database.database import initialize_database, insert_metrics


COLLECTION_INTERVAL = 5


def start_collection():
    """
    Continuously collect system metrics and store them in SQLite.
    """

    initialize_database()

    print("Pulse Monitor - Data Collection Service")
    print("----------------------------------------")
    print(f"Collection interval: {COLLECTION_INTERVAL} seconds")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            metrics = get_system_metrics()

            insert_metrics(metrics)

            print(
                f"[{metrics['timestamp']}] "
                f"CPU: {metrics['cpu_usage']:.1f}% | "
                f"RAM: {metrics['memory_usage']:.1f}% | "
                f"Disk: {metrics['disk_usage']:.1f}% | "
                f"Processes: {metrics['process_count']}"
            )

            time.sleep(COLLECTION_INTERVAL)

    except KeyboardInterrupt:
        print("\nPulse Monitor collection stopped.")


if __name__ == "__main__":
    start_collection()