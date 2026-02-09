import { Component, ErrorInfo, ReactNode } from 'react';
import { Heading } from './design-system/Heading';
import { Text } from './design-system/Text';
import { Button } from './design-system/Button';
import styles from './ErrorBoundary.module.css';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * Error Boundary Component
 * Catches JavaScript errors anywhere in the child component tree
 * Displays fallback UI instead of crashing the whole app
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(_error: Error): Partial<State> {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  override componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log error to console in development
    console.error('Error caught by ErrorBoundary:', error, errorInfo);

    // Update state with error details
    this.setState({
      error,
      errorInfo,
    });

    // TODO: Log error to error reporting service (e.g., Sentry)
    // logErrorToService(error, errorInfo);
  }

  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  override render(): ReactNode {
    if (this.state.hasError) {
      // Custom fallback UI provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      return (
        <div className={styles.errorBoundary}>
          <div className={styles.container}>
            <div className={styles.content}>
              <div className={styles.icon}>⚠</div>

              <Heading level="h1" className={styles.title}>
                Something went wrong
              </Heading>

              <Text size="lg" className={styles.description}>
                We're sorry, but something unexpected happened. The error has been logged and we'll look into it.
              </Text>

              {import.meta.env.DEV && this.state.error && (
                <details className={styles.errorDetails}>
                  <summary className={styles.errorSummary}>
                    Error Details (Development Only)
                  </summary>
                  <div className={styles.errorContent}>
                    <Text size="sm" className={styles.errorMessage}>
                      <strong>Error:</strong> {this.state.error.toString()}
                    </Text>
                    {this.state.errorInfo && (
                      <pre className={styles.errorStack}>
                        {this.state.errorInfo.componentStack}
                      </pre>
                    )}
                  </div>
                </details>
              )}

              <div className={styles.actions}>
                <Button
                  variant="primary"
                  size="lg"
                  onClick={this.handleReset}
                >
                  Try Again
                </Button>

                <Button
                  variant="ghost"
                  size="lg"
                  onClick={() => window.location.href = '/'}
                >
                  Go Home
                </Button>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
