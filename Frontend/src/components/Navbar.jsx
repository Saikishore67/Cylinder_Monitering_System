import { useAuth } from "../context/AuthContext";

export default function Navbar({ onHamburgerClick }) {
  const { profile, firebaseUser, logout } = useAuth();

  const displayName =
    profile?.full_name || firebaseUser?.displayName || firebaseUser?.email || "User";
  const initials = displayName
    .split(" ")
    .map((w) => w[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  const handleLogout = () => {
    if (confirm("Log out of the system?")) {
      logout();
    }
  };

  return (
    <header className="navbar">
      <div className="hamburger" onClick={onHamburgerClick}>
        ☰
      </div>
      <div className="navbar-brand">Cylinder Monitor</div>
      <div className="live-dot">LIVE</div>

      <div className="navbar-actions">
        <div className="user-profile" onClick={handleLogout} title="Log out">
          <div className="user-avatar">{initials}</div>
          <div className="user-info">
            <div className="user-name">{displayName}</div>
            <div className="user-role">Log out</div>
          </div>
        </div>
      </div>
    </header>
  );
}
