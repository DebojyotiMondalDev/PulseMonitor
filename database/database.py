import sqlite3
from pathlib import Path


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database directory
DATABASE_DIR = BASE_DIR / "data"

# Database file
DATABASE_FILE = DATABASE_DIR / "pulse_monitor.db"


def get_connection():
    """
    Create and return a connection to the SQLite database.
    """

    DATABASE_DIR.mkdir(exist_ok=True)

    connection = sqlite3.connect(DATABASE_FILE)

    return connection


def initialize_database():
    """
    Create the system_metrics table if it does not already exist.
    """

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
    """
    Insert one system-metrics record into the database.
    """

    connection = get_connection()
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
    connection.close()

if __name__ == "__main__":
    initialize_database()
    print("Pulse Monitor database initialized successfully.")