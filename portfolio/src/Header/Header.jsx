import React from 'react'
import "./Header.css"
export default function Header() {
  return (
    <div className='Header-container'>
        
        <ul className='Header-List-container'>
            <li className='Header-list-item'>
                Home
            </li>
            <li className='Header-list-item'>
                About Me
            </li>
            <li className='Header-list-item'>
                Projects
            </li>
            <li className='Header-list-item'>
                Contact
            </li>

        </ul>

    </div>
  )
}
