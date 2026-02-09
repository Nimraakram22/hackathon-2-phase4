/**
 * TypeScript type definitions for UI/UX Enhancement feature
 * Generated from OpenAPI spec: contact-api.yaml
 * Date: 2026-01-31
 */

// ============================================================================
// Contact Form Types
// ============================================================================

export enum SubmissionStatus {
  NEW = 'new',
  IN_PROGRESS = 'in-progress',
  RESOLVED = 'resolved',
  CLOSED = 'closed'
}

export interface ContactSubmissionCreate {
  name: string;
  email: string;
  subject: string;
  message: string;
}

export interface ContactSubmissionResponse {
  id: number;
  name: string;
  email: string;
  subject: string;
  message: string;
  status: SubmissionStatus;
  created_at: string; // ISO 8601 format
}

export interface ContactSubmissionAdmin extends ContactSubmissionResponse {
  assigned_to: string | null;
  response_sent: boolean;
  updated_at: string; // ISO 8601 format
  ip_address: string | null;
  user_agent: string | null;
}

export interface ContactSubmissionUpdate {
  status?: SubmissionStatus;
  assigned_to?: string | null;
  response_sent?: boolean;
}

// ============================================================================
// API Response Types
// ============================================================================

export interface ValidationErrorDetail {
  type: string;
  loc: (string | number)[];
  msg: string;
  input?: any;
}

export interface ValidationError {
  detail: ValidationErrorDetail[];
}

export interface ApiError {
  detail: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

// ============================================================================
// Form Validation Schemas (Zod)
// ============================================================================

import { z } from 'zod';

export const contactSubmissionSchema = z.object({
  name: z.string()
    .min(1, 'Name is required')
    .max(100, 'Name must be less than 100 characters'),
  email: z.string()
    .email('Invalid email address')
    .max(255, 'Email must be less than 255 characters'),
  subject: z.enum(['Bug Report', 'Feature Request', 'General Question', 'Feedback'], {
    errorMap: () => ({ message: 'Please select a valid subject' })
  }),
  message: z.string()
    .min(10, 'Message must be at least 10 characters')
    .max(5000, 'Message must be less than 5000 characters')
});

export type ContactSubmissionFormData = z.infer<typeof contactSubmissionSchema>;

// ============================================================================
// Design System Types
// ============================================================================

export interface TypographyScale {
  base: string;      // 16px
  lg: string;        // 20px (16 * 1.25)
  xl: string;        // 25px (20 * 1.25)
  '2xl': string;     // 31px (25 * 1.25)
  '3xl': string;     // 39px (31 * 1.25)
  '4xl': string;     // 49px (39 * 1.25)
}

export interface SpacingScale {
  1: string;   // 8px
  2: string;   // 16px
  3: string;   // 24px
  4: string;   // 32px
  6: string;   // 48px
  8: string;   // 64px
  12: string;  // 96px
}

export interface ColorShades {
  50: string;
  100: string;
  200: string;
  300: string;
  400: string;
  500: string;
  600: string;
  700: string;
  800: string;
  900: string;
}

export interface ColorPalette {
  neutral: ColorShades;
  primary: {
    50: string;
    500: string;
    700: string;
  };
  accent: {
    50: string;
    500: string;
    700: string;
  };
}

export interface DesignTokens {
  typography: TypographyScale;
  spacing: SpacingScale;
  colors: ColorPalette;
}

// ============================================================================
// Authentication Types
// ============================================================================

export interface LoginCredentials {
  email: string;
  password: string;
  remember_me?: boolean;
}

export interface SignupCredentials {
  email: string;
  password: string;
  confirm_password: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number; // seconds
}

export interface User {
  id: number;
  email: string;
  created_at: string;
}

// ============================================================================
// Password Validation Types
// ============================================================================

export enum PasswordStrength {
  WEAK = 'weak',
  MEDIUM = 'medium',
  STRONG = 'strong'
}

export interface PasswordValidationResult {
  strength: PasswordStrength;
  score: number; // 0-100
  feedback: string[];
  meetsRequirements: boolean;
}

export interface PasswordRequirements {
  minLength: boolean;
  hasUppercase: boolean;
  hasLowercase: boolean;
  hasNumber: boolean;
  hasSpecialChar: boolean;
  notPwned: boolean;
}

// ============================================================================
// Component Props Types
// ============================================================================

export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  type?: 'button' | 'submit' | 'reset';
  onClick?: () => void;
  children: React.ReactNode;
  className?: string;
}

export interface InputProps {
  type?: 'text' | 'email' | 'password' | 'number';
  label: string;
  name: string;
  placeholder?: string;
  error?: string;
  disabled?: boolean;
  required?: boolean;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onBlur?: (e: React.FocusEvent<HTMLInputElement>) => void;
  className?: string;
}

export interface FormProps {
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
  children: React.ReactNode;
  className?: string;
}

export interface CardProps {
  title?: string;
  children: React.ReactNode;
  className?: string;
}

// ============================================================================
// API Client Types
// ============================================================================

export interface ApiClientConfig {
  baseURL: string;
  timeout?: number;
  headers?: Record<string, string>;
}

export interface ApiResponse<T> {
  data: T;
  status: number;
  statusText: string;
}

export interface ApiErrorResponse {
  error: ApiError | ValidationError;
  status: number;
  statusText: string;
}

// ============================================================================
// Route Types
// ============================================================================

export interface RouteConfig {
  path: string;
  component: React.ComponentType;
  protected?: boolean;
  middleware?: Array<(context: any) => Promise<void>>;
}

export interface NavigationItem {
  label: string;
  path: string;
  icon?: React.ComponentType;
  protected?: boolean;
}

// ============================================================================
// Accessibility Types
// ============================================================================

export interface AriaAttributes {
  'aria-label'?: string;
  'aria-labelledby'?: string;
  'aria-describedby'?: string;
  'aria-required'?: boolean;
  'aria-invalid'?: boolean;
  'aria-live'?: 'polite' | 'assertive' | 'off';
  role?: string;
}

// ============================================================================
// Performance Types
// ============================================================================

export interface PerformanceMetrics {
  fcp: number; // First Contentful Paint (ms)
  lcp: number; // Largest Contentful Paint (ms)
  tbt: number; // Total Blocking Time (ms)
  cls: number; // Cumulative Layout Shift
  fid: number; // First Input Delay (ms)
}

export interface LighthouseScore {
  performance: number;
  accessibility: number;
  bestPractices: number;
  seo: number;
}
