from utils.health_score import calculate_pulse_score
from flask import Blueprint, render_template, jsonify

from database.queries import get_metrics
from models.anomaly_detector import detect_anomalies


main = Blueprint("main", __name__)


@main.route("/")
def dashboard():
    data = get_metrics()

    if data.empty:
        return render_template(
            "dashboard.html",
            has_data=False
        )

    results = detect_anomalies(data)

    latest = results.iloc[-1]

    anomaly_count = int(
        (results["anomaly_label"] == -1).sum()
    )

    latest_anomaly = latest["anomaly_label"] == -1

    pulse_score = calculate_pulse_score(
    cpu=latest["cpu_usage"],
    memory=latest["memory_usage"],
    disk=latest["disk_usage"],
    anomaly=latest_anomaly
    )
    return render_template(
        "dashboard.html",
        has_data=True,
        cpu=latest["cpu_usage"],
        memory=latest["memory_usage"],
        disk=latest["disk_usage"],
        processes=int(latest["process_count"]),
        records=len(results),
        anomaly_count=anomaly_count,
        latest_anomaly=latest_anomaly,
        pulse_score=pulse_score
    )

@main.route("/api/history")
def history():
    data = get_metrics()

    if data.empty:
        return jsonify([])

    results = detect_anomalies(data)

    history_data = []

    for _, row in results.tail(100).iterrows():
        history_data.append({
            "timestamp": row["timestamp"],
            "cpu": round(float(row["cpu_usage"]), 2),
            "memory": round(float(row["memory_usage"]), 2),
            "disk": round(float(row["disk_usage"]), 2),
            "anomaly": int(row["anomaly_label"])
        })

    return jsonify(history_data)