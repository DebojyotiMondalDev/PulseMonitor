import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

import pandas as pd
from sklearn.ensemble import IsolationForest


FEATURES = [
    "cpu_usage",
    "memory_usage",
    "disk_usage",
    "process_count"
]


def detect_anomalies(dataframe):
    """
    Detect unusual system behavior using Isolation Forest.

    Returns the input DataFrame with two additional columns:
    anomaly_score and anomaly_label.
    """

    if dataframe.empty:
        raise ValueError("No data available for anomaly detection.")

    if len(dataframe) < 10:
        raise ValueError(
            "At least 10 records are recommended for anomaly detection."
        )

    data = dataframe.copy()

    # Select features used by the model
    feature_data = data[FEATURES]

    # Create Isolation Forest model
    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42
    )

    # Train model and predict
    predictions = model.fit_predict(feature_data)

    # Calculate anomaly scores
    scores = model.decision_function(feature_data)

    # Store results
    data["anomaly_score"] = scores

    # Isolation Forest:
    #  1  = normal
    # -1  = anomaly
    data["anomaly_label"] = predictions

    return data


if __name__ == "__main__":
    from database.queries import get_metrics

    print("Pulse Monitor - AI Anomaly Detection")
    print("--------------------------------------")

    df = get_metrics()

    results = detect_anomalies(df)

    print("\nAnomaly Detection Results:\n")

    print(
        results[
            [
                "timestamp",
                "cpu_usage",
                "memory_usage",
                "disk_usage",
                "process_count",
                "anomaly_score",
                "anomaly_label"
            ]
        ].tail(10)
    )

    anomalies = results[results["anomaly_label"] == -1]

    print(f"\nTotal records: {len(results)}")
    print(f"Anomalies detected: {len(anomalies)}")