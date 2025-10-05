import React from 'react';
import Typewriter from 'typewriter-effect';
import './Home.css';

export default function Home() {
  return (
    <div className='Home-container'>
      <div className='Picture-paragraph'>
        <div className='Picture'>
          <img className="Home-img" src="/My Photo.jpg" alt="Sphesihle Mabaso" />
        </div>

        <div className='Text'>
          <h3>
            Hi, I'm <span className='Highlighted-text'>Sphesihle Mabaso</span> a
          </h3>

          <div className='Home-paragraph'>
            <Typewriter
              options={{
                strings: [
                  'Software Engineer in training',
                  'Problem Solver',
                  'Team Player',
                  'Full-Stack Developer'
                ],
                autoStart: true,
                loop: true,
              }}
            />
          </div>

          <p className='Home-paragraph'>
            I’m passionate about building secure, scalable web and mobile applications that solve real-world problems. Whether it’s designing responsive dashboards, integrating powerful backends, or refining git workflows I thrive on clean architecture and iterative improvement.
          </p>

         
        </div>
      </div>

      <div className='Buttons'>
        <a href="/Sphesihle Mabaso.pdf" download>
          <button>Get Resume</button>
        </a>
        <a href="#contact">
          <button>Contact Me</button>
        </a>
      </div>
    </div>
  );
}

