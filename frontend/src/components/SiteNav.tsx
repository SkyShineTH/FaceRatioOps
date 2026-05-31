import { NavLink } from "react-router-dom";

export default function SiteNav() {
  return (
    <nav className="site-nav" aria-label="Primary">
      <NavLink to="/" end className={({ isActive }) => (isActive ? "active" : undefined)}>
        Workbench
      </NavLink>
      <NavLink to="/architecture" className={({ isActive }) => (isActive ? "active" : undefined)}>
        Architecture
      </NavLink>
    </nav>
  );
}
