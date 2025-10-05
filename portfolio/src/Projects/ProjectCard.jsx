import React from "react";
import "./Project.css";

export default function ProjectCard({ title, image, link }) {
  return (
    <div className="ProjectCard">
      <img src={image} alt={title} className="project-image" />
      <h3 className="project-title">{title}</h3>
      <a href={link} target="_blank" rel="noopener noreferrer">
        <button className="view-button">View Project</button>
      </a>
    </div>
  );
}

