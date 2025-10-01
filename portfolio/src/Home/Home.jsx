import React from 'react'
import Typewriter from 'typewriter-effect';
import "./Home.css"
export default function Home() {
  return (
    <div className='Home-container'>
        <div className='Picture-paragraph'>
            <div className='Picture'>
                <img className="Home-img" src="/logo512.png" alt="Sphesihle Mabaso"></img>

            </div>
            <div className='Text'>
                <h3>Hi I'm  <span className='Highlighted-text'> Sphesihle Mabaso </span> I'm a </h3> 

                <p1 className='Home-paragraph'>
                      <Typewriter
                            options={{
                            strings: ['Aspiring Software Engineer', 'Problem Solver', 'Team Player', ],
                            autoStart: true,
                            loop: true,
                            }}
                        />
                    <p>
                        Lorem ipsum dolor sit amet consectetur adipisicing elit. Velit vero rem voluptate, eaque voluptatem saepe
                        , optio deleniti, praesentium nam enim distinctio nesciunt neque illo odio! Dolorum ipsam a quae adipisci?
                    </p>
                </p1>

            </div>
        </div>
        <div className='Buttons'>
        <a href="/Sphesihle Mabaso.pdf" download="/Sphesihle Mabaso.pdf"><button >
            Get Resume
        </button></a>
        <button>
            Contact Me
        </button>
        </div>
    </div>
  )
}
