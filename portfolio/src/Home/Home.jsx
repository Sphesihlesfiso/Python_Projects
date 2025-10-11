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
            I’m passionate about building secure, scalable web applications and websites that solve real-world problems. Whether you want a buisness or Personal website you've found  the right person for the job.
          </p>

         
        </div>
      </div>

      <div className='Buttons'>
        <a href="/Sphesihle_Mabaso_ATS_Friendly_CV.docx" download>
          <button>Get Resume</button>
        </a>
        <a href="#contact">
          <button>Contact Me</button>
        </a>
      </div>
    </div>
  );
}

