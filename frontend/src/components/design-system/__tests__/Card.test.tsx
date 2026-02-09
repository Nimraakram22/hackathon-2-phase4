import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Card } from '../Card';

describe('Card Component', () => {
  describe('Rendering', () => {
    it('renders children content', () => {
      render(
        <Card>
          <p>Card content</p>
        </Card>
      );

      expect(screen.getByText('Card content')).toBeInTheDocument();
    });

    it('renders without title', () => {
      render(
        <Card>
          <p>Content only</p>
        </Card>
      );

      const card = screen.getByText('Content only').parentElement;
      expect(card).toBeInTheDocument();
      expect(screen.queryByRole('heading')).not.toBeInTheDocument();
    });

    it('renders with title', () => {
      render(
        <Card title="Card Title">
          <p>Card content</p>
        </Card>
      );

      expect(screen.getByRole('heading', { name: /card title/i })).toBeInTheDocument();
      expect(screen.getByText('Card content')).toBeInTheDocument();
    });
  });

  describe('Styling', () => {
    it('applies base card styles', () => {
      const { container } = render(
        <Card>
          <p>Content</p>
        </Card>
      );

      const card = container.firstChild as HTMLElement;
      expect(card).toHaveClass('card');
    });

    it('applies custom className', () => {
      const { container } = render(
        <Card className="custom-card">
          <p>Content</p>
        </Card>
      );

      const card = container.firstChild as HTMLElement;
      expect(card).toHaveClass('card');
      expect(card).toHaveClass('custom-card');
    });

    it('has hover effect styles', () => {
      const { container } = render(
        <Card>
          <p>Hover me</p>
        </Card>
      );

      const card = container.firstChild as HTMLElement;
      const styles = window.getComputedStyle(card);

      // Card should have transition for hover effect
      expect(styles.transition).toBeTruthy();
    });
  });

  describe('Accessibility', () => {
    it('has proper semantic structure with title', () => {
      render(
        <Card title="Accessible Card">
          <p>Content</p>
        </Card>
      );

      const heading = screen.getByRole('heading', { name: /accessible card/i });
      expect(heading).toBeInTheDocument();
    });

    it('maintains proper heading hierarchy', () => {
      render(
        <div>
          <h1>Page Title</h1>
          <Card title="Card Title">
            <p>Content</p>
          </Card>
        </div>
      );

      const cardHeading = screen.getByRole('heading', { name: /card title/i });
      // Card title should be h3 by default (from Heading component)
      expect(cardHeading.tagName).toBe('H3');
    });

    it('allows custom content structure', () => {
      render(
        <Card>
          <h4>Custom Heading</h4>
          <p>Custom content structure</p>
          <button>Action</button>
        </Card>
      );

      expect(screen.getByRole('heading', { name: /custom heading/i })).toBeInTheDocument();
      expect(screen.getByText('Custom content structure')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /action/i })).toBeInTheDocument();
    });
  });

  describe('Content Flexibility', () => {
    it('renders multiple children', () => {
      render(
        <Card>
          <h4>Title</h4>
          <p>Paragraph 1</p>
          <p>Paragraph 2</p>
          <button>Action</button>
        </Card>
      );

      expect(screen.getByText('Title')).toBeInTheDocument();
      expect(screen.getByText('Paragraph 1')).toBeInTheDocument();
      expect(screen.getByText('Paragraph 2')).toBeInTheDocument();
      expect(screen.getByRole('button')).toBeInTheDocument();
    });

    it('renders complex nested content', () => {
      render(
        <Card title="Feature Card">
          <div className="icon">Icon</div>
          <p className="description">Description text</p>
          <ul>
            <li>Item 1</li>
            <li>Item 2</li>
          </ul>
        </Card>
      );

      expect(screen.getByText('Icon')).toBeInTheDocument();
      expect(screen.getByText('Description text')).toBeInTheDocument();
      expect(screen.getByText('Item 1')).toBeInTheDocument();
      expect(screen.getByText('Item 2')).toBeInTheDocument();
    });

    it('renders with React components as children', () => {
      const CustomComponent = () => <div>Custom Component</div>;

      render(
        <Card>
          <CustomComponent />
        </Card>
      );

      expect(screen.getByText('Custom Component')).toBeInTheDocument();
    });
  });

  describe('Props Forwarding', () => {
    it('forwards additional HTML attributes', () => {
      render(
        <Card data-testid="test-card" aria-label="Test Card">
          <p>Content</p>
        </Card>
      );

      const card = screen.getByTestId('test-card');
      expect(card).toHaveAttribute('aria-label', 'Test Card');
    });

    it('forwards id attribute', () => {
      render(
        <Card id="unique-card">
          <p>Content</p>
        </Card>
      );

      const card = document.getElementById('unique-card');
      expect(card).toBeInTheDocument();
    });
  });

  describe('Visual Hierarchy', () => {
    it('separates title from content visually', () => {
      const { container } = render(
        <Card title="Card Title">
          <p>Card content</p>
        </Card>
      );

      const cardTitle = container.querySelector('.cardTitle');
      expect(cardTitle).toBeInTheDocument();

      const cardContent = container.querySelector('.cardContent');
      expect(cardContent).toBeInTheDocument();
    });
  });
});
