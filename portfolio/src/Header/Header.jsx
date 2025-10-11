import React, { useState } from 'react';
import './Header.css';
import useActiveSection from './ActiveSection'; // adjust path as needed

export default function Header() {
  const [isOpen, setIsOpen] = useState(false);
  const activeSection = useActiveSection();

  return (
    <header className="Header-container">
      <div className="Header-logo">Portfolio</div>

      <button className="Header-toggle" onClick={() => setIsOpen(!isOpen)}>
        ☰
      </button>

      <nav className={`Header-nav ${isOpen ? 'open' : ''}`}>
        <ul className="Header-List-container">
          {['home', 'about', 'services', 'certifications', 'projects', 'contact'].map((section) => (
            <li key={section}>
              <a
                href={`#${section}`}
                className={`Header-list-item ${activeSection === section ? 'active' : ''}`}
              >
                {section.charAt(0).toUpperCase() + section.slice(1).replace('-', ' ')}
              </a>
            </li>
          ))}
        </ul>
      </nav>
    </header>
  );
}

