import { useEffect, useState } from 'react';

function useActiveSection() {
  const [activeSection, setActiveSection] = useState('');

  useEffect(() => {
    const handleScroll = () => {
      const sections = ['home', 'about', 'services', 'certifications', 'projects', 'contact'];
      for (let id of sections) {
        const el = document.getElementById(id);
        if (el) {
          const rect = el.getBoundingClientRect();
          if (rect.top <= 100 && rect.bottom >= 100) {
            setActiveSection(id);
            break;
          }
        }
      }
    };

    window.addEventListener('scroll', handleScroll);
    handleScroll(); // run on mount
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return activeSection;
}
export default useActiveSection
