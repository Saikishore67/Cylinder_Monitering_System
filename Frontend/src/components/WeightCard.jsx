import { useState } from "react";

export default function WeightCard({ device, latestReading, capacity, onCapacityChange }) {
  const [editingCapacity, setEditingCapacity] = useState(false);
  const [capacityInput, setCapacityInput] = useState(capacity);

  const weight = latestReading ? Number(latestReading.weight) : null;
  const fillPct =
    weight !== null && capacity > 0 ? Math.round((weight / capacity) * 100) : null;

  const status =
    fillPct === null ? "unknown" : fillPct <= 15 ? "critical" : fillPct <= 25 ? "warning" : "normal";

  const statusLabel = { normal: "Normal", warning: "Low", critical: "Critical", unknown: "No data" }[status];

  const saveCapacity = () => {
    const val = Number(capacityInput);
    if (val > 0) onCapacityChange(val);
    setEditingCapacity(false);
  };

  return (
    <div className="card fade-up">
      <div className="card-header">
        <div>
          <div className="card-label">Current Cylinder Weight</div>
          <div className="card-title">{device?.name || "—"}</div>
        </div>
        <div className={`status-badge status-${status}`}>
          <span className="badge-dot" /> {statusLabel}
        </div>
      </div>

      <div className="weight-display">
        <div className="weight-value">
          <span>{weight !== null ? weight.toFixed(1) : "--"}</span>
          <span className="weight-unit">kg</span>
        </div>
        <div className="weight-updated">
          {latestReading
            ? `Last updated: ${new Date(latestReading.timestamp).toLocaleString()}`
            : "No readings yet"}
        </div>
      </div>

      <div className="progress-section">
        <div className="progress-labels">
          <span className="progress-label">
            Fill Level {fillPct !== null ? `(${fillPct}%)` : ""}
          </span>
          {editingCapacity ? (
            <span className="progress-capacity-edit">
              <input
                type="number"
                min="1"
                step="0.1"
                value={capacityInput}
                onChange={(e) => setCapacityInput(e.target.value)}
                autoFocus
              />
              <button onClick={saveCapacity}>Save</button>
            </span>
          ) : (
            <span
              className="progress-capacity"
              onClick={() => setEditingCapacity(true)}
              title="Click to edit capacity"
            >
              Capacity: {capacity} kg ✎
            </span>
          )}
        </div>
        <div className="progress-track">
          <div
            className="progress-fill"
            style={{ width: `${Math.min(fillPct ?? 0, 100)}%` }}
          />
        </div>
      </div>
    </div>
  );
}
