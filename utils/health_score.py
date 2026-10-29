
def calculate_resource_health(usage):
    usage = max(0, min(100, usage))
    return 100 - usage


def calculate_pulse_score(cpu, memory, disk, anomaly=None):
    cpu_health = calculate_resource_health(cpu)
    memory_health = calculate_resource_health(memory)
    disk_health = calculate_resource_health(disk)

    score = (
        cpu_health * 0.40
        + memory_health * 0.40
        + disk_health * 0.20
    )

    return round(score)
