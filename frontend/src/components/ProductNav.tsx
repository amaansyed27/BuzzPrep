import { ChevronDown, LogOut } from "lucide-react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";

export default function ProductNav({ transparent = false }: { transparent?: boolean }) {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();

  return (
    <header className={`product-nav ${transparent ? "transparent" : ""}`}>
      <Link className="brand-lockup" to="/" aria-label="BuzzPrep home">
        <span className="brand-mark">B</span>
        <span>BUZZPREP</span>
      </Link>
      {user ? (
        <>
          <nav aria-label="Product navigation">
            <NavLink to="/dashboard">Dashboard</NavLink>
            <NavLink to="/history">Prep history</NavLink>
          </nav>
          <div className="nav-account">
            <span>{user.email}</span>
            <ChevronDown size={14} aria-hidden="true" />
            <button
              type="button"
              onClick={() => {
                void signOut().then(() => navigate("/"));
              }}
            >
              <LogOut size={14} /> Sign out
            </button>
          </div>
        </>
      ) : (
        <>
          <nav aria-label="Landing navigation">
            <a href="/#how-it-works">How it works</a>
            <a href="/#workspace">Workspace</a>
            <a href="/#evidence">Evidence</a>
          </nav>
          <div className="nav-actions">
            <Link to="/auth?mode=signin">Sign in</Link>
            <Link className="nav-primary" to="/auth?mode=signup">Create account</Link>
          </div>
        </>
      )}
    </header>
  );
}
