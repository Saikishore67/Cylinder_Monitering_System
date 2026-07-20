export default function ActivityTable({ readings }) {
  return (
    <div className="table-card fade-up">
      <div className="table-header">
        <div className="table-title">Activity History</div>
      </div>

      {readings.length === 0 ? (
        <div className="table-empty">No readings recorded yet.</div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Weight (kg)</th>
              <th>Change</th>
            </tr>
          </thead>
          <tbody>
            {readings.map((r, i) => {
              const prev = readings[i + 1]; // next item is older, since list is newest-first
              const change = prev ? (Number(r.weight) - Number(prev.weight)).toFixed(1) : null;
              return (
                <tr key={r.id}>
                  <td className="ts-cell">{new Date(r.timestamp).toLocaleString()}</td>
                  <td className="weight-cell">{Number(r.weight).toFixed(1)}</td>
                  <td className="change-cell">
                    {change === null ? "—" : `${change > 0 ? "+" : ""}${change}`}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}
