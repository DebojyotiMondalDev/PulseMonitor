import threading

from app import create_app
from collector.collector_service import start_collection


app = create_app()


def start_background_collector():
    collector_thread = threading.Thread(
        target=start_collection,
        daemon=True
    )

    collector_thread.start()


if __name__ == "__main__":
    start_background_collector()

    app.run(
        debug=True,
        use_reloader=False
    )