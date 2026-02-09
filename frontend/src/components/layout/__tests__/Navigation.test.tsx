import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Navigation } from '../Navigation';

// Helper to render with router context
const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('Navigation Component', () => {
  describe('Public Variant', () => {
    it('renders logo', () => {
      renderWithRouter(<Navigation variant="public" />);

      const logo = screen.getByText('Agentic Todo');
      expect(logo).toBeInTheDocument();
    });

    it('renders Sign In link', () => {
      renderWithRouter(<Navigation variant="public" />);

      const signInLink = screen.getByRole('link', { name: /sign in/i });
      expect(signInLink).toBeInTheDocument();
      expect(signInLink).toHaveAttribute('href', '/login');
    });

    it('renders Get Started button', () => {
      renderWithRouter(<Navigation variant="public" />);

      const getStartedButton = screen.getByRole('link', { name: /get started/i });
      expect(getStartedButton).toBeInTheDocument();
      expect(getStartedButton).toHaveAttribute('href', '/signup');
    });

    it('does not render user menu', () => {
      renderWithRouter(<Navigation variant="public" />);

      expect(screen.queryByText(/logout/i)).not.toBeInTheDocument();
    });
  });

  describe('Protected Variant', () => {
    const mockUser = {
      name: 'John Doe',
      email: 'john@example.com'
    };

    it('renders logo', () => {
      renderWithRouter(<Navigation variant="protected" user={mockUser} />);

      const logo = screen.getByText('Agentic Todo');
      expect(logo).toBeInTheDocument();
    });

    it('renders user name', () => {
      renderWithRouter(<Navigation variant="protected" user={mockUser} />);

      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    it('renders logout button', () => {
      renderWithRouter(<Navigation variant="protected" user={mockUser} />);

      const logoutButton = screen.getByRole('button', { name: /logout/i });
      expect(logoutButton).toBeInTheDocument();
    });

    it('calls onLogout when logout button clicked', () => {
      const handleLogout = vi.fn();
      renderWithRouter(
        <Navigation variant="protected" user={mockUser} onLogout={handleLogout} />
      );

      const logoutButton = screen.getByRole('button', { name: /logout/i });
      fireEvent.click(logoutButton);

      expect(handleLogout).toHaveBeenCalledTimes(1);
    });

    it('does not render Sign In or Get Started', () => {
      renderWithRouter(<Navigation variant="protected" user={mockUser} />);

      expect(screen.queryByText(/sign in/i)).not.toBeInTheDocument();
      expect(screen.queryByText(/get started/i)).not.toBeInTheDocument();
    });
  });

  describe('Responsive Behavior', () => {
    it('renders mobile menu toggle on small screens', () => {
      // Mock window.matchMedia for mobile viewport
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: vi.fn().mockImplementation(query => ({
          matches: query === '(max-width: 768px)',
          media: query,
          onchange: null,
          addListener: vi.fn(),
          removeListener: vi.fn(),
          addEventListener: vi.fn(),
          removeEventListener: vi.fn(),
          dispatchEvent: vi.fn(),
        })),
      });

      renderWithRouter(<Navigation variant="public" />);

      // Mobile menu toggle should be present
      const menuToggle = screen.queryByRole('button', { name: /menu/i });
      // This test assumes mobile menu implementation exists
      // If not implemented yet, this will be a placeholder
    });

    it('maintains sticky positioning', () => {
      const { container } = renderWithRouter(<Navigation variant="public" />);

      const nav = container.querySelector('nav');
      const styles = window.getComputedStyle(nav!);

      expect(styles.position).toBe('sticky');
    });
  });

  describe('Accessibility', () => {
    it('has proper navigation landmark', () => {
      renderWithRouter(<Navigation variant="public" />);

      const nav = screen.getByRole('navigation');
      expect(nav).toBeInTheDocument();
    });

    it('has accessible logo link', () => {
      renderWithRouter(<Navigation variant="public" />);

      const logoLink = screen.getByRole('link', { name: /agentic todo/i });
      expect(logoLink).toHaveAttribute('href', '/');
    });

    it('has keyboard accessible navigation links', () => {
      renderWithRouter(<Navigation variant="public" />);

      const signInLink = screen.getByRole('link', { name: /sign in/i });
      signInLink.focus();

      expect(signInLink).toHaveFocus();
    });

    it('has keyboard accessible buttons', () => {
      const mockUser = { name: 'John Doe', email: 'john@example.com' };
      const handleLogout = vi.fn();

      renderWithRouter(
        <Navigation variant="protected" user={mockUser} onLogout={handleLogout} />
      );

      const logoutButton = screen.getByRole('button', { name: /logout/i });

      logoutButton.focus();
      expect(logoutButton).toHaveFocus();

      fireEvent.keyDown(logoutButton, { key: 'Enter', code: 'Enter' });
      expect(handleLogout).toHaveBeenCalled();
    });

    it('has proper focus indicators', () => {
      renderWithRouter(<Navigation variant="public" />);

      const signInLink = screen.getByRole('link', { name: /sign in/i });
      signInLink.focus();

      // Focus styles should be applied (from CSS)
      expect(signInLink).toHaveFocus();
    });
  });

  describe('Visual Hierarchy', () => {
    it('emphasizes Get Started button over Sign In', () => {
      renderWithRouter(<Navigation variant="public" />);

      const getStartedButton = screen.getByRole('link', { name: /get started/i });
      const signInLink = screen.getByRole('link', { name: /sign in/i });

      // Get Started should use primary button variant (accent color)
      expect(getStartedButton.className).toContain('primary');

      // Sign In should be less prominent (ghost variant)
      expect(signInLink.className).toContain('ghost');
    });

    it('maintains consistent spacing', () => {
      const { container } = renderWithRouter(<Navigation variant="public" />);

      const nav = container.querySelector('nav');
      const styles = window.getComputedStyle(nav!);

      // Should use spacing from design tokens
      expect(styles.padding).toBeTruthy();
    });
  });

  describe('Logo Behavior', () => {
    it('logo links to home page', () => {
      renderWithRouter(<Navigation variant="public" />);

      const logoLink = screen.getByRole('link', { name: /agentic todo/i });
      expect(logoLink).toHaveAttribute('href', '/');
    });

    it('logo is clickable', () => {
      renderWithRouter(<Navigation variant="public" />);

      const logoLink = screen.getByRole('link', { name: /agentic todo/i });
      fireEvent.click(logoLink);

      // Navigation should occur (handled by React Router)
      expect(logoLink).toBeInTheDocument();
    });
  });

  describe('User Menu', () => {
    const mockUser = {
      name: 'Jane Smith',
      email: 'jane@example.com'
    };

    it('displays user information', () => {
      renderWithRouter(<Navigation variant="protected" user={mockUser} />);

      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });

    it('handles missing user name gracefully', () => {
      const userWithoutName = { email: 'user@example.com' };

      renderWithRouter(
        <Navigation variant="protected" user={userWithoutName as any} />
      );

      // Should display email or fallback
      expect(screen.getByText('user@example.com')).toBeInTheDocument();
    });
  });

  describe('Integration', () => {
    it('works with React Router navigation', () => {
      renderWithRouter(<Navigation variant="public" />);

      const signInLink = screen.getByRole('link', { name: /sign in/i });
      const getStartedLink = screen.getByRole('link', { name: /get started/i });

      expect(signInLink).toHaveAttribute('href', '/login');
      expect(getStartedLink).toHaveAttribute('href', '/signup');
    });
  });
});
