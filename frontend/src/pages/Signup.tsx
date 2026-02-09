import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import { Heading } from '../components/design-system/Heading';
import { Text } from '../components/design-system/Text';
import { Input } from '../components/design-system/Input';
import { Button } from '../components/design-system/Button';
import { Form } from '../components/design-system/Form';
import { setSession } from '../services/auth';
import styles from './Signup.module.css';

// Password validation schema
const signupSchema = z.object({
  email: z.string()
    .min(1, 'Email is required')
    .email('Invalid email address')
    .max(255, 'Email too long'),
  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .max(128, 'Password too long')
    .refine(
      (password) => {
        // Check for at least 3 of 4 character types
        const hasUppercase = /[A-Z]/.test(password);
        const hasLowercase = /[a-z]/.test(password);
        const hasNumber = /[0-9]/.test(password);
        const hasSpecial = /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password);
        const typesCount = [hasUppercase, hasLowercase, hasNumber, hasSpecial].filter(Boolean).length;
        return typesCount >= 3;
      },
      'Password must contain at least 3 of: uppercase, lowercase, numbers, special characters'
    ),
  confirmPassword: z.string().min(1, 'Please confirm your password'),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
});

type SignupFormData = z.infer<typeof signupSchema>;

type PasswordStrength = 'weak' | 'medium' | 'strong' | null;

/**
 * Signup Page Component
 * User registration with password strength indicator and validation
 * Implements conversion-optimized user journey (US3)
 */
export function Signup(): React.ReactElement {
  const navigate = useNavigate();
  const [formError, setFormError] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState<PasswordStrength>(null);
  const [isPwnedChecking, setIsPwnedChecking] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<SignupFormData>({
    resolver: zodResolver(signupSchema),
    mode: 'onBlur',
  });

  const password = watch('password');

  // Calculate password strength
  React.useEffect(() => {
    if (!password) {
      setPasswordStrength(null);
      return;
    }

    const hasUppercase = /[A-Z]/.test(password);
    const hasLowercase = /[a-z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    const hasSpecial = /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password);
    const typesCount = [hasUppercase, hasLowercase, hasNumber, hasSpecial].filter(Boolean).length;

    if (password.length < 8) {
      setPasswordStrength('weak');
    } else if (password.length >= 8 && typesCount >= 2) {
      setPasswordStrength('medium');
    } else if (password.length >= 12 && typesCount >= 3) {
      setPasswordStrength('strong');
    } else {
      setPasswordStrength('weak');
    }
  }, [password]);

  // Check password against Have I Been Pwned API
  const checkPasswordPwned = async (password: string): Promise<boolean> => {
    try {
      setIsPwnedChecking(true);
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/auth/check-password-pwned`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password }),
      });

      const data = await response.json();
      return data.isPwned;
    } catch (error) {
      console.error('Error checking password:', error);
      return false; // Don't block signup if check fails
    } finally {
      setIsPwnedChecking(false);
    }
  };

  const onSubmit = async (data: SignupFormData) => {
    setFormError('');
    setIsLoading(true);

    try {
      // Check if password has been pwned
      const isPwned = await checkPasswordPwned(data.password);
      if (isPwned) {
        setFormError(
          'This password has been found in data breaches and is not secure. Please choose a different password.'
        );
        setIsLoading(false);
        return;
      }

      // Submit signup request
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: data.email,
          password: data.password,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Signup failed');
      }

      const result = await response.json();

      // Store session with 24 hour expiration
      setSession({
        token: result.access_token,
        userId: result.user_id,
        expiresInDays: 1,
      });

      // Redirect to chat page
      navigate('/chat');
    } catch (error) {
      setFormError(
        error instanceof Error ? error.message : 'An error occurred during signup'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.signup}>
      <div className={styles.container}>
        <div className={styles.card}>
          <div className={styles.header}>
            <Heading level="h1" className={styles.title}>
              Create Your Account
            </Heading>
            <Text size="base" className={styles.subtitle}>
              Start managing your tasks with AI assistance
            </Text>
          </div>

          <Form error={formError} onSubmit={handleSubmit(onSubmit)}>
            <Input
              label="Email"
              type="email"
              placeholder="you@example.com"
              error={errors.email?.message}
              required
              autoComplete="email"
              {...register('email')}
            />

            <div>
              <Input
                label="Password"
                type="password"
                placeholder="Create a strong password"
                error={errors.password?.message}
                required
                autoComplete="new-password"
                {...register('password')}
              />

              {password && (
                <div className={styles.passwordStrength}>
                  <div className={styles.strengthLabel}>Password Strength</div>
                  <div className={styles.strengthBar}>
                    <div
                      className={`${styles.strengthFill} ${
                        passwordStrength ? styles[passwordStrength] : ''
                      }`}
                    />
                  </div>
                  <div
                    className={`${styles.strengthText} ${
                      passwordStrength ? styles[passwordStrength] : ''
                    }`}
                  >
                    {passwordStrength === 'weak' && 'Weak - Add more character types'}
                    {passwordStrength === 'medium' && 'Medium - Consider adding more characters'}
                    {passwordStrength === 'strong' && 'Strong - Great password!'}
                  </div>
                </div>
              )}

              <ul className={styles.passwordRequirements}>
                <li>At least 8 characters</li>
                <li>At least 3 of: uppercase, lowercase, numbers, special characters</li>
                <li>Not found in data breaches</li>
              </ul>
            </div>

            <Input
              label="Confirm Password"
              type="password"
              placeholder="Re-enter your password"
              error={errors.confirmPassword?.message}
              required
              autoComplete="new-password"
              {...register('confirmPassword')}
            />

            <Button
              type="submit"
              variant="primary"
              size="lg"
              loading={isLoading || isPwnedChecking}
              className={styles.submitButton}
            >
              {isPwnedChecking ? 'Checking password security...' : 'Create Account'}
            </Button>
          </Form>

          <div className={styles.footer}>
            <Text size="sm" className={styles.footerText}>
              Already have an account?{' '}
              <Link to="/login" className={styles.footerLink}>
                Sign In
              </Link>
            </Text>
          </div>
        </div>
      </div>
    </div>
  );
}
