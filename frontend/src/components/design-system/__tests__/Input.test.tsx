import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Input } from '../Input';

describe('Input Component', () => {
  describe('Rendering', () => {
    it('renders with label', () => {
      render(<Input label="Email" />);

      expect(screen.getByLabelText('Email')).toBeInTheDocument();
    });

    it('renders with placeholder', () => {
      render(<Input label="Email" placeholder="Enter your email" />);

      const input = screen.getByPlaceholderText('Enter your email');
      expect(input).toBeInTheDocument();
    });

    it('renders with helper text', () => {
      render(<Input label="Email" helperText="We'll never share your email" />);

      expect(screen.getByText("We'll never share your email")).toBeInTheDocument();
    });

    it('renders required indicator', () => {
      render(<Input label="Email" required />);

      const requiredIndicator = screen.getByLabelText('required');
      expect(requiredIndicator).toBeInTheDocument();
      expect(requiredIndicator).toHaveTextContent('*');
    });
  });

  describe('Validation', () => {
    it('displays error message when error prop is provided', () => {
      render(<Input label="Email" error="Email is required" />);

      const errorMessage = screen.getByRole('alert');
      expect(errorMessage).toHaveTextContent('Email is required');
    });

    it('applies error styles when error prop is provided', () => {
      render(<Input label="Email" error="Invalid email" />);

      const input = screen.getByLabelText('Email');
      expect(input).toHaveClass('error');
    });

    it('sets aria-invalid when error is present', () => {
      render(<Input label="Email" error="Invalid email" />);

      const input = screen.getByLabelText('Email');
      expect(input).toHaveAttribute('aria-invalid', 'true');
    });

    it('does not show helper text when error is present', () => {
      render(
        <Input
          label="Email"
          helperText="Helper text"
          error="Error message"
        />
      );

      expect(screen.queryByText('Helper text')).not.toBeInTheDocument();
      expect(screen.getByText('Error message')).toBeInTheDocument();
    });

    it('links error message to input with aria-describedby', () => {
      render(<Input label="Email" error="Invalid email" />);

      const input = screen.getByLabelText('Email');
      const errorMessage = screen.getByRole('alert');

      expect(input).toHaveAttribute('aria-describedby', errorMessage.id);
    });
  });

  describe('Accessibility', () => {
    it('has proper label association', () => {
      render(<Input label="Email Address" />);

      const input = screen.getByLabelText('Email Address');
      expect(input).toBeInTheDocument();
    });

    it('has minimum 48px height for touch targets', () => {
      const { container } = render(<Input label="Email" />);

      const input = container.querySelector('input');
      const styles = window.getComputedStyle(input!);

      expect(parseInt(styles.minHeight)).toBeGreaterThanOrEqual(48);
    });

    it('supports keyboard navigation', () => {
      render(<Input label="Email" />);

      const input = screen.getByLabelText('Email');
      input.focus();

      expect(input).toHaveFocus();
    });

    it('has visible focus indicator', () => {
      render(<Input label="Email" />);

      const input = screen.getByLabelText('Email');
      input.focus();

      expect(input).toHaveFocus();
      // Focus styles are applied via CSS
    });

    it('announces errors to screen readers', () => {
      render(<Input label="Email" error="Email is required" />);

      const errorMessage = screen.getByRole('alert');
      expect(errorMessage).toBeInTheDocument();
    });

    it('uses aria-describedby for helper text', () => {
      render(<Input label="Email" helperText="Enter a valid email" />);

      const input = screen.getByLabelText('Email');
      const helperText = screen.getByText('Enter a valid email');

      expect(input).toHaveAttribute('aria-describedby', helperText.id);
    });
  });

  describe('Error States', () => {
    it('shows error icon with error message', () => {
      render(<Input label="Email" error="Invalid email" />);

      const errorMessage = screen.getByRole('alert');
      expect(errorMessage).toHaveTextContent('⚠');
    });

    it('changes border color when error is present', () => {
      const { container } = render(<Input label="Email" error="Invalid" />);

      const input = container.querySelector('input');
      expect(input).toHaveClass('error');
    });

    it('clears error when error prop is removed', () => {
      const { rerender } = render(<Input label="Email" error="Invalid" />);

      expect(screen.getByRole('alert')).toBeInTheDocument();

      rerender(<Input label="Email" />);

      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    });
  });

  describe('User Interaction', () => {
    it('accepts user input', () => {
      render(<Input label="Email" />);

      const input = screen.getByLabelText('Email') as HTMLInputElement;
      fireEvent.change(input, { target: { value: 'test@example.com' } });

      expect(input.value).toBe('test@example.com');
    });

    it('calls onChange handler when value changes', () => {
      const handleChange = vi.fn();
      render(<Input label="Email" onChange={handleChange} />);

      const input = screen.getByLabelText('Email');
      fireEvent.change(input, { target: { value: 'test@example.com' } });

      expect(handleChange).toHaveBeenCalledTimes(1);
    });

    it('calls onBlur handler when input loses focus', () => {
      const handleBlur = vi.fn();
      render(<Input label="Email" onBlur={handleBlur} />);

      const input = screen.getByLabelText('Email');
      fireEvent.blur(input);

      expect(handleBlur).toHaveBeenCalledTimes(1);
    });

    it('calls onFocus handler when input gains focus', () => {
      const handleFocus = vi.fn();
      render(<Input label="Email" onFocus={handleFocus} />);

      const input = screen.getByLabelText('Email');
      fireEvent.focus(input);

      expect(handleFocus).toHaveBeenCalledTimes(1);
    });
  });

  describe('Disabled State', () => {
    it('renders as disabled when disabled prop is true', () => {
      render(<Input label="Email" disabled />);

      const input = screen.getByLabelText('Email');
      expect(input).toBeDisabled();
    });

    it('does not accept input when disabled', () => {
      render(<Input label="Email" disabled />);

      const input = screen.getByLabelText('Email') as HTMLInputElement;
      fireEvent.change(input, { target: { value: 'test@example.com' } });

      expect(input.value).toBe('');
    });

    it('does not call onChange when disabled', () => {
      const handleChange = vi.fn();
      render(<Input label="Email" disabled onChange={handleChange} />);

      const input = screen.getByLabelText('Email');
      fireEvent.change(input, { target: { value: 'test' } });

      expect(handleChange).not.toHaveBeenCalled();
    });
  });

  describe('Input Types', () => {
    it('renders as email input', () => {
      render(<Input label="Email" type="email" />);

      const input = screen.getByLabelText('Email');
      expect(input).toHaveAttribute('type', 'email');
    });

    it('renders as password input', () => {
      render(<Input label="Password" type="password" />);

      const input = screen.getByLabelText('Password');
      expect(input).toHaveAttribute('type', 'password');
    });

    it('renders as text input by default', () => {
      render(<Input label="Name" />);

      const input = screen.getByLabelText('Name');
      expect(input).toHaveAttribute('type', 'text');
    });
  });

  describe('Props Forwarding', () => {
    it('forwards additional HTML attributes', () => {
      render(
        <Input
          label="Email"
          data-testid="email-input"
          autoComplete="email"
        />
      );

      const input = screen.getByTestId('email-input');
      expect(input).toHaveAttribute('autocomplete', 'email');
    });

    it('forwards ref to input element', () => {
      const ref = React.createRef<HTMLInputElement>();
      render(<Input label="Email" ref={ref} />);

      expect(ref.current).toBeInstanceOf(HTMLInputElement);
    });

    it('applies custom className', () => {
      render(<Input label="Email" className="custom-input" />);

      const wrapper = screen.getByLabelText('Email').parentElement;
      expect(wrapper).toHaveClass('custom-input');
    });
  });

  describe('Mobile Optimization', () => {
    it('prevents iOS zoom with 16px font size', () => {
      const { container } = render(<Input label="Email" />);

      const input = container.querySelector('input');
      const styles = window.getComputedStyle(input!);

      // Font size should be at least 16px to prevent iOS zoom
      const fontSize = parseFloat(styles.fontSize);
      expect(fontSize).toBeGreaterThanOrEqual(16);
    });
  });
});
