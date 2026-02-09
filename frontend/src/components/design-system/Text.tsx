import React from 'react';
import styles from './Text.module.css';

export type TextSize = 'xs' | 'sm' | 'base' | 'lg' | 'xl';
export type TextWeight = 'normal' | 'medium' | 'semibold' | 'bold';

export interface TextProps {
  size?: TextSize;
  weight?: TextWeight;
  children: React.ReactNode;
  className?: string | undefined;
  as?: 'p' | 'span' | 'div';
}

/**
 * Text Component
 * Flexible text component with size and weight variants
 */
export function Text({
  size = 'base',
  weight = 'normal',
  as: Component = 'p',
  children,
  className = '',
}: TextProps): React.ReactElement {
  const classNames = [styles.text, styles[size], styles[weight], className]
    .filter(Boolean)
    .join(' ');

  return <Component className={classNames}>{children}</Component>;
}
