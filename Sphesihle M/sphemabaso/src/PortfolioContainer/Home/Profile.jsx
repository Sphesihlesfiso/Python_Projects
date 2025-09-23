import React from 'react'
import {Typewriter} from "react-simple-typewriter"
import "./Profile.css"
export default function Profile() {
  return (
    <div className='profile-container'>
        <div className='profile-parent'>
            <div className='profile-details'>
                <div className='colz'>
                    <div className='colz-icon'>
                    <a href="https://web.facebook.com/profile.php?id=100090026647652">
                        <i className='fa fa-facebook-square'> </i>
                    </a>
                    <a href="https://web.facebook.com/profile.php?id=100090026647652">
                        <i className='fa fa-google-plus-square'> </i>
                    </a>
                    <a href="https://web.facebook.com/profile.php?id=100090026647652">
                        <i className='fa fa-youtube-square'> </i>
                    </a>
                    <a href="https://www.instagram.com/sphesihlesamamntungwa/">
                        <i className='fa fa-instagram'> </i>
                    </a>
                    <a href="https://web.facebook.com/profile.php?id=100090026647652">
                        <i className='fa fa-twitter'> </i>
                    </a>
                    </div>
                </div>
                <div className='profile-details-name'>
                    <span className='primary-text'>
                        {" "}
                        Hello,I'm <span className='highlighted-text'>Sphesihle Mabaso</span> a
                    </span>
                </div>
                <div className='profile-details-role'>
                    <span className='primary-text'>
                        {" "}
                        <h1>
                            <Typewriter
                                words={['Full Stack Developer', 'React Enthusiast', 'Creative Thinker']}
                                loop={Infinity}
                                cursor
                                cursorStyle=''
                                typeSpeed={70}
                                deleteSpeed={40}
                                delaySpeed={1000}
                            />
                        </h1>
                        <span className='profile-role-tagline'>
                            Your work is going to fill a large part of your life,
                            and the only way to be truly satisfied is to do
                            what you believe is great work. : Steve Jobs
                        </span>
                    </span>
                </div>
                <div className='profile-options'>
                    <button className='btn primary-btn'>
                        Hire me
                    </button>
                    <a href='Sphesihle Mabaso.pdf' download="Sphesihle Mabaso.pdf"><button  className='btn primary-btn'>
                        Get Resume
                    </button>
                    </a>
                </div>
            </div>
            <div className='profile-picture'>
                <div className='profile-picture-background'>

                </div>
            </div>
        </div>
    </div>
  )
}
