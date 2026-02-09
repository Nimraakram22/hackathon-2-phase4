import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Heading } from '../components/design-system/Heading';
import { Text } from '../components/design-system/Text';
import { Input } from '../components/design-system/Input';
import { Button } from '../components/design-system/Button';
import { Form } from '../components/design-system/Form';
import { setSession } from '../services/auth';
import styles from './Login.module.css';

// Login validation schema
const loginSchema = z.object({
  email: z.string()
    .min(1, 'Email is required')
    .email('Invalid email address'),
  password: z.string()
    .min(1, 'Password is required'),
  rememberMe: z.boolean().optional(),
});

type LoginFormData = z.infer<typeof loginSchema>;

/**
 * Login Page Component
 * User authentication with "Remember Me" option
 * Implements conversion-optimized user journey (US3)
 */
export function Login(): React.ReactElement {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const returnUrl = searchParams.get('returnUrl') || '/chat';

  const [formError, setFormError] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    mode: 'onBlur',
    defaultValues: {
      rememberMe: false,
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    setFormError('');
    setIsLoading(true);

    try {
      // Submit login request
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: data.email,
          password: data.password,
          rememberMe: data.rememberMe,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Login failed');
      }

      const result = await response.json();

      // Store session with appropriate expiration
      // 24 hours default, 30 days with Remember Me
      const expiresInDays = data.rememberMe ? 30 : 1;
      setSession({
        token: result.access_token,
        userId: result.user_id,
        expiresInDays,
      });

      console.log('Login successful, session stored:', { userId: result.user_id, returnUrl });

      // Redirect to return URL or chat page
      navigate(returnUrl);
    } catch (error) {
      setFormError(
        error instanceof Error ? error.message : 'An error occurred during login'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.login}>
      <div className={styles.container}>
        <div className={styles.card}>
          <div className={styles.header}>
            <Heading level="h1" className={styles.title}>
              Welcome Back
            </Heading>
            <Text size="base" className={styles.subtitle}>
              Sign in to continue managing your tasks
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

            <Input
              label="Password"
              type="password"
              placeholder="Enter your password"
              error={errors.password?.message}
              required
              autoComplete="current-password"
              {...register('password')}
            />

            <div className={styles.rememberMeContainer}>
              <label className={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  className={styles.checkbox}
                  {...register('rememberMe')}
                />
                <span className={styles.checkboxText}>
                  Remember me for 30 days
                </span>
              </label>
              <Text size="xs" className={styles.rememberMeHelp}>
                Keep me signed in on this device
              </Text>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              loading={isLoading}
              className={styles.submitButton}
            >
              Sign In
            </Button>
          </Form>

          <div className={styles.footer}>
            <Text size="sm" className={styles.footerText}>
              Don't have an account?{' '}
              <Link to="/signup" className={styles.footerLink}>
                Sign Up
              </Link>
            </Text>
          </div>
        </div>
      </div>
    </div>
  );
}
