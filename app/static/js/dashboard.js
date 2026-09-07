async function loadPerformanceHistory() {
    try {
        const response = await fetch("/api/history");

        if (!response.ok) {
            throw new Error("Unable to load monitoring history.");
        }

        const data = await response.json();

        if (data.length === 0) {
            return;
        }

        const labels = data.map(item => item.timestamp);

        const cpuValues = data.map(item => item.cpu);
        const memoryValues = data.map(item => item.memory);

        // Keep CPU values only for observations
        // identified as anomalies by Isolation Forest.
        const anomalyValues = data.map(item => {
            if (item.anomaly === -1) {
                return item.cpu;
            }

            return null;
        });

        const chart = document.getElementById("performanceChart");

        new Chart(chart, {
            type: "line",

            data: {
                labels: labels,

                datasets: [
                    {
                        label: "CPU Usage (%)",
                        data: cpuValues,
                        tension: 0.3
                    },

                    {
                        label: "Memory Usage (%)",
                        data: memoryValues,
                        tension: 0.3
                    },

                    {
                        label: "AI Anomaly",
                        data: anomalyValues,
                        showLine: false,
                        pointRadius: 7,
                        pointHoverRadius: 9
                    }
                ]
            },

            options: {
                responsive: true,

                interaction: {
                    mode: "index",
                    intersect: false
                },

                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,

                        title: {
                            display: true,
                            text: "Usage (%)"
                        }
                    },

                    x: {
                        title: {
                            display: true,
                            text: "Time"
                        },

                        ticks: {
                            maxTicksLimit: 8,
                            autoSkip: true
                        }
                    }
                }
            }
        });

    } catch (error) {
        console.error("Performance history error:", error);
    }
}


loadPerformanceHistory();

setInterval(() => {
    window.location.reload();
}, 10000);