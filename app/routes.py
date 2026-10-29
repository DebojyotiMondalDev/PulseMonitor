from utils.health_score import calculate_pulse_score
from flask import Blueprint, render_template, jsonify

from database.queries import get_metrics
from models.anomaly_detector import detect_anomalies
from models.public_dataset_analysis import METRICS, analyze_public_metric


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
    import pandas as pd

    data = get_metrics()

    if data.empty:
        return jsonify([])

    results = detect_anomalies(data)

    results["parsed_timestamp"] = pd.to_datetime(
        results["timestamp"],
        errors="coerce"
    )

    results = results.dropna(subset=["parsed_timestamp"])
    results = results.sort_values("parsed_timestamp")

    if results.empty:
        return jsonify([])

    latest_time = results["parsed_timestamp"].max()
    cutoff_time = latest_time - pd.Timedelta(minutes=30)

    recent_data = results[
        results["parsed_timestamp"] >= cutoff_time
    ].tail(100)

    history_data = []

    for _, row in recent_data.iterrows():
        history_data.append({
            "timestamp": row["timestamp"],
            "cpu": round(float(row["cpu_usage"]), 2),
            "memory": round(float(row["memory_usage"]), 2),
            "disk": round(float(row["disk_usage"]), 2),
            "anomaly": int(row["anomaly_label"])
        })

    return jsonify(history_data)


@main.route("/dataset-analysis")
def dataset_analysis():
    return render_template(
        "dataset_analysis.html",
        metrics=[
            {"key": key, "label": value["label"]}
            for key, value in METRICS.items()
        ]
    )


@main.route("/api/public-dataset/<metric_key>")
def public_dataset_results(metric_key):
    try:
        return jsonify(analyze_public_metric(metric_key))
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except FileNotFoundError:
        return jsonify({
            "error": "Public dataset files are missing from data/public_dataset."
        }), 500