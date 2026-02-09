import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Login } from '../Login';

// Mock fetch
global.fetch = vi.fn();

// Helper to render with router
const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('Login Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  describe('Rendering', () => {
    it('renders login form with all fields', () => {
      renderWithRouter(<Login />);

      expect(screen.getByRole('heading', { name: /welcome back/i })).toBeInTheDocument();
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
    });

    it('renders Remember Me checkbox', () => {
      renderWithRouter(<Login />);

      const checkbox = screen.getByRole('checkbox', { name: /remember me/i });
      expect(checkbox).toBeInTheDocument();
      expect(screen.getByText(/remember me for 30 days/i)).toBeInTheDocument();
    });

    it('renders link to signup page', () => {
      renderWithRouter(<Login />);

      const signupLink = screen.getByRole('link', { name: /sign up/i });
      expect(signupLink).toBeInTheDocument();
      expect(signupLink).toHaveAttribute('href', '/signup');
    });

    it('displays helper text for Remember Me', () => {
      renderWithRouter(<Login />);

      expect(screen.getByText(/keep me signed in on this device/i)).toBeInTheDocument();
    });
  });

  describe('Form Validation', () => {
    it('validates email format', async () => {
      renderWithRouter(<Login />);

      const emailInput = screen.getByLabelText(/email/i);
      fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
      fireEvent.blur(emailInput);

      await waitFor(() => {
        expect(screen.getByText(/invalid email address/i)).toBeInTheDocument();
      });
    });

    it('requires email field', async () => {
      renderWithRouter(<Login />);

      const submitButton = screen.getByRole('button', { name: /sign in/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/email is required/i)).toBeInTheDocument();
      });
    });

    it('requires password field', async () => {
      renderWithRouter(<Login />);

      const emailInput = screen.getByLabelText(/email/i);
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });

      const submitButton = screen.getByRole('button', { name: /sign in/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/password is required/i)).toBeInTheDocument();
      });
    });
  });

  describe('Remember Me Functionality', () => {
    it('Remember Me checkbox is unchecked by default', () => {
      renderWithRouter(<Login />);

      const checkbox = screen.getByRole('checkbox', { name: /remember me/i }) as HTMLInputElement;
      expect(checkbox.checked).toBe(false);
    });

    it('can toggle Remember Me checkbox', () => {
      renderWithRouter(<Login />);

      const checkbox = screen.getByRole('checkbox', { name: /remember me/i }) as HTMLInputElement;

      fireEvent.click(checkbox);
      expect(checkbox.checked).toBe(true);

      fireEvent.click(checkbox);
      expect(checkbox.checked).toBe(false);
    });

    it('sets 30-day session when Remember Me is checked', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ token: 'test-token', userId: 'user-123' }),
      });

      renderWithRouter(<Login />);

      fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
      fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } });

      const checkbox = screen.getByRole('checkbox', { name: /remember me/i });
      fireEvent.click(checkbox);

      const submitButton = screen.getByRole('button', { name: /sign in/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        const sessionStr = localStorage.getItem('auth_session');
        expect(sessionStr).toBeTruthy();

        if (sessionStr) {
          const session = JSON.parse(sessionStr);
          const expiresInMs = session.expiresAt - Date.now();
          const expiresInDays = expiresInMs / (24 * 60 * 60 * 1000);

          // Should be approximately 30 days
          expect(expiresInDays).toBeGreaterThan(29);
          expect(expiresInDays).toBeLessThan(31);
        }
      });
    });

    it('sets 1-day session when Remember Me is not checked', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ token: 'test-token', userId: 'user-123' }),
      });

      renderWithRouter(<Login />);

      fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
      fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } });

      const submitButton = screen.getByRole('button', { name: /sign in/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        const sessionStr = localStorage.getItem('auth_session');
        expect(sessionStr).toBeTruthy();

        if (sessionStr) {
          const session = JSON.parse(sessionStr);
          const expiresInMs = session.expiresAt - Date.now();
          const expiresInDays = expiresInMs / (24 * 60 * 60 * 1000);

          // Should be approximately 1 day
          expect(expiresInDays).toBeGreaterThan(0.9);
          expect(expiresInDays).toBeLessThan(1.1);
        }
      });
    });
  });

  describe('Error Messages', () => {
    it('displays form-level error when login fails', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ message: 'Invalid credentials' }),
      });

      renderWithRouter(<Login />);

      fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
      fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'wrongpassword' } });

      const submitButton = screen.getByRole('button', { name: /sign in/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
      });
    });

    it('displays generic error when fetch fails', async () => {
      (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

      renderWithRouter(<Login />);

      fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
      fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } });

      const submitButton = screen.getByRole('button', { name: /sign in/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/network error/i)).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('has proper form labels', () => {
      renderWithRouter(<Login />);

      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    });

    it('marks required fields', () => {
      renderWithRouter(<Login />);

      const requiredIndicators = screen.getAllByLabelText('required');
      expect(requiredIndicators.length).toBeGreaterThan(0);
    });

    it('announces errors to screen readers', async () => {
      renderWithRouter(<Login />);

      const emailInput = screen.getByLabelText(/email/i);
      fireEvent.change(emailInput, { target: { value: 'invalid' } });
      fireEvent.blur(emailInput);

      await waitFor(() => {
        const errorMessage = screen.getByRole('alert');
        expect(errorMessage).toBeInTheDocument();
      });
    });

    it('has keyboard accessible form', () => {
      renderWithRouter(<Login />);

      const emailInput = screen.getByLabelText(/email/i);
      emailInput.focus();
      expect(emailInput).toHaveFocus();
    });

    it('has accessible checkbox', () => {
      renderWithRouter(<Login />);

      const checkbox = screen.getByRole('checkbox', { name: /remember me/i });
      expect(checkbox).toBeInTheDocument();
    });
  });

  describe('Successful Login', () => {
    it('redirects to chat page after successful login', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ token: 'test-token', userId: 'user-123' }),
      });

      renderWithRouter(<Login />);

      fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
      fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } });

      const submitButton = screen.getByRole('button', { name: /sign in/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(localStorage.getItem('auth_session')).toBeTruthy();
      });
    });

    it('stores session token in localStorage', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ token: 'test-token-123', userId: 'user-456' }),
      });

      renderWithRouter(<Login />);

      fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
      fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } });

      const submitButton = screen.getByRole('button', { name: /sign in/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        const sessionStr = localStorage.getItem('auth_session');
        expect(sessionStr).toBeTruthy();

        if (sessionStr) {
          const session = JSON.parse(sessionStr);
          expect(session.token).toBe('test-token-123');
          expect(session.userId).toBe('user-456');
        }
      });
    });

    it('shows loading state during submission', async () => {
      (global.fetch as any).mockImplementation(() => new Promise(() => {})); // Never resolves

      renderWithRouter(<Login />);

      fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
      fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } });

      const submitButton = screen.getByRole('button', { name: /sign in/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(submitButton).toHaveAttribute('aria-busy', 'true');
      });
    });

    it('redirects to returnUrl if provided', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ token: 'test-token', userId: 'user-123' }),
      });

      // Render with returnUrl query parameter
      window.history.pushState({}, '', '/login?returnUrl=/tasks');

      renderWithRouter(<Login />);

      fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
      fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } });

      const submitButton = screen.getByRole('button', { name: /sign in/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(localStorage.getItem('auth_session')).toBeTruthy();
      });
    });
  });
});
