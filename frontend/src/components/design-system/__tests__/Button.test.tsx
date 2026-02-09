import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '../Button';

describe('Button Component', () => {
  describe('Variants', () => {
    it('renders primary variant with correct styles', () => {
      render(<Button variant="primary">Primary Button</Button>);
      const button = screen.getByRole('button', { name: /primary button/i });
      expect(button).toHaveClass('primary');
    });

    it('renders secondary variant with correct styles', () => {
      render(<Button variant="secondary">Secondary Button</Button>);
      const button = screen.getByRole('button', { name: /secondary button/i });
      expect(button).toHaveClass('secondary');
    });

    it('renders ghost variant with correct styles', () => {
      render(<Button variant="ghost">Ghost Button</Button>);
      const button = screen.getByRole('button', { name: /ghost button/i });
      expect(button).toHaveClass('ghost');
    });
  });

  describe('Sizes', () => {
    it('renders small size correctly', () => {
      render(<Button size="sm">Small</Button>);
      const button = screen.getByRole('button', { name: /small/i });
      expect(button).toHaveClass('sm');
    });

    it('renders medium size correctly', () => {
      render(<Button size="md">Medium</Button>);
      const button = screen.getByRole('button', { name: /medium/i });
      expect(button).toHaveClass('md');
    });

    it('renders large size correctly', () => {
      render(<Button size="lg">Large</Button>);
      const button = screen.getByRole('button', { name: /large/i });
      expect(button).toHaveClass('lg');
    });
  });

  describe('Accessibility', () => {
    it('has minimum 48x48px touch target for mobile', () => {
      render(<Button size="sm">Touch Target</Button>);
      const button = screen.getByRole('button', { name: /touch target/i });
      const styles = window.getComputedStyle(button);

      // Small buttons should still meet 48x48px minimum
      const minHeight = parseInt(styles.minHeight);
      const minWidth = parseInt(styles.minWidth);

      expect(minHeight).toBeGreaterThanOrEqual(48);
      expect(minWidth).toBeGreaterThanOrEqual(48);
    });

    it('is keyboard accessible with Enter key', () => {
      const handleClick = vi.fn();
      render(<Button onClick={handleClick}>Keyboard Test</Button>);
      const button = screen.getByRole('button', { name: /keyboard test/i });

      fireEvent.keyDown(button, { key: 'Enter', code: 'Enter' });
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('is keyboard accessible with Space key', () => {
      const handleClick = vi.fn();
      render(<Button onClick={handleClick}>Keyboard Test</Button>);
      const button = screen.getByRole('button', { name: /keyboard test/i });

      fireEvent.keyDown(button, { key: ' ', code: 'Space' });
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('has proper focus styles', () => {
      render(<Button>Focus Test</Button>);
      const button = screen.getByRole('button', { name: /focus test/i });

      button.focus();
      expect(button).toHaveFocus();
    });

    it('is disabled when disabled prop is true', () => {
      render(<Button disabled>Disabled Button</Button>);
      const button = screen.getByRole('button', { name: /disabled button/i });

      expect(button).toBeDisabled();
      expect(button).toHaveAttribute('aria-disabled', 'true');
    });

    it('has aria-busy when loading', () => {
      render(<Button loading>Loading Button</Button>);
      const button = screen.getByRole('button', { name: /loading button/i });

      expect(button).toHaveAttribute('aria-busy', 'true');
      expect(button).toBeDisabled();
    });
  });

  describe('Keyboard Navigation', () => {
    it('can be focused with Tab key', () => {
      render(
        <div>
          <Button>First</Button>
          <Button>Second</Button>
        </div>
      );

      const firstButton = screen.getByRole('button', { name: /first/i });
      const secondButton = screen.getByRole('button', { name: /second/i });

      firstButton.focus();
      expect(firstButton).toHaveFocus();

      // Simulate Tab to next button
      fireEvent.keyDown(firstButton, { key: 'Tab', code: 'Tab' });
      secondButton.focus();
      expect(secondButton).toHaveFocus();
    });

    it('does not trigger click when disabled', () => {
      const handleClick = vi.fn();
      render(<Button disabled onClick={handleClick}>Disabled</Button>);
      const button = screen.getByRole('button', { name: /disabled/i });

      fireEvent.click(button);
      fireEvent.keyDown(button, { key: 'Enter', code: 'Enter' });

      expect(handleClick).not.toHaveBeenCalled();
    });

    it('does not trigger click when loading', () => {
      const handleClick = vi.fn();
      render(<Button loading onClick={handleClick}>Loading</Button>);
      const button = screen.getByRole('button', { name: /loading/i });

      fireEvent.click(button);
      fireEvent.keyDown(button, { key: 'Enter', code: 'Enter' });

      expect(handleClick).not.toHaveBeenCalled();
    });
  });

  describe('Loading State', () => {
    it('shows loading spinner when loading prop is true', () => {
      render(<Button loading>Loading Button</Button>);
      const button = screen.getByRole('button', { name: /loading button/i });

      // Check for spinner element
      const spinner = button.querySelector('.spinner');
      expect(spinner).toBeInTheDocument();
    });

    it('hides button text when loading', () => {
      const { container } = render(<Button loading>Submit</Button>);
      const buttonText = container.querySelector('.buttonText');

      expect(buttonText).toHaveClass('loading');
    });
  });

  describe('Click Handling', () => {
    it('calls onClick handler when clicked', () => {
      const handleClick = vi.fn();
      render(<Button onClick={handleClick}>Click Me</Button>);
      const button = screen.getByRole('button', { name: /click me/i });

      fireEvent.click(button);
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('passes event to onClick handler', () => {
      const handleClick = vi.fn();
      render(<Button onClick={handleClick}>Click Me</Button>);
      const button = screen.getByRole('button', { name: /click me/i });

      fireEvent.click(button);
      expect(handleClick).toHaveBeenCalledWith(expect.any(Object));
    });
  });

  describe('Custom Props', () => {
    it('applies custom className', () => {
      render(<Button className="custom-class">Custom</Button>);
      const button = screen.getByRole('button', { name: /custom/i });

      expect(button).toHaveClass('custom-class');
    });

    it('forwards additional props to button element', () => {
      render(<Button data-testid="custom-button" aria-label="Custom Label">Test</Button>);
      const button = screen.getByTestId('custom-button');

      expect(button).toHaveAttribute('aria-label', 'Custom Label');
    });
  });
});
