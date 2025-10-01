import React from 'react'
import "./Home.css"

import Profile from '../../PortfolioContainer/Profile/Profile'
import Footer from '../../PortfolioContainer/Footer/Footer'
function Home() {
  return (
    <div className='home-container'>
        <Profile/>
        <Footer/>
    </div>
  )
}
export default Home;
