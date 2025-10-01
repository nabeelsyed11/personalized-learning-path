import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from './App';

describe('App', () => {
  it('renders Vite and React logos', () => {
    render(<App />);
    
    // Check for Vite logo
    const viteLogo = screen.getByAltText('Vite logo');
    expect(viteLogo).toBeInTheDocument();
    expect(viteLogo).toHaveAttribute('src', '/vite.svg');
    
    // Check for React logo
    const reactLogo = screen.getByAltText('React logo');
    expect(reactLogo).toBeInTheDocument();
    expect(reactLogo).toHaveClass('react');
    
    // Check for heading
    const heading = screen.getByRole('heading', { level: 1 });
    expect(heading).toHaveTextContent('Vite + React');
  });

  it('renders a counter button', () => {
    render(<App />);
    const button = screen.getByRole('button');
    expect(button).toHaveTextContent('count is 0');
  });
});
