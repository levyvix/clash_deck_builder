import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  BrowserRouter: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Routes: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Route: ({ element }: { element: React.ReactNode }) => <div>{element}</div>,
  Link: ({ children, to }: { children: React.ReactNode; to: string }) => <a href={to}>{children}</a>,
  useNavigate: () => jest.fn(),
  Navigate: () => <div>Navigate</div>,
  useLocation: () => ({ pathname: '/' }),
}));

test('renders app title', () => {
  render(<App />);
  const titleElement = screen.getByText(/Clash Royale Deck Builder/i);
  expect(titleElement).toBeInTheDocument();
});
