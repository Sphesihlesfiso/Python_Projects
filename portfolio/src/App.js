
import './App.css';
import Header from './Header/Header';
import Home from './Home/Home';
import Footer from './Footer/Footer';
import About from './About/About';
import Services from './My servises/Services';
import Certifications from './Certifications/Certifications';
import Projects from './Projects/Projects';
import Contact from './Contact/Contact';

function App() {
  return (
    <>
      <Header />
    <div className="App">
        
        <section id="home"  className="full-section"><Home /></section>
        <section id="about" className="full-section"><About /></section>
        <section id="services" className="full-section"><Services /></section>
        <section id="certifications" className="full-section"><Certifications /></section>
        <section id="projects" className="full-section"><Projects /></section>
        <section id="contact" className="full-section"><Contact/></section>
        
</div>
      <Footer />
      </>

  );
}

export default App;
