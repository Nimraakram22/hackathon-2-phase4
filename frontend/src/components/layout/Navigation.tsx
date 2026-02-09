import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../design-system/Button';
import styles from './Navigation.module.css';

export interface NavigationProps {
  variant?: 'public' | 'protected';
}

/**
 * Navigation Component
 * Consistent navigation across pages with variants for public and protected pages
 */
export function Navigation({ variant = 'public' }: NavigationProps): React.ReactElement {
  return (
    <nav className={styles.nav}>
      <div className={styles.container}>
        {/* Logo */}
        <Link to="/" className={styles.logo}>
          <span className={styles.logoText}>Agentic Todo</span>
        </Link>

        {/* Navigation Items */}
        <div className={styles.navItems}>
          {variant === 'public' ? (
            <>
              <Link to="/contact" className={styles.navLink}>
                Contact
              </Link>
              <Link to="/login" className={styles.navLink}>
                Sign In
              </Link>
              <Button variant="primary" size="md" onClick={() => window.location.href = '/signup'}>
                Get Started
              </Button>
            </>
          ) : (
            <>
              <Link to="/chat" className={styles.navLink}>
                Chat
              </Link>
              <div className={styles.userMenu}>
                <button className={styles.userMenuButton}>
                  <span>Account</span>
                </button>
                {/* User menu dropdown would go here */}
              </div>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
