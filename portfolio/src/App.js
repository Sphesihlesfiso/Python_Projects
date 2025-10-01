
import './App.css';
import Header from './Header/Header';
import Home from './Home/Home';
import Footer from './Footer/Footer';
import About from './About/About';
import Services from './My servises/Services';
function App() {
  return (
    <div className="App">
        <Header/>
        <Home/>
        <About/>
        <Services/>
        <Footer/>
    </div>
  );
}

export default App;
