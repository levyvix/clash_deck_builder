import React from 'react';
import { render, screen } from '@testing-library/react';
import Footer from './Footer';

describe('Footer Component', () => {
  test('renders footer with creator attribution', () => {
    render(<Footer />);
    
    // Check that the footer text is present
    expect(screen.getByText(/Made with KIRO IDE by/i)).toBeInTheDocument();
    expect(screen.getByText(/Levy Nunes \(@levyvix\)/i)).toBeInTheDocument();
  });

  test('renders footer with correct structure', () => {
    const { container } = render(<Footer />);
    
    // Check that footer element exists
    const footer = container.querySelector('footer');
    expect(footer).toBeInTheDocument();
    expect(footer).toHaveClass('footer');
    
    // Check container structure
    const footerContainer = container.querySelector('.footer__container');
    expect(footerContainer).toBeInTheDocument();
    
    // Check text structure
    const footerText = container.querySelector('.footer__text');
    expect(footerText).toBeInTheDocument();
    
    // Check creator span
    const creatorSpan = container.querySelector('.footer__creator');
    expect(creatorSpan).toBeInTheDocument();
  });

  test('creator name has proper styling class', () => {
    const { container } = render(<Footer />);
    
    const creatorSpan = container.querySelector('.footer__creator');
    expect(creatorSpan).toHaveClass('footer__creator');
    expect(creatorSpan).toHaveTextContent('Levy Nunes (@levyvix)');
  });
});