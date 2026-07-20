export default function Sidebar({
  devices,
  selectedDeviceId,
  onSelectDevice,
  onAddDeviceClick,
  isOpen,
  onClose,
}) {
  return (
    <>
      <div
        className={`sidebar-overlay ${isOpen ? "open" : ""}`}
        onClick={onClose}
      />
      <aside className={`sidebar ${isOpen ? "open" : ""}`}>
        <div className="sidebar-brand">
          <div className="hotel-icon">⛽</div>
          <h2>Cylinder Monitor</h2>
          <span>{devices.length} device{devices.length !== 1 ? "s" : ""}</span>
        </div>

        <nav className="sidebar-nav">
          <div className="nav-label">Devices</div>

          {devices.length === 0 && (
            <div className="nav-empty">No devices yet</div>
          )}

          {devices.map((d) => (
            <div
              key={d.device_id}
              className={`nav-item ${
                d.device_id === selectedDeviceId ? "active" : ""
              }`}
              onClick={() => {
                onSelectDevice(d.device_id);
                onClose();
              }}
            >
              <span className="nav-icon">▣</span>
              <div className="nav-item-text">
                <div>{d.name}</div>
                <div className="nav-item-sub">{d.device_id}</div>
              </div>
            </div>
          ))}

          <div className="nav-item nav-add" onClick={onAddDeviceClick}>
            <span className="nav-icon">＋</span> Add Device
          </div>
        </nav>
      </aside>
    </>
  );
}
