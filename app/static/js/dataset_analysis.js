let datasetChart;

async function runDatasetAnalysis() {
    const metric = document.getElementById("metricSelect").value;
    const message = document.getElementById("datasetMessage");
    const button = document.getElementById("analyzeButton");
    button.disabled = true;
    message.textContent = "Analyzing dataset. This may take a few seconds.";

    try {
        const response = await fetch(`/api/public-dataset/${encodeURIComponent(metric)}`);
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Dataset analysis failed.");
        }

        document.getElementById("recordsValue").textContent = result.total_records.toLocaleString();
        document.getElementById("eventValue").textContent = result.actual_event_points.toLocaleString();
        document.getElementById("anomalyValue").textContent = result.predicted_anomalies.toLocaleString();
        document.getElementById("f1Value").textContent = result.f1_score.toFixed(3);
        document.getElementById("precisionValue").textContent = result.precision.toFixed(3);
        document.getElementById("recallValue").textContent = result.recall.toFixed(3);
        document.getElementById("f1DetailValue").textContent = result.f1_score.toFixed(3);
        document.getElementById("tpValue").textContent = result.true_positives.toLocaleString();
        document.getElementById("fpValue").textContent = result.false_positives.toLocaleString();
        document.getElementById("fnValue").textContent = result.false_negatives.toLocaleString();
        document.getElementById("tnValue").textContent = result.true_negatives.toLocaleString();
        document.getElementById("chartTitle").textContent = `${result.label} timeline (${result.unit})`;
        message.textContent = `Analysis complete: ${result.total_records.toLocaleString()} observations compared with the dataset's annotated event intervals.`;

        const context = document.getElementById("datasetChart");
        if (datasetChart) {
            datasetChart.destroy();
        }

        datasetChart = new Chart(context, {
            type: "line",
            data: {
                labels: result.chart.map(row => row.time),
                datasets: [
                    {
                        label: result.label,
                        data: result.chart.map(row => row.value),
                        tension: 0.15,
                        pointRadius: 0
                    },
                    {
                        label: "Annotated disturbance",
                        data: result.chart.map(row => row.actual ? row.value : null),
                        showLine: false,
                        pointRadius: 3
                    },
                    {
                        label: "Predicted anomaly",
                        data: result.chart.map(row => row.predicted ? row.value : null),
                        showLine: false,
                        pointRadius: 3
                    }
                ]
            },
            options: {
                responsive: true,
                interaction: { mode: "index", intersect: false },
                scales: {
                    x: { ticks: { maxTicksLimit: 8, autoSkip: true } },
                    y: { title: { display: true, text: result.unit } }
                }
            }
        });
    } catch (error) {
        message.textContent = error.message;
    } finally {
        button.disabled = false;
    }
}

document.getElementById("analyzeButton").addEventListener("click", runDatasetAnalysis);
runDatasetAnalysis();
