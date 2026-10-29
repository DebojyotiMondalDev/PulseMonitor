
import sys
from pathlib import Path

import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


if getattr(sys, "frozen", False):
    PROJECT_ROOT = Path(sys._MEIPASS)
else:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_DIR = PROJECT_ROOT / "data" / "public_dataset"
TRAIN_RATIO = 0.70

METRICS = {
    "cpu_usage": {
        "file": "cpu_usage.csv",
        "label_file": "event_logs/event_logs_cpu.csv",
        "label": "CPU Usage",
        "unit": "%"
    },
    "memory_usage": {
        "file": "memory_usage.csv",
        "label_file": "event_logs/event_logs_memory.csv",
        "label": "Memory Usage",
        "unit": "%"
    },
    "memory_used": {
        "file": "memory_used.csv",
        "label_file": "event_logs/event_logs_memory.csv",
        "label": "Memory Used",
        "unit": "dataset units"
    },
    "network_response_time_a": {
        "file": "network_response_time_a.csv",
        "label_file": "event_logs/event_logs_network.csv",
        "label": "Network Response Time A",
        "unit": "dataset units"
    },
    "network_response_time_b": {
        "file": "network_response_time_b.csv",
        "label_file": "event_logs/event_logs_network.csv",
        "label": "Network Response Time B",
        "unit": "dataset units"
    },
    "network_response_time_diff": {
        "file": "network_response_time_diff.csv",
        "label_file": "event_logs/event_logs_network.csv",
        "label": "Network Response Time Difference",
        "unit": "dataset units"
    }
}


def analyze_public_metric(metric_key):
    if metric_key not in METRICS:
        raise ValueError("Unknown public dataset metric.")

    config = METRICS[metric_key]
    data = pd.read_csv(DATASET_DIR / config["file"])

    data["Time"] = pd.to_datetime(data["Time"], errors="coerce")
    data["Value"] = pd.to_numeric(data["Value"], errors="coerce")

    event_path = DATASET_DIR / config["label_file"]
    events = pd.read_csv(event_path)

    actual_all = [0] * len(data)

    for _, event in events.iterrows():
        try:
            start = max(0, int(event["start_point"]))
            end = min(len(data) - 1, int(event["end_point"]))

            if end >= start:
                for idx in range(start, end + 1):
                    actual_all[idx] = 1
        except (TypeError, ValueError, KeyError):
            continue

    valid_mask = (
        data["Time"].notna()
        & data["Value"].notna()
        & data["Value"].ne(-99999)
    )

    valid_positions = data.index[valid_mask].tolist()
    actual = [actual_all[idx] for idx in valid_positions]

    data = data.loc[valid_mask].copy().reset_index(drop=True)

    if len(data) < 10:
        raise ValueError("Not enough valid observations for evaluation.")

    features = pd.DataFrame({
        "value": data["Value"],
        "change": data["Value"].diff().fillna(0),
        "rolling_mean": data["Value"].rolling(
            5, min_periods=1
        ).mean(),
        "rolling_std": data["Value"].rolling(
            5, min_periods=1
        ).std().fillna(0)
    })

    split_index = int(len(data) * TRAIN_RATIO)

    train_features = features.iloc[:split_index]
    test_features = features.iloc[split_index:]

    actual_test = actual[split_index:]
    test_data = data.iloc[split_index:].reset_index(drop=True)

    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42
    )

    model.fit(train_features)

    predictions = model.predict(test_features)
    predicted = [1 if value == -1 else 0 for value in predictions]

    precision = precision_score(
        actual_test, predicted, zero_division=0
    )
    recall = recall_score(
        actual_test, predicted, zero_division=0
    )
    f1 = f1_score(
        actual_test, predicted, zero_division=0
    )

    tn, fp, fn, tp = confusion_matrix(
        actual_test, predicted, labels=[0, 1]
    ).ravel()

    step = max(1, len(test_data) // 500)
    chart_rows = []

    for idx in range(0, len(test_data), step):
        chart_rows.append({
            "time": test_data.iloc[idx]["Time"].strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "value": round(float(test_data.iloc[idx]["Value"]), 4),
            "actual": actual_test[idx],
            "predicted": predicted[idx]
        })

    return {
        "metric": metric_key,
        "label": config["label"],
        "unit": config["unit"],
        "total_records": int(len(test_data)),
        "actual_event_points": int(sum(actual_test)),
        "predicted_anomalies": int(sum(predicted)),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1_score": round(float(f1), 4),
        "true_positives": int(tp),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_negatives": int(tn),
        "evaluation_method": "Chronological 70/30 holdout",
        "training_records": int(split_index),
        "test_records": int(len(test_data)),
        "chart": chart_rows
    }
