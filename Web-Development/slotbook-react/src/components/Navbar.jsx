import { useState } from "react";
import { navLinks } from "../data.js";
import useScrollSpy from "../hooks/useScrollSpy.js";

const sectionIds = navLinks.map((l) => l.href.slice(1));

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const active = useScrollSpy(sectionIds);
  const close = () => setOpen(false);

  return (
    <header className="nav">
      <div className="wrap nav-inner">
        <a href="#top" className="logo" onClick={close}>Slotbook</a>
        <button
          className="menu-btn"
          aria-expanded={open}
          aria-controls="menu"
          onClick={() => setOpen(!open)}
        >
          {open ? "Close" : "Menu"}
        </button>
        <nav id="menu" className={`menu ${open ? "open" : ""}`}>
          {navLinks.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className={active === link.href.slice(1) ? "active" : ""}
              onClick={close}
            >
              {link.label}
            </a>
          ))}
          <a href="#contact" className="btn btn-small" onClick={close}>Get started</a>
        </nav>
      </div>
    </header>
  );
}
