import { useState } from "react";

export default function AddDeviceModal({ open, onClose, onSubmit }) {
  const [name, setName] = useState("");
  const [deviceId, setDeviceId] = useState("");
  const [capacity, setCapacity] = useState(36);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (!open) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim() || !deviceId.trim()) {
      setError("Name and device ID are both required.");
      return;
    }
    setError("");
    setSubmitting(true);
    try {
      await onSubmit(name.trim(), deviceId.trim(), Number(capacity) || 36);
      setName("");
      setDeviceId("");
      setCapacity(36);
      onClose();
    } catch (err) {
      setError(err.message || "Failed to add device.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay open" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-title">🛢 Register Device</div>
        <div className="modal-sub">
          Add a cylinder/sensor device to start tracking its readings.
        </div>
        <form onSubmit={handleSubmit}>
          <input
            className="modal-input"
            type="text"
            placeholder="Device name (e.g. Main Supply Tank A)"
            value={name}
            onChange={(e) => setName(e.target.value)}
            autoFocus
          />
          <input
            className="modal-input"
            type="text"
            placeholder="Device ID (must match the physical sensor's ID)"
            value={deviceId}
            onChange={(e) => setDeviceId(e.target.value)}
          />
          <input
            className="modal-input"
            type="number"
            min="1"
            step="0.1"
            placeholder="Full tank capacity (kg)"
            value={capacity}
            onChange={(e) => setCapacity(e.target.value)}
          />
          {error && <div className="auth-error">{error}</div>}
          <div className="modal-actions">
            <button type="button" className="btn-ghost" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={submitting}>
              {submitting ? "Adding…" : "Add Device"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
