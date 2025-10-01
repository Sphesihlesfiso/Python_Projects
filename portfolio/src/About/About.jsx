import React from 'react'
import "./About.css"
export default function About() {
  return (
    <div className='About-container'>
        <h1 className='Heading'>
            About Me
        </h1>
        <h2 className='Paragraph-name'>
            Who am I?
        </h2>
        <p className='paragraph'>
            Lorem ipsum dolor sit amet consectetur, adipisicing elit. 
            Esse consectetur odio molestias quidem harum, distinctio sapiente consequuntur eaque ratione sed! Ad repellendus repellat ab, 
            expedita deserunt maiores id pariatur hic!
        </p>
        <h3 className='ending'>
            My Skills
        </h3>
            <ul className='Skills-container'>
                <li className='Skill'>HTML</li>
                <li className='Skill'>CSS</li>
                <li className='Skill'>JavaScript</li>
                <li className='Skill'>React</li>
                <li className='Skill'>Node.js</li>
                <li className='Skill'>Express</li>
                <li className='Skill'>EJS Templating</li>
                <li className='Skill'>Python</li>
                <li className='Skill'>Java</li>
                <li className='Skill'>Spring</li>
                <li className='Skill'>Spring Boot</li>
                <li className='Skill'>Databases</li>
                <li className='Skill'>Supabase</li>
                <li className='Skill'>Git</li>
                <li className='Skill'>GitHub</li>
            </ul>
        
    </div>
  )
}
