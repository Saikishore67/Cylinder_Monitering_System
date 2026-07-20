import { useEffect, useRef } from "react";
import Chart from "chart.js/auto";

export default function TrendChart({ readings }) {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    // Readings come newest-first from the API; chart reads left-to-right (oldest -> newest).
    const ordered = [...readings].reverse();
    const labels = ordered.map((r) =>
      new Date(r.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    );
    const data = ordered.map((r) => Number(r.weight));

    if (chartRef.current) {
      chartRef.current.destroy();
    }

    chartRef.current = new Chart(canvasRef.current.getContext("2d"), {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            data,
            borderColor: "#1d3557",
            borderWidth: 2.5,
            tension: 0.45,
            fill: true,
            backgroundColor: (ctx) => {
              const g = ctx.chart.ctx.createLinearGradient(0, 0, 0, 180);
              g.addColorStop(0, "rgba(29,53,87,0.12)");
              g.addColorStop(1, "rgba(29,53,87,0)");
              return g;
            },
            pointRadius: 3,
            pointBackgroundColor: "#1d3557",
            pointBorderColor: "#fff",
            pointBorderWidth: 2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: { label: (ctx) => ` ${ctx.parsed.y} kg` },
          },
        },
        scales: {
          x: { grid: { color: "rgba(0,0,0,0.05)" }, ticks: { font: { size: 11 } } },
          y: { grid: { color: "rgba(0,0,0,0.05)" }, ticks: { font: { size: 11 }, callback: (v) => v + " kg" } },
        },
      },
    });

    return () => chartRef.current?.destroy();
  }, [readings]);

  if (readings.length === 0) {
    return <div className="chart-empty">No readings yet for this device.</div>;
  }

  return (
    <div className="chart-container">
      <canvas ref={canvasRef} />
    </div>
  );
}
