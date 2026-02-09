import React from 'react';
import { Heading } from '../design-system/Heading';
import { Text } from '../design-system/Text';
import { Card } from '../design-system/Card';
import styles from './FeaturesSection.module.css';

export interface Feature {
  icon: React.ReactNode;
  title: string;
  description: string;
}

export interface FeaturesSectionProps {
  features: Feature[];
}

/**
 * Features Section Component
 * Displays 3-4 key benefits with icons and descriptions
 * Implements scannability principles (US1)
 */
export function FeaturesSection({ features }: FeaturesSectionProps): React.ReactElement {
  return (
    <section className={styles.features}>
      <div className={styles.container}>
        <Heading level="h2" className={styles.sectionTitle}>
          Why Choose Agentic Todo?
        </Heading>
        <div className={styles.grid}>
          {features.map((feature, index) => (
            <Card key={index} className={styles.featureCard}>
              <div className={styles.icon}>{feature.icon}</div>
              <Heading level="h3" className={styles.featureTitle}>
                {feature.title}
              </Heading>
              <Text size="base" className={styles.featureDescription}>
                {feature.description}
              </Text>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
