import { useState } from "react";

export default function AddEntryModal({ open, onClose, onSubmit, capacity }) {
  const [weight, setWeight] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (!open) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    const w = parseFloat(weight);
    if (!w || w < 0) {
      setError("Please enter a valid, non-negative weight.");
      return;
    }
    setError("");
    setSubmitting(true);
    try {
      await onSubmit(w);
      setWeight("");
      onClose();
    } catch (err) {
      setError(err.message || "Failed to add reading.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay open" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-title">➕ Add New Entry</div>
        <div className="modal-sub">Log a new cylinder weight reading manually.</div>
        <form onSubmit={handleSubmit}>
          <input
            className="modal-input"
            type="number"
            step="0.1"
            min="0"
            max={capacity}
            placeholder={`Weight (kg, max ${capacity})`}
            value={weight}
            onChange={(e) => setWeight(e.target.value)}
            autoFocus
          />
          {error && <div className="auth-error">{error}</div>}
          <div className="modal-actions">
            <button type="button" className="btn-ghost" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={submitting}>
              {submitting ? "Adding…" : "Add Entry"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
