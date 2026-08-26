import psutil
import time


def get_system_metrics():
    """
    Collect current system performance metrics.
    """

    # CPU usage percentage
    cpu_usage = psutil.cpu_percent(interval=1)

    # Memory usage percentage
    memory = psutil.virtual_memory()
    memory_usage = memory.percent

    # Disk usage percentage
    disk = psutil.disk_usage("C:\\")
    disk_usage = disk.percent

    # Network statistics
    network = psutil.net_io_counters()

    # Running processes
    process_count = len(psutil.pids())

    return {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage,
        "disk_usage": disk_usage,
        "bytes_sent": network.bytes_sent,
        "bytes_received": network.bytes_recv,
        "process_count": process_count,
    }


if __name__ == "__main__":
    print("Pulse Monitor - System Resource Collector")
    print("------------------------------------------")

    metrics = get_system_metrics()

    for key, value in metrics.items():
        print(f"{key}: {value}")