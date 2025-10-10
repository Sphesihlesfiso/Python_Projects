import React from 'react';
import './CertificationCard.css';

export default function CertificateCard({ name, image, completed, teacher }) {
  return (
    <div className="Certificate-container Certificate">
      <div className="Certificate-image">
        {image.startsWith('http') ? (
          <img src={image} alt={name} style={{ width: '100%', borderRadius: '12px' }} />
        ) : (
          <span  dangerouslySetInnerHTML={{ __html: image }} />
        )}
      </div>
      <h3>{name}</h3>
      <p><strong>Instructor:</strong> {teacher}</p>
      <p><strong>Completed:</strong> {completed}%</p>
    </div>
  );
}
