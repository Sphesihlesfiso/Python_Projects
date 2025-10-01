import React from 'react'
import "./Servises.css"
export default function Services() {
  return (
        <div className='Services'>
            <h1 className='tittle'>My Services</h1>
            <ul className='Services-container'>
                <li className='Service'>Web Development</li>
                <li className='Service'>Mobile App Development</li>
                <li className='Service'>Backend API Integration</li>
                <li className='Service'>Authentication & Security</li>
                <li className='Service'>Responsive UI Design</li>
                <li className='Service'>Database Management (PostgreSQL, Supabase)</li>
                <li className='Service'>Version Control (Git & GitHub)</li>
                <li className='Service'>Java & Spring Boot Applications</li>
                <li className='Service'>Python Scripting & Automation</li>
            </ul>
        </div>
   
  )
}
