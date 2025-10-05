import React from 'react';
import './Servises.css';

export default function Services() {
  return (
    <div className='Services'>
      <h1 className='tittle'>My Services</h1>
      <ul className='Services-container'>
        <li className='Service'>
          <i className="bi bi-laptop"></i> Web Development
        </li>
        <li className='Service'>
          <i className="bi bi-phone"></i> Mobile App Development
        </li>
        <li className='Service'>
          <i className="bi bi-plug"></i> Backend API Integration
        </li>
        <li className='Service'>
          <i className="bi bi-shield-lock"></i> Authentication & Security
        </li>
        <li className='Service'>
          <i className="bi bi-columns-gap"></i> Responsive UI Design
        </li>
        <li className='Service'>
          <i className="bi bi-database"></i> Database Management (PostgreSQL, Supabase)
        </li>
        <li className='Service'>
          <i className="bi bi-git"></i> Version Control (Git & GitHub)
        </li>
        <li className='Service'>
          <i className="bi bi-cup-hot"></i> Java & Spring Boot Applications
        </li>
        <li className='Service'>
          <i className="bi bi-terminal"></i> Python Scripting & Automation
        </li>
      </ul>
    </div>
  );
}
