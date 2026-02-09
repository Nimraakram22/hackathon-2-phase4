import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Signup } from '../Signup';

// Mock fetch
global.fetch = vi.fn();

// Helper to render with router
const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('Signup Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  describe('Rendering', () => {
    it('renders signup form with all fields', () => {
      renderWithRouter(<Signup />);

      expect(screen.getByRole('heading', { name: /create your account/i })).toBeInTheDocument();
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByLabelText('Password', { exact: false })).toBeInTheDocument();
      expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument();
    });

    it('renders link to login page', () => {
      renderWithRouter(<Signup />);

      const loginLink = screen.getByRole('link', { name: /sign in/i });
      expect(loginLink).toBeInTheDocument();
      expect(loginLink).toHaveAttribute('href', '/login');
    });

    it('displays password requirements', () => {
      renderWithRouter(<Signup />);

      expect(screen.getByText(/at least 8 characters/i)).toBeInTheDocument();
      expect(screen.getByText(/at least 3 of:/i)).toBeInTheDocument();
      expect(screen.getByText(/not found in data breaches/i)).toBeInTheDocument();
    });
  });

  describe('Form Validation', () => {
    it('validates email format', async () => {
      renderWithRouter(<Signup />);

      const emailInput = screen.getByLabelText(/email/i);
      fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
      fireEvent.blur(emailInput);

      await waitFor(() => {
        expect(screen.getByText(/invalid email address/i)).toBeInTheDocument();
      });
    });

    it('validates password minimum length', async () => {
      renderWithRouter(<Signup />);

      const passwordInput = screen.getByLabelText('Password', { exact: false });
      fireEvent.change(passwordInput, { target: { value: 'short' } });
      fireEvent.blur(passwordInput);

      await waitFor(() => {
        expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument();
      });
    });

    it('validates password character types', async () => {
      renderWithRouter(<Signup />);

      const passwordInput = screen.getByLabelText('Password', { exact: false });
      fireEvent.change(passwordInput, { target: { value: 'weakpassword' } });
      fireEvent.blur(passwordInput);

      await waitFor(() => {
        expect(screen.getByText(/password must contain at least 3 of/i)).toBeInTheDocument();
      });
    });

    it('validates password confirmation match', async () => {
      renderWithRouter(<Signup />);

      const passwordInput = screen.getByLabelText('Password', { exact: false });
      const confirmInput = screen.getByLabelText(/confirm password/i);

      fireEvent.change(passwordInput, { target: { value: 'SecurePass123!' } });
      fireEvent.change(confirmInput, { target: { value: 'DifferentPass123!' } });
      fireEvent.blur(confirmInput);

      await waitFor(() => {
        expect(screen.getByText(/passwords don't match/i)).toBeInTheDocument();
      });
    });

    it('requires all fields to be filled', async () => {
      renderWithRouter(<Signup />);

      const submitButton = screen.getByRole('button', { name: /create account/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/email is required/i)).toBeInTheDocument();
      });
    });
  });

  describe('Password Strength Indicator', () => {
    it('shows weak strength for short passwords', async () => {
      renderWithRouter(<Signup />);

      const passwordInput = screen.getByLabelText('Password', { exact: false });
      fireEvent.change(passwordInput, { target: { value: 'Pass123' } });

      await waitFor(() => {
        expect(screen.getByText(/weak/i)).toBeInTheDocument();
      });
    });

    it('shows medium strength for adequate passwords', async () => {
      renderWithRouter(<Signup />);

      const passwordInput = screen.getByLabelText('Password', { exact: false });
      fireEvent.change(passwordInput, { target: { value: 'Password123' } });

      await waitFor(() => {
        expect(screen.getByText(/medium/i)).toBeInTheDocument();
      });
    });

    it('shows strong strength for secure passwords', async () => {
      renderWithRouter(<Signup />);

      const passwordInput = screen.getByLabelText('Password', { exact: false });
      fireEvent.change(passwordInput, { target: { value: 'SecurePassword123!' } });

      await waitFor(() => {
        expect(screen.getByText(/strong/i)).toBeInTheDocument();
      });
    });

    it('displays password strength bar', async () => {
      renderWithRouter(<Signup />);

      const passwordInput = screen.getByLabelText('Password', { exact: false });
      fireEvent.change(passwordInput, { target: { value: 'SecurePass123!' } });

      await waitFor(() => {
        expect(screen.getByText(/password strength/i)).toBeInTheDocument();
      });
    });
  });

  describe('Error Messages', () => {
    it('displays form-level error when signup fails', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ message: 'Email already exists' }),
      });

      renderWithRouter(<Signup />);

      fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
      fireEvent.change(screen.getByLabelText('Password', { exact: false }), { target: { value: 'SecurePass123!' } });
      fireEvent.change(screen.getByLabelText(/confirm password/i), { target: { value: 'SecurePass123!' } });

      const submitButton = screen.getByRole('button', { name: /create account/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/email already exists/i)).toBeInTheDocument();
      });
    });

    it('displays error when password is pwned', async () => {
      // Mock pwned check
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ isPwned: true }),
      });

      renderWithRouter(<Signup />);

      fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
      fireEvent.change(screen.getByLabelText('Password', { exact: false }), { target: { value: 'Password123!' } });
      fireEvent.change(screen.getByLabelText(/confirm password/i), { target: { value: 'Password123!' } });

      const submitButton = screen.getByRole('button', { name: /create account/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/found in data breaches/i)).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('has proper form labels', () => {
      renderWithRouter(<Signup />);

      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByLabelText('Password', { exact: false })).toBeInTheDocument();
      expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
    });

    it('marks required fields', () => {
      renderWithRouter(<Signup />);

      const requiredIndicators = screen.getAllByLabelText('required');
      expect(requiredIndicators.length).toBeGreaterThan(0);
    });

    it('announces errors to screen readers', async () => {
      renderWithRouter(<Signup />);

      const emailInput = screen.getByLabelText(/email/i);
      fireEvent.change(emailInput, { target: { value: 'invalid' } });
      fireEvent.blur(emailInput);

      await waitFor(() => {
        const errorMessage = screen.getByRole('alert');
        expect(errorMessage).toBeInTheDocument();
      });
    });

    it('has keyboard accessible form', () => {
      renderWithRouter(<Signup />);

      const emailInput = screen.getByLabelText(/email/i);
      emailInput.focus();
      expect(emailInput).toHaveFocus();
    });
  });

  describe('Successful Signup', () => {
    it('redirects to chat page after successful signup', async () => {
      // Mock successful pwned check
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ isPwned: false }),
      });

      // Mock successful signup
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ token: 'test-token', userId: 'user-123' }),
      });

      renderWithRouter(<Signup />);

      fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
      fireEvent.change(screen.getByLabelText('Password', { exact: false }), { target: { value: 'SecurePass123!' } });
      fireEvent.change(screen.getByLabelText(/confirm password/i), { target: { value: 'SecurePass123!' } });

      const submitButton = screen.getByRole('button', { name: /create account/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(localStorage.getItem('authToken')).toBe('test-token');
        expect(localStorage.getItem('userId')).toBe('user-123');
      });
    });

    it('shows loading state during submission', async () => {
      (global.fetch as any).mockImplementation(() => new Promise(() => {})); // Never resolves

      renderWithRouter(<Signup />);

      fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
      fireEvent.change(screen.getByLabelText('Password', { exact: false }), { target: { value: 'SecurePass123!' } });
      fireEvent.change(screen.getByLabelText(/confirm password/i), { target: { value: 'SecurePass123!' } });

      const submitButton = screen.getByRole('button', { name: /create account/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(submitButton).toHaveAttribute('aria-busy', 'true');
      });
    });
  });
});
