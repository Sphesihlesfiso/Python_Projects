import React from 'react';
import './About.css';

export default function About() {
  return (
    <div className='About-container'>
        <div className="About-content">
      <h1 className='Heading'>About Me</h1>

      <h2 className='Paragraph-name' style={{textAlign:"center"}}>Who am I?</h2>
      <p className='paragraph'>
        I'm Sphesihle Mabaso  a resilient, methodical builder with a passion for crafting secure, scalable web and mobile applications. I thrive on solving real-world problems through clean architecture, responsive design, and thoughtful backend integration.
      </p>
      <p className='paragraph'>
        My workflow is rooted in iterative improvement and professional code practices. Whether I’m refining React dashboards, managing PostgreSQL databases, or troubleshooting git branches, I bring precision and purpose to every project.
      </p>

      <h3 className='ending' style={{textAlign:"center"}}>My Skills</h3>
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
        <li className='Skill'>PostgreSQL</li>
        <li className='Skill'>Supabase</li>
        <li className='Skill'>Git</li>
        <li className='Skill'>GitHub</li>
      </ul>
      <h3 className='ending' style={{textAlign:"center"}}>Tools</h3>
          <ul className='Tool-container'>
            <li className='Tool'>VS Code</li>
            <li className='Tool'>Postman</li>
            <li className='Tool'>GitHub Desktop</li>
            <li className='Tool'>Figma</li>
            <li className='Tool'>Supabase Studio</li>
            <li className='Tool'>Chrome DevTools</li>
            <li className='Tool'>IntelliJ IDEA</li>
            <li className='Tool'>Netlify</li>
            <li className='Tool'>Vercel</li>
          </ul>


    </div>
    </div>
  );
}
