import sqlite3
import pandas as pd
from pathlib import Path


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database location
DATABASE_FILE = BASE_DIR / "data" / "pulse_monitor.db"


def get_metrics(limit=None):
    """
    Retrieve system metrics from the SQLite database
    and return them as a Pandas DataFrame.
    """

    connection = sqlite3.connect(DATABASE_FILE)

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

        dataframe = dataframe.sort_values("id")

    else:
        dataframe = pd.read_sql_query(
            query,
            connection
        )

    connection.close()

    return dataframe


if __name__ == "__main__":
    df = get_metrics()

    print("Pulse Monitor - Historical Metrics")
    print("-----------------------------------")
    print(f"Total records: {len(df)}")
    print()

    print(df.tail())