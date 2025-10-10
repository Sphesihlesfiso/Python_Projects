import {React} from 'react'
import "./Certifications.css"
import CertificationsArray from '../assets/CertificationsArray'
import CertificateCard from '../assets/CertificateCard'

export default function Certifications() {
  return (
    <div className='Certifications' id='certifications'>
        <h1 style={{textAlign:'center'}} className='title'>
           Certificates
        </h1>
        <ul className='Certifications-container'>
             {CertificationsArray.map((cert, index) => (
                    <CertificateCard
                    key={index}
                    name={cert.name}
                    image={cert.image}
                    completed={cert.completed}
                    teacher={cert.teacher}
                    />
                ))}
                    </ul>

    </div>
  )
}
