import React from 'react';
import { Container } from 'react-bootstrap';

function Footer() {
  return (
    <footer >
      <Container>
        <p>Sphesihle Mabaso</p>
        <p > © All CopyRights Reserved {new Date().getFullYear()}.</p>
      </Container>
    </footer>
  );
}

export default Footer;
