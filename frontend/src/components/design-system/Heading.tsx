import React from 'react';
import styles from './Heading.module.css';

export type HeadingLevel = 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6';

export interface HeadingProps {
  level: HeadingLevel;
  children: React.ReactNode;
  className?: string | undefined;
}

/**
 * Heading Component
 * Semantic heading component with consistent sizing from typography scale
 */
export function Heading({ level, children, className = '' }: HeadingProps): React.ReactElement {
  const Component = level;
  const classNames = [styles.heading, styles[level], className].filter(Boolean).join(' ');

  return <Component className={classNames}>{children}</Component>;
}
