import React from 'react';
import '../styles/Footer.css';

const Footer: React.FC = () => {
  return (
    <footer className="footer">
      <div className="footer__container">
        <p className="footer__text">
          Made with KIRO IDE by{' '}
          <span className="footer__creator">Levy Nunes (@levyvix)</span>
        </p>
      </div>
    </footer>
  );
};

export default Footer;