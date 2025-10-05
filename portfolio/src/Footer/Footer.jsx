import React from "react";
import "./Footer.css";

export default function Footer() {
  return (
    <footer className="Footer-container">
      <div className="footer-text">
        All Rights Reserved © {new Date().getFullYear()}
      </div>
    </footer>
  );
}

