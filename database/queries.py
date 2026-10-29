
import os
import sqlite3
from pathlib import Path

import pandas as pd


DATABASE_DIR = (
    Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local")))
    / "PulseMonitor"
)

DATABASE_FILE = DATABASE_DIR / "pulse_monitor.db"


def get_metrics(limit=None):
    if not DATABASE_FILE.exists():
        return pd.DataFrame(columns=[
            "id",
            "timestamp",
            "cpu_usage",
            "memory_usage",
            "disk_usage",
            "bytes_sent",
            "bytes_received",
            "process_count"
        ])

    query = """
        SELECT
            id,
            timestamp,
            cpu_usage,
            memory_usage,
            disk_usage,
            bytes_sent,
            bytes_received,
            process_count
        FROM system_metrics
        ORDER BY id ASC
    """

    connection = sqlite3.connect(DATABASE_FILE)

    try:
        if limit:
            query = """
                SELECT
                    id,
                    timestamp,
                    cpu_usage,
                    memory_usage,
                    disk_usage,
                    bytes_sent,
                    bytes_received,
                    process_count
                FROM system_metrics
                ORDER BY id DESC
                LIMIT ?
            """

            dataframe = pd.read_sql_query(
                query,
                connection,
                params=(limit,)
            )

            return dataframe.sort_values("id")

        return pd.read_sql_query(query, connection)
    finally:
        connection.close()


if __name__ == "__main__":
    dataframe = get_metrics()
    print("Pulse Monitor - Historical Metrics")
    print("-----------------------------------")
    print(f"Total records: {len(dataframe)}")
    print(dataframe.tail())
