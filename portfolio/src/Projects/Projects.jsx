import React from 'react'
import "./Projects.css"
import Projects_array  from './Projects_array'
import ProjectCard from './ProjectCard'


export default function Projects() {
  return (
    <div className='Projects-container'>
        <h2 className='title'>
            My Projects
        </h2>
        
         <div className="projects-grid">
            {Projects_array.map((project, index) => (
                <ProjectCard
                key={index}
                title={project.title}
                image={project.image}
                video={project.video}
                description={project.description}
                />
            ))}
    </div>
      
    </div>
  )
}
