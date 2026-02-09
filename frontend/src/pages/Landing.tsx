import React from 'react';
import { HeroSection } from '../components/landing/HeroSection';
import { FeaturesSection, Feature } from '../components/landing/FeaturesSection';
import { Navigation } from '../components/layout/Navigation';
import styles from './Landing.module.css';

// Feature icons (using simple SVG icons)
const CheckCircleIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const SparklesIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
  </svg>
);

const ChatBubbleIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z" />
  </svg>
);

const LightningBoltIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
  </svg>
);

/**
 * Landing Page Component
 * Marketing page with hero section, features, and primary CTA
 * Implements conversion-optimized user journey (US3)
 */
export function Landing(): React.ReactElement {
  const features: Feature[] = [
    {
      icon: <SparklesIcon />,
      title: 'AI-Powered Task Management',
      description: 'Chat naturally with AI to create, organize, and manage your tasks. No complex forms or menus.',
    },
    {
      icon: <ChatBubbleIcon />,
      title: 'Conversational Interface',
      description: 'Simply tell the AI what you need to do. It understands context and helps you stay organized.',
    },
    {
      icon: <LightningBoltIcon />,
      title: 'Lightning Fast',
      description: 'Create tasks in seconds with natural language. No clicking through multiple screens.',
    },
    {
      icon: <CheckCircleIcon />,
      title: 'Smart Organization',
      description: 'AI automatically categorizes and prioritizes your tasks based on your conversation.',
    },
  ];

  return (
    <div className={styles.landing}>
      <Navigation variant="public" />

      <main>
        <HeroSection
          headline="Manage Your Tasks with AI"
          subheadline="Stop wrestling with complex task managers. Just chat with AI and get things done. Simple, fast, and intelligent task management."
          ctaText="Get Started Free"
          ctaLink="/signup"
        />

        <FeaturesSection features={features} />

        {/* Social Proof Section */}
        <section className={styles.socialProof}>
          <div className={styles.container}>
            <p className={styles.socialProofText}>
              Join thousands of users who manage their tasks effortlessly with AI
            </p>
          </div>
        </section>

        {/* Final CTA Section */}
        <section className={styles.finalCta}>
          <div className={styles.container}>
            <div className={styles.ctaContent}>
              <h2 className={styles.ctaHeadline}>Ready to Get Organized?</h2>
              <p className={styles.ctaSubheadline}>
                Start managing your tasks with AI assistance today. No credit card required.
              </p>
              <div className={styles.ctaButtons}>
                <a href="/signup" className={styles.ctaPrimary}>
                  Create Free Account
                </a>
                <a href="/login" className={styles.ctaSecondary}>
                  Sign In
                </a>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className={styles.footer}>
        <div className={styles.container}>
          <div className={styles.footerContent}>
            <p className={styles.footerText}>
              © 2026 Agentic Todo. All rights reserved.
            </p>
            <nav className={styles.footerNav}>
              <a href="/contact" className={styles.footerLink}>Contact</a>
              <a href="/privacy" className={styles.footerLink}>Privacy</a>
              <a href="/terms" className={styles.footerLink}>Terms</a>
            </nav>
          </div>
        </div>
      </footer>
    </div>
  );
}
