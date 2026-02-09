import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Heading } from '../components/design-system/Heading';
import { Text } from '../components/design-system/Text';
import { Input } from '../components/design-system/Input';
import { Button } from '../components/design-system/Button';
import { Form } from '../components/design-system/Form';
import { Card } from '../components/design-system/Card';
import { Navigation } from '../components/layout/Navigation';
import styles from './Contact.module.css';

// Contact form validation schema
const contactSchema = z.object({
  name: z.string()
    .min(1, 'Name is required')
    .max(100, 'Name too long'),
  email: z.string()
    .min(1, 'Email is required')
    .email('Invalid email address')
    .max(255, 'Email too long'),
  subject: z.string()
    .min(1, 'Subject is required')
    .max(200, 'Subject too long'),
  message: z.string()
    .min(10, 'Message must be at least 10 characters')
    .max(5000, 'Message too long (max 5000 characters)'),
});

type ContactFormData = z.infer<typeof contactSchema>;

interface FAQ {
  question: string;
  answer: string;
}

const faqs: FAQ[] = [
  {
    question: 'How do I create a task?',
    answer: 'Simply chat with the AI assistant on the main page. Tell it what you need to do, and it will create tasks for you automatically.',
  },
  {
    question: 'Can I edit or delete tasks?',
    answer: 'Yes! You can ask the AI to modify or remove tasks by chatting naturally. For example, "Delete my grocery shopping task" or "Change the deadline for my report to Friday."',
  },
  {
    question: 'Is my data secure?',
    answer: 'Absolutely. We use industry-standard encryption for all data transmission and storage. Your tasks and conversations are private and never shared with third parties.',
  },
  {
    question: 'How does the AI understand my tasks?',
    answer: 'Our AI uses natural language processing to understand your intent. It can extract task details, deadlines, and priorities from conversational text.',
  },
  {
    question: 'Can I use this on mobile?',
    answer: 'Yes! Agentic Todo is fully responsive and works great on mobile devices, tablets, and desktops.',
  },
  {
    question: 'What if I need help with a specific feature?',
    answer: 'Use this contact form to reach our support team. We typically respond within 24 hours on business days.',
  },
  {
    question: 'Is there a limit to how many tasks I can create?',
    answer: 'No limits! Create as many tasks as you need. The AI will help you stay organized no matter how many tasks you have.',
  },
];

/**
 * Contact Page Component
 * Contact form with FAQ section
 * Implements form simplification and input design (US7)
 */
export function Contact(): React.ReactElement {
  const [formError, setFormError] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [submissionId, setSubmissionId] = useState<number | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ContactFormData>({
    resolver: zodResolver(contactSchema),
    mode: 'onBlur',
  });

  const onSubmit = async (data: ContactFormData) => {
    setFormError('');
    setIsLoading(true);
    setIsSuccess(false);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/contact`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to submit contact form');
      }

      const result = await response.json();

      // Show success message
      setIsSuccess(true);
      setSubmissionId(result.id);

      // Reset form
      reset();

      // Scroll to success message
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (error) {
      setFormError(
        error instanceof Error ? error.message : 'An error occurred while submitting the form'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.contact}>
      <Navigation variant="public" />

      <main className={styles.main}>
        <div className={styles.container}>
          {/* Success Message */}
          {isSuccess && (
            <div className={styles.successBanner} role="alert" aria-live="polite">
              <div className={styles.successIcon}>✓</div>
              <div className={styles.successContent}>
                <Heading level="h3" className={styles.successTitle}>
                  Message Received!
                </Heading>
                <Text size="base" className={styles.successText}>
                  Thank you for contacting us. We've received your message (ID: #{submissionId}) and will get back to you within 24 hours.
                </Text>
              </div>
            </div>
          )}

          {/* Header */}
          <div className={styles.header}>
            <Heading level="h1" className={styles.title}>
              Get in Touch
            </Heading>
            <Text size="lg" className={styles.subtitle}>
              Have a question or feedback? We'd love to hear from you.
            </Text>
          </div>

          <div className={styles.content}>
            {/* Contact Form */}
            <div className={styles.formSection}>
              <Card>
                <Form error={formError} onSubmit={handleSubmit(onSubmit)}>
                  <Input
                    label="Name"
                    type="text"
                    placeholder="Your name"
                    error={errors.name?.message}
                    required
                    autoComplete="name"
                    {...register('name')}
                  />

                  <Input
                    label="Email"
                    type="email"
                    placeholder="you@example.com"
                    error={errors.email?.message}
                    required
                    autoComplete="email"
                    helperText="We'll never share your email with anyone else"
                    {...register('email')}
                  />

                  <div className={styles.selectWrapper}>
                    <label htmlFor="subject" className={styles.selectLabel}>
                      Subject <span className={styles.required} aria-label="required">*</span>
                    </label>
                    <select
                      id="subject"
                      className={`${styles.select} ${errors.subject ? styles.selectError : ''}`}
                      {...register('subject')}
                      aria-invalid={errors.subject ? 'true' : 'false'}
                      aria-describedby={errors.subject ? 'subject-error' : undefined}
                    >
                      <option value="">Select a subject</option>
                      <option value="General Inquiry">General Inquiry</option>
                      <option value="Feature Request">Feature Request</option>
                      <option value="Bug Report">Bug Report</option>
                      <option value="Account Issue">Account Issue</option>
                      <option value="Billing Question">Billing Question</option>
                      <option value="Other">Other</option>
                    </select>
                    {errors.subject && (
                      <span id="subject-error" className={styles.errorMessage} role="alert">
                        {errors.subject.message}
                      </span>
                    )}
                  </div>

                  <div className={styles.textareaWrapper}>
                    <label htmlFor="message" className={styles.textareaLabel}>
                      Message <span className={styles.required} aria-label="required">*</span>
                    </label>
                    <textarea
                      id="message"
                      className={`${styles.textarea} ${errors.message ? styles.textareaError : ''}`}
                      placeholder="Tell us more about your inquiry..."
                      rows={6}
                      {...register('message')}
                      aria-invalid={errors.message ? 'true' : 'false'}
                      aria-describedby={errors.message ? 'message-error' : 'message-helper'}
                    />
                    {errors.message ? (
                      <span id="message-error" className={styles.errorMessage} role="alert">
                        {errors.message.message}
                      </span>
                    ) : (
                      <span id="message-helper" className={styles.helperText}>
                        Minimum 10 characters, maximum 5000 characters
                      </span>
                    )}
                  </div>

                  <Button
                    type="submit"
                    variant="primary"
                    size="lg"
                    loading={isLoading}
                    className={styles.submitButton}
                  >
                    Send Message
                  </Button>
                </Form>
              </Card>
            </div>

            {/* FAQ Section */}
            <div className={styles.faqSection}>
              <Heading level="h2" className={styles.faqTitle}>
                Frequently Asked Questions
              </Heading>

              <div className={styles.faqList}>
                {faqs.map((faq, index) => (
                  <Card key={index} className={styles.faqCard}>
                    <Heading level="h3" className={styles.faqQuestion}>
                      {faq.question}
                    </Heading>
                    <Text size="base" className={styles.faqAnswer}>
                      {faq.answer}
                    </Text>
                  </Card>
                ))}
              </div>

              <div className={styles.faqFooter}>
                <Text size="base" className={styles.faqFooterText}>
                  Still have questions? Use the contact form to reach our support team.
                </Text>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
