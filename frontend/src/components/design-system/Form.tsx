import React from 'react';
import styles from './Form.module.css';

export interface FormProps extends React.FormHTMLAttributes<HTMLFormElement> {
  children: React.ReactNode;
  error?: string;
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
}

/**
 * Form Component
 * Form wrapper with error handling and accessibility
 * Implements form best practices (US3)
 */
export function Form({ children, error, onSubmit, className, ...props }: FormProps): React.ReactElement {
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    onSubmit(e);
  };

  return (
    <form
      className={`${styles.form} ${className || ''}`}
      onSubmit={handleSubmit}
      noValidate
      {...props}
    >
      {error && (
        <div className={styles.formError} role="alert" aria-live="polite">
          <span className={styles.errorIcon}>⚠</span>
          <span className={styles.errorText}>{error}</span>
        </div>
      )}

      {children}
    </form>
  );
}
