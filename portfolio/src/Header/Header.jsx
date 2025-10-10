import React, { useState } from 'react';
import './Header.css';

export default function Header() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <header className="Header-container">
      <div className="Header-logo">Portfolio</div>

      <button className="Header-toggle" onClick={() => setIsOpen(!isOpen)}>
        ☰
      </button>

      <nav className={`Header-nav ${isOpen ? 'open' : ''}`}>
        <ul className="Header-List-container">
        <li><a href="#home" className="Header-list-item">Home</a></li>
        <li><a href="#about" className="Header-list-item">About Me</a></li>
        <li><a href="#services" className="Header-list-item">Services</a></li>
        <li><a href="#certifications" className="Header-list-item">Certificates</a></li>
        <li><a href="#projects" className="Header-list-item">Projects</a></li>
        <li><a href="#contact" className="Header-list-item">Contact</a></li>
        </ul>

      </nav>
    </header>
  );
}
