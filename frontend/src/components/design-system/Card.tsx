import React from 'react';
import styles from './Card.module.css';

export interface CardProps {
  title?: string;
  children: React.ReactNode;
  className?: string;
}

/**
 * Card Component
 * Container component with optional title for grouping related content
 */
export function Card({ title, children, className = '' }: CardProps): React.ReactElement {
  const classNames = [styles.card, className].filter(Boolean).join(' ');

  return (
    <div className={classNames}>
      {title && <h3 className={styles.title}>{title}</h3>}
      <div className={styles.content}>{children}</div>
    </div>
  );
}
