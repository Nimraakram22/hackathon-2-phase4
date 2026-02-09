import React from 'react';
import { Heading } from '../components/design-system/Heading';
import { Text } from '../components/design-system/Text';
import { Card } from '../components/design-system/Card';
import styles from './TypographyShowcase.module.css';

/**
 * Typography Showcase Page
 * Displays all typography styles for testing readability and consistency
 * Used for User Story 2 validation (US2)
 */
export function TypographyShowcase(): React.ReactElement {
  return (
    <div className={styles.showcase}>
      <div className={styles.container}>
        <Heading level="h1" className={styles.pageTitle}>
          Typography Showcase
        </Heading>
        <Text size="lg" className={styles.pageDescription}>
          This page demonstrates all typography styles used in the Agentic Todo application.
          Test readability across different screen sizes (mobile 320px, tablet 768px, desktop 1280px+).
        </Text>

        {/* Heading Styles */}
        <section className={styles.section}>
          <Card title="Heading Styles">
            <div className={styles.headingExamples}>
              <div className={styles.example}>
                <Heading level="h1">Heading 1 - 49px (3.052rem)</Heading>
                <Text size="sm" className={styles.meta}>
                  Font: Inter Bold 700, Line Height: 120%, Letter Spacing: -0.025em
                </Text>
              </div>

              <div className={styles.example}>
                <Heading level="h2">Heading 2 - 39px (2.441rem)</Heading>
                <Text size="sm" className={styles.meta}>
                  Font: Inter Bold 700, Line Height: 120%, Letter Spacing: -0.025em
                </Text>
              </div>

              <div className={styles.example}>
                <Heading level="h3">Heading 3 - 31px (1.953rem)</Heading>
                <Text size="sm" className={styles.meta}>
                  Font: Inter Semibold 600, Line Height: 120%
                </Text>
              </div>

              <div className={styles.example}>
                <Heading level="h4">Heading 4 - 25px (1.563rem)</Heading>
                <Text size="sm" className={styles.meta}>
                  Font: Inter Semibold 600, Line Height: 120%
                </Text>
              </div>

              <div className={styles.example}>
                <Heading level="h5">Heading 5 - 20px (1.25rem)</Heading>
                <Text size="sm" className={styles.meta}>
                  Font: Inter Medium 500, Line Height: 120%
                </Text>
              </div>

              <div className={styles.example}>
                <Heading level="h6">Heading 6 - 16px (1rem)</Heading>
                <Text size="sm" className={styles.meta}>
                  Font: Inter Medium 500, Line Height: 120%, Uppercase, Letter Spacing: 0.025em
                </Text>
              </div>
            </div>
          </Card>
        </section>

        {/* Body Text Styles */}
        <section className={styles.section}>
          <Card title="Body Text Styles">
            <div className={styles.textExamples}>
              <div className={styles.example}>
                <Text size="xl">Extra Large Text - 25px (1.563rem)</Text>
                <Text size="sm" className={styles.meta}>
                  Font: Inter Regular 400, Line Height: 150%
                </Text>
              </div>

              <div className={styles.example}>
                <Text size="lg">Large Text - 20px (1.25rem)</Text>
                <Text size="sm" className={styles.meta}>
                  Font: Inter Regular 400, Line Height: 150%
                </Text>
              </div>

              <div className={styles.example}>
                <Text size="base">Base Text - 16px (1rem) - Default body text</Text>
                <Text size="sm" className={styles.meta}>
                  Font: Inter Regular 400, Line Height: 150%
                </Text>
              </div>

              <div className={styles.example}>
                <Text size="sm">Small Text - 14px (0.875rem)</Text>
                <Text size="sm" className={styles.meta}>
                  Font: Inter Regular 400, Line Height: 150%
                </Text>
              </div>

              <div className={styles.example}>
                <Text size="xs">Extra Small Text - 12.8px (0.8rem)</Text>
                <Text size="sm" className={styles.meta}>
                  Font: Inter Regular 400, Line Height: 150%
                </Text>
              </div>
            </div>
          </Card>
        </section>

        {/* Font Weights */}
        <section className={styles.section}>
          <Card title="Font Weights">
            <div className={styles.weightExamples}>
              <div className={styles.example}>
                <Text size="base" weight="normal">Normal Weight (400) - Regular body text</Text>
              </div>
              <div className={styles.example}>
                <Text size="base" weight="medium">Medium Weight (500) - Emphasized text</Text>
              </div>
              <div className={styles.example}>
                <Text size="base" weight="semibold">Semibold Weight (600) - Strong emphasis</Text>
              </div>
              <div className={styles.example}>
                <Text size="base" weight="bold">Bold Weight (700) - Headings and important text</Text>
              </div>
            </div>
          </Card>
        </section>

        {/* Readability Test */}
        <section className={styles.section}>
          <Card title="Readability Test - Long Form Content">
            <div className={styles.readabilityTest}>
              <Heading level="h3">The Importance of Typography in User Interfaces</Heading>

              <Text size="base">
                Typography is one of the most critical aspects of user interface design. Good typography
                enhances readability, establishes visual hierarchy, and creates a pleasant reading experience
                that keeps users engaged with your content.
              </Text>

              <Text size="base">
                The Major Third typographic scale (1.25 ratio) provides a harmonious progression of font sizes
                that creates clear visual distinction between different levels of content hierarchy. Starting
                from a base size of 16px, each level multiplies by 1.25, resulting in sizes that feel naturally
                related yet distinctly different.
              </Text>

              <Heading level="h4">Line Height and Readability</Heading>

              <Text size="base">
                Line height (leading) significantly impacts readability. For body text, a line height of 150%
                (1.5) provides comfortable spacing between lines, reducing eye strain during extended reading
                sessions. Headings use a tighter line height of 120% (1.2) to maintain visual cohesion and
                emphasize their role as scannable landmarks.
              </Text>

              <Text size="base">
                The optimal line length for readability is between 50-75 characters per line (approximately
                65 characters is ideal). This prevents readers from losing their place when moving from the
                end of one line to the beginning of the next.
              </Text>

              <Heading level="h4">Color Contrast and Accessibility</Heading>

              <Text size="base">
                Color contrast between text and background is crucial for accessibility. The WCAG AA standard
                requires a minimum contrast ratio of 4.5:1 for normal text and 3:1 for large text (18pt+ or
                14pt+ bold). Our design uses dark gray (#1a1a1a) on off-white backgrounds (#fafafa) to achieve
                excellent contrast while reducing the harshness of pure black on pure white.
              </Text>

              <Text size="sm" className={styles.meta}>
                This paragraph demonstrates small text (14px) which should still be comfortably readable
                with proper line height and contrast. Small text is ideal for metadata, captions, and
                supplementary information that supports but doesn't compete with primary content.
              </Text>
            </div>
          </Card>
        </section>

        {/* Color Contrast Examples */}
        <section className={styles.section}>
          <Card title="Color Contrast Examples">
            <div className={styles.contrastExamples}>
              <div className={styles.contrastBox} style={{ backgroundColor: '#fafafa', color: '#1a1a1a' }}>
                <Text size="base" weight="medium">Primary Text on Background</Text>
                <Text size="sm">#1a1a1a on #fafafa - Contrast Ratio: ~15:1 (AAA)</Text>
              </div>

              <div className={styles.contrastBox} style={{ backgroundColor: '#ffffff', color: '#525252' }}>
                <Text size="base" weight="medium">Secondary Text on White</Text>
                <Text size="sm">#525252 on #ffffff - Contrast Ratio: ~7:1 (AAA)</Text>
              </div>

              <div className={styles.contrastBox} style={{ backgroundColor: '#f5f5f5', color: '#737373' }}>
                <Text size="base" weight="medium">Tertiary Text on Light Gray</Text>
                <Text size="sm">#737373 on #f5f5f5 - Contrast Ratio: ~4.6:1 (AA)</Text>
              </div>
            </div>
          </Card>
        </section>

        {/* Responsive Typography Test */}
        <section className={styles.section}>
          <Card title="Responsive Typography Guidelines">
            <div className={styles.responsiveGuide}>
              <Heading level="h4">Mobile (320px - 767px)</Heading>
              <Text size="base">
                • Base font size: 16px (never smaller for body text)
                <br />
                • H1 may scale down to 32px on very small screens
                <br />
                • Line length: 45-60 characters
                <br />
                • Touch targets: Minimum 48x48px
              </Text>

              <Heading level="h4">Tablet (768px - 1023px)</Heading>
              <Text size="base">
                • Base font size: 16px
                <br />
                • Full typographic scale applies
                <br />
                • Line length: 60-70 characters
                <br />
                • Comfortable reading distance
              </Text>

              <Heading level="h4">Desktop (1024px+)</Heading>
              <Text size="base">
                • Base font size: 16px
                <br />
                • Full typographic scale with optimal spacing
                <br />
                • Line length: 65-75 characters (max-width: 65ch)
                <br />
                • Generous whitespace for scannability
              </Text>
            </div>
          </Card>
        </section>

        {/* Testing Instructions */}
        <section className={styles.section}>
          <Card title="Testing Instructions">
            <div className={styles.testingInstructions}>
              <Heading level="h4">How to Test Typography (US2 Validation)</Heading>

              <Text size="base" weight="medium">1. Viewport Testing (T037)</Text>
              <Text size="base">
                • Resize browser to 320px width (mobile)
                <br />
                • Resize to 768px width (tablet)
                <br />
                • Resize to 1280px+ width (desktop)
                <br />
                • Verify all text remains readable at each size
                <br />
                • Check that line lengths don't exceed 75 characters
              </Text>

              <Text size="base" weight="medium">2. Readability Testing</Text>
              <Text size="base">
                • Read the long-form content section above for 2-3 minutes
                <br />
                • Verify no eye strain or difficulty tracking lines
                <br />
                • Check that headings are easily scannable
                <br />
                • Confirm visual hierarchy is clear
              </Text>

              <Text size="base" weight="medium">3. Accessibility Audit (T038)</Text>
              <Text size="base">
                • Use browser DevTools Lighthouse to check contrast ratios
                <br />
                • Verify all text meets WCAG AA standard (4.5:1 minimum)
                <br />
                • Test with screen reader to ensure semantic HTML
                <br />
                • Check keyboard navigation through headings
              </Text>
            </div>
          </Card>
        </section>
      </div>
    </div>
  );
}
