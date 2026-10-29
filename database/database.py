
import os
import sqlite3
from pathlib import Path


DATABASE_DIR = (
    Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local")))
    / "PulseMonitor"
)

DATABASE_FILE = DATABASE_DIR / "pulse_monitor.db"


def get_connection():
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DATABASE_FILE)


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            cpu_usage REAL NOT NULL,
            memory_usage REAL NOT NULL,
            disk_usage REAL NOT NULL,
            bytes_sent INTEGER NOT NULL,
            bytes_received INTEGER NOT NULL,
            process_count INTEGER NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def insert_metrics(metrics):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO system_metrics (
                timestamp,
                cpu_usage,
                memory_usage,
                disk_usage,
                bytes_sent,
                bytes_received,
                process_count
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            metrics["timestamp"],
            metrics["cpu_usage"],
            metrics["memory_usage"],
            metrics["disk_usage"],
            metrics["bytes_sent"],
            metrics["bytes_received"],
            metrics["process_count"]
        ))

        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    initialize_database()
    print(f"Pulse Monitor database initialized: {DATABASE_FILE}")
