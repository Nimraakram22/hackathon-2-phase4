import React from 'react';
import { Heading } from '../design-system/Heading';
import { Text } from '../design-system/Text';
import { Button } from '../design-system/Button';
import styles from './HeroSection.module.css';

export interface HeroSectionProps {
  headline: string;
  subheadline: string;
  ctaText: string;
  ctaLink: string;
}

/**
 * Hero Section Component
 * Landing page hero with headline, subheadline, and primary CTA
 * Implements visual hierarchy principles (US1)
 */
export function HeroSection({
  headline,
  subheadline,
  ctaText,
  ctaLink,
}: HeroSectionProps): React.ReactElement {
  return (
    <section className={styles.hero}>
      <div className={styles.container}>
        <div className={styles.content}>
          <Heading level="h1" className={styles.headline}>
            {headline}
          </Heading>
          <Text size="lg" className={styles.subheadline}>
            {subheadline}
          </Text>
          <div className={styles.ctaContainer}>
            <Button
              variant="primary"
              size="lg"
              onClick={() => (window.location.href = ctaLink)}
              className={styles.cta}
            >
              {ctaText}
            </Button>
          </div>
        </div>
        <div className={styles.visual}>
          {/* Placeholder for hero image/illustration */}
          <div className={styles.placeholder}>
            <Text size="lg" weight="medium">
              Hero Visual
            </Text>
          </div>
        </div>
      </div>
    </section>
  );
}
