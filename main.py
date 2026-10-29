
import threading

from waitress import serve

from app import create_app
from collector.collector_service import start_collection


app = create_app()


def start_background_collector():
    collector_thread = threading.Thread(
        target=start_collection,
        name="PulseMonitorCollector",
        daemon=True
    )
    collector_thread.start()


if __name__ == "__main__":
    start_background_collector()

    print("Pulse Monitor - Production Server")
    print("----------------------------------")
    print("Dashboard: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop.\n")

    try:
        serve(
            app,
            host="127.0.0.1",
            port=5000,
            threads=4
        )
    except KeyboardInterrupt:
        print("\nPulse Monitor is shutting down.")
