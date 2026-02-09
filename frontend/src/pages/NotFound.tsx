import React from 'react';
import { useRouteError, isRouteErrorResponse, Link } from 'react-router-dom';
import { Heading } from '../components/design-system/Heading';
import { Text } from '../components/design-system/Text';
import { Button } from '../components/design-system/Button';
import styles from './NotFound.module.css';

/**
 * 404 Not Found Page
 * Displayed when user navigates to non-existent route
 */
export function NotFound(): React.ReactElement {
  const error = useRouteError();

  let errorMessage = 'Page not found';
  let errorDetails = "The page you're looking for doesn't exist or has been moved.";

  if (isRouteErrorResponse(error)) {
    errorMessage = error.statusText || errorMessage;
    errorDetails = error.data?.message || errorDetails;
  } else if (error instanceof Error) {
    errorMessage = error.message;
  }

  return (
    <div className={styles.notFound}>
      <div className={styles.container}>
        <div className={styles.content}>
          <div className={styles.errorCode}>404</div>

          <Heading level="h1" className={styles.title}>
            {errorMessage}
          </Heading>

          <Text size="lg" className={styles.description}>
            {errorDetails}
          </Text>

          <div className={styles.actions}>
            <Link to="/">
              <Button variant="primary" size="lg">
                Go Home
              </Button>
            </Link>

            <Link to="/contact">
              <Button variant="ghost" size="lg">
                Contact Support
              </Button>
            </Link>
          </div>

          <div className={styles.suggestions}>
            <Text size="sm" className={styles.suggestionsTitle}>
              You might be looking for:
            </Text>
            <ul className={styles.suggestionsList}>
              <li>
                <Link to="/" className={styles.suggestionLink}>
                  Home Page
                </Link>
              </li>
              <li>
                <Link to="/login" className={styles.suggestionLink}>
                  Sign In
                </Link>
              </li>
              <li>
                <Link to="/signup" className={styles.suggestionLink}>
                  Create Account
                </Link>
              </li>
              <li>
                <Link to="/contact" className={styles.suggestionLink}>
                  Contact Us
                </Link>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
