import React, { useRef } from 'react';
import emailjs from '@emailjs/browser';
import './Contact.css';


export default function Contact() {
    const form = useRef();

    const sendEmail = (e) => {
    e.preventDefault();
      emailjs.sendForm(
  process.env.REACT_APP_EMAILJS_SERVICE_ID,
  process.env.REACT_APP_EMAILJS_TEMPLATE_ID,
  form.current,
  process.env.REACT_APP_EMAILJS_PUBLIC_KEY
)

    
.then(
        () => {
        alert('Message sent successfully!');
        form.current.reset();
        },
        (error) => {
        alert('Failed to send message. Please try again.');
        console.error("email.js error ",error);
        console.log(form.current);

        }
    );
    };

  return (
    <div className="Contact-container" id="contact">
      <h1 className="Contact-heading">Contact Me</h1>
      <div className="Contact-grid">
        {/* Left: Contact Form */}
        <form ref={form} onSubmit={sendEmail} className="Contact-form">
            <input type="text" name="user_name" placeholder="Your Name" required />
            <input type="email" name="user_email" placeholder="Your Email" required />
            <input type="text" name="subject" placeholder="Subject" required />
            <textarea name="message" rows="5" placeholder="Your Message" required></textarea>
            <button type="submit">Send Message</button>
        </form>


        {/* Right: Contact Info */}
        <div className="Contact-info">
          <h3>Reach Me Directly</h3>
          <p><i className="bi bi-envelope-fill"></i> <strong>Email:</strong> <a href="mailto:mabasosphesihle25@gmail.com">mabasosphesihle25@gmail.com</a></p>
          <p><i className="bi bi-geo-alt-fill"></i> <strong>Location:</strong> Cape Town, Stellenbosch</p>
          <p><i className="bi bi-telephone-fill"></i> <strong>Phone:</strong> <a href="tel:+27638133387">063 813 3387</a></p>
        </div>
      </div>
    </div>
  );
}

