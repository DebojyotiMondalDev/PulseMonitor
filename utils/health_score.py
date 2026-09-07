def calculate_resource_health(usage):
    """
    Convert resource utilization into a health score from 0 to 100.
    Lower utilization receives a higher health score.
    """

    usage = max(0, min(100, usage))

    return 100 - usage


def calculate_pulse_score(cpu, memory, disk, anomaly):
    """
    Calculate the overall Pulse Health Score.

    Weights:
    CPU       : 30%
    Memory    : 30%
    Disk      : 15%
    AI status : 25%
    """

    cpu_health = calculate_resource_health(cpu)
    memory_health = calculate_resource_health(memory)
    disk_health = calculate_resource_health(disk)

    if anomaly:
        ai_health = 0
    else:
        ai_health = 100

    score = (
        cpu_health * 0.30
        + memory_health * 0.30
        + disk_health * 0.15
        + ai_health * 0.25
    )

    return round(score)