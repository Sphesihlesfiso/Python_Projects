import { React, useState } from "react";
import "./Project.css";

export default function ProjectCard({ title, image, video, description, techStack }) {
  const [showDescription, setShowDescription] = useState(false);
  


  return (
    <div className="ProjectCard">
      <img src={image} alt={title} className="project-image" />
      <h3 className="project-title">{title}</h3>

      <button className="view-button" onClick={() => setShowDescription(prev => !prev)}>
        {showDescription ? "Hide Description" : "Show Description"}
      </button>
        
      {video && (
          <a href={video} target="_blank" rel="noopener noreferrer">
            <button className="view-button">Project Demo</button>
          </a>
        )}

     

      {showDescription && <p className="project-description">{description}</p>}

      {techStack && (
        <div className="tech-stack">
          {techStack.map((tech, index) => (
            <span key={index} className="tech-badge">
              {tech}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}


