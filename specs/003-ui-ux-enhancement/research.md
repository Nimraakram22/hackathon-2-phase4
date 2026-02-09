# Research: UI/UX Enhancement Technical Decisions

**Feature**: 003-ui-ux-enhancement
**Date**: 2026-01-31
**Status**: Complete

## Overview

This document captures all technical research and decisions made during Phase 0 planning for the UI/UX Enhancement feature. Each decision includes rationale, alternatives considered, and references to authoritative documentation.

---

## 1. React Router Version & Protected Routes

### Decision
**Use React Router v7 with middleware-based authentication**

### Rationale
- React Router v7 is the latest version with improved TypeScript support and modern patterns
- Middleware-based authentication provides centralized, reusable auth logic
- Supports both server-side and client-side route protection
- Better integration with React 18+ features

### Implementation Pattern
```typescript
// Authentication middleware
async function authMiddleware({ request, context }, next) {
  const session = await getSession(request.headers.get("Cookie"));

  if (!session.userId) {
    return redirect("/login");
  }

  // Add user to context for downstream loaders
  context.user = await getUserById(session.userId);

  return next();
}

// Protected route configuration
{
  path: '/chat',
  middleware: [authMiddleware],
  loader: chatLoader,
  Component: ChatPage
}
```

### Alternatives Considered
- **React Router v6**: Rejected - older version, less TypeScript support, no middleware pattern
- **Custom HOC approach**: Rejected - less maintainable, duplicates logic across routes
- **Route guards**: Rejected - v7 middleware is more idiomatic and powerful

### References
- Context7: `/remix-run/react-router` (v7.6.2)
- Source: https://context7.com/remix-run/react-router/llms.txt

---

## 2. Form Validation Library

### Decision
**Use React Hook Form v7 with Zod resolver for type-safe validation**

### Rationale
- React Hook Form provides excellent performance with minimal re-renders
- Zod integration enables type-safe schema validation with TypeScript inference
- Built-in support for real-time validation (onChange, onBlur, onSubmit modes)
- Comprehensive error handling with field-specific error messages
- 274 code snippets available in Context7 (high adoption, well-documented)

### Implementation Pattern
```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const signupSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Must contain uppercase letter')
    .regex(/[0-9]/, 'Must contain number')
    .regex(/[^A-Za-z0-9]/, 'Must contain special character'),
  confirmPassword: z.string()
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword']
});

type SignupFormData = z.infer<typeof signupSchema>;

function SignupForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<SignupFormData>({
    resolver: zodResolver(signupSchema),
    mode: 'onBlur' // Real-time validation on blur
  });

  const onSubmit = async (data: SignupFormData) => {
    // Submit to API
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('email')} />
      {errors.email && <span>{errors.email.message}</span>}
      {/* ... */}
    </form>
  );
}
```

### Alternatives Considered
- **Formik**: Rejected - heavier bundle size, more re-renders, less TypeScript support
- **Manual validation**: Rejected - error-prone, duplicates logic, no type safety
- **Native HTML5 validation**: Rejected - insufficient for complex requirements (password strength, Have I Been Pwned check)

### References
- Context7: `/react-hook-form/react-hook-form` (v7.66.0)
- Source: https://context7.com/react-hook-form/react-hook-form/llms.txt

---

## 3. CSS Architecture Approach

### Decision
**Use CSS Modules with CSS Custom Properties (design tokens) for design system**

### Rationale
- CSS Modules provide scoped styles without global namespace pollution
- CSS Custom Properties enable centralized design tokens (colors, spacing, typography)
- No build-time compilation required (unlike Tailwind)
- Better for design system approach with reusable component styles
- Maintains separation of concerns (styles in .module.css files)
- Easier for designers to understand than utility-first approaches

### Implementation Pattern
```css
/* styles/design-tokens.css */
:root {
  /* Typography Scale (Major Third 1.25) */
  --font-size-base: 16px;
  --font-size-lg: 20px;
  --font-size-xl: 25px;
  --font-size-2xl: 31px;
  --font-size-3xl: 39px;

  /* 8-point Spacing System */
  --spacing-1: 8px;
  --spacing-2: 16px;
  --spacing-3: 24px;
  --spacing-4: 32px;
  --spacing-6: 48px;
  --spacing-8: 64px;
  --spacing-12: 96px;

  /* Color Palette (60-30-10 rule) */
  --color-neutral-50: #fafafa;
  --color-neutral-900: #1a1a1a;
  --color-primary-500: #[TBD]; /* From brand research */
  --color-accent-500: #[TBD]; /* From brand research */
}

/* components/Button.module.css */
.button {
  padding: var(--spacing-2) var(--spacing-4);
  font-size: var(--font-size-base);
  background-color: var(--color-primary-500);
  color: var(--color-neutral-50);
  border-radius: 8px;
}
```

### Alternatives Considered
- **Tailwind CSS**: Rejected - utility-first approach conflicts with design system component library, steeper learning curve, larger HTML markup
- **Styled Components**: Rejected - runtime CSS-in-JS has performance overhead, increases bundle size
- **Vanilla CSS**: Rejected - no scoping, global namespace pollution, harder to maintain

### References
- Best practice based on design system requirements and component library approach
- CSS Custom Properties: MDN Web Docs (standard browser feature)

---

## 4. Icon Library

### Decision
**Use Heroicons v2 (React components)**

### Rationale
- MIT licensed (free, no attribution required)
- High-quality hand-crafted SVG icons
- Official React component library with TypeScript support
- Consistent design language (matches Tailwind ecosystem)
- Two variants: outline (24x24) and solid (20x20)
- 24 code snippets in Context7, high source reputation

### Implementation Pattern
```typescript
import { EnvelopeIcon, UserIcon, CheckCircleIcon } from '@heroicons/react/24/outline';

function ContactForm() {
  return (
    <div>
      <label>
        <EnvelopeIcon className="w-5 h-5" />
        Email
      </label>
      <input type="email" />
    </div>
  );
}
```

### Alternatives Considered
- **Feather Icons**: Rejected - smaller icon set, less active maintenance
- **Font Awesome**: Rejected - requires paid license for full icon set, heavier bundle
- **Custom SVG icons**: Rejected - time-consuming to create, inconsistent design

### References
- Context7: `/tailwindlabs/heroicons`
- Source: https://context7.com/tailwindlabs/heroicons/llms.txt

---

## 5. E2E Testing Framework

### Decision
**Use Playwright for end-to-end testing**

### Rationale
- Modern framework with excellent TypeScript support
- Cross-browser testing (Chromium, Firefox, WebKit) out of the box
- Auto-wait and web-first assertions reduce flakiness
- Better performance than Cypress (runs in Node.js, not browser)
- Built-in test isolation and parallel execution
- 13,277 code snippets in Context7 (highest coverage)

### Implementation Pattern
```typescript
// tests/e2e/landing-to-signup.spec.ts
import { test, expect } from '@playwright/test';

test('user can navigate from landing page to signup', async ({ page }) => {
  // Navigate to landing page
  await page.goto('/');

  // Verify hero section visible
  await expect(page.getByRole('heading', { name: /manage your tasks/i })).toBeVisible();

  // Click primary CTA
  await page.getByRole('button', { name: /get started/i }).click();

  // Verify redirected to signup
  await expect(page).toHaveURL('/signup');

  // Verify signup form visible
  await expect(page.getByLabel(/email address/i)).toBeVisible();
  await expect(page.getByLabel(/create password/i)).toBeVisible();
});

test('signup form validates password requirements', async ({ page }) => {
  await page.goto('/signup');

  // Enter weak password
  await page.getByLabel(/create password/i).fill('weak');
  await page.getByLabel(/create password/i).blur();

  // Verify validation error
  await expect(page.getByText(/must be at least 8 characters/i)).toBeVisible();
});
```

### Alternatives Considered
- **Cypress**: Rejected - runs in browser (slower), less TypeScript support, more flaky tests
- **Selenium**: Rejected - outdated, verbose API, poor developer experience
- **Puppeteer**: Rejected - Chromium-only, no built-in test runner

### References
- Context7: `/microsoft/playwright.dev`
- Source: https://context7.com/microsoft/playwright.dev/llms.txt

---

## 6. Backend: FastAPI REST Endpoint Patterns

### Decision
**Use FastAPI with Pydantic v2 models for request/response validation**

### Rationale
- Automatic request body parsing and validation
- Type-safe with full editor support
- Automatic OpenAPI schema generation
- Structured error responses with field-specific messages
- Async support for better performance

### Implementation Pattern
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class ContactSubmissionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    subject: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=10, max_length=5000)

class ContactSubmissionResponse(BaseModel):
    id: int
    name: str
    email: str
    subject: str
    message: str
    status: str
    created_at: str

app = FastAPI()

@app.post("/api/contact", response_model=ContactSubmissionResponse, status_code=201)
async def create_contact_submission(submission: ContactSubmissionCreate):
    # Validation happens automatically
    # Create submission in database
    # Send email notification
    return submission_response
```

### Alternatives Considered
- **Manual validation**: Rejected - error-prone, no automatic documentation
- **Marshmallow**: Rejected - less integrated with FastAPI, more verbose

### References
- Context7: `/websites/fastapi_tiangolo`
- Source: https://fastapi.tiangolo.com/tutorial/body

---

## 7. Database: SQLModel for Contact Submissions

### Decision
**Use SQLModel with Pydantic v2 for type-safe ORM**

### Rationale
- Combines SQLAlchemy (ORM) with Pydantic (validation)
- Single model definition for database and API schemas
- Full TypeScript-like type safety in Python
- Automatic validation on database writes
- Excellent FastAPI integration

### Implementation Pattern
```python
from sqlmodel import Field, SQLModel, create_engine, Session
from typing import Optional
from datetime import datetime

class ContactSubmissionBase(SQLModel):
    name: str = Field(max_length=100, index=False)
    email: str = Field(max_length=255, index=True)
    subject: str = Field(max_length=200, index=False)
    message: str = Field(max_length=5000, index=False)

class ContactSubmission(ContactSubmissionBase, table=True):
    __tablename__ = "contact_submissions"

    id: Optional[int] = Field(default=None, primary_key=True)
    status: str = Field(default="new", max_length=20, index=True)
    assigned_to: Optional[str] = Field(default=None, max_length=255)
    response_sent: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)

class ContactSubmissionCreate(ContactSubmissionBase):
    pass

class ContactSubmissionPublic(ContactSubmissionBase):
    id: int
    status: str
    created_at: datetime
```

### Alternatives Considered
- **Raw SQLAlchemy**: Rejected - more verbose, no automatic Pydantic validation
- **Django ORM**: Rejected - not compatible with FastAPI async patterns
- **Tortoise ORM**: Rejected - less mature, smaller community

### References
- Context7: `/websites/sqlmodel_tiangolo`
- Source: https://sqlmodel.tiangolo.com/tutorial/fastapi/relationships

---

## 8. Password Security: Have I Been Pwned Integration

### Decision
**Use Have I Been Pwned k-anonymity API with hash prefix approach**

### Rationale
- k-anonymity model ensures password never leaves client/server
- Only first 5 characters of SHA-1 hash sent to API
- Free API, no rate limiting for reasonable use
- Industry-standard approach for password breach checking
- Recommended by NIST and security experts

### Implementation Pattern
```python
import hashlib
import httpx
from typing import Tuple

async def check_password_pwned(password: str) -> Tuple[bool, int]:
    """
    Check if password appears in Have I Been Pwned database.
    Returns (is_pwned, occurrence_count).
    """
    # Hash password with SHA-1
    sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()

    # Split into prefix (first 5 chars) and suffix
    prefix, suffix = sha1_hash[:5], sha1_hash[5:]

    # Query API with prefix only (k-anonymity)
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.pwnedpasswords.com/range/{prefix}",
            headers={"User-Agent": "Agentic-Todo-App"}
        )

    # Check if suffix appears in response
    for line in response.text.splitlines():
        hash_suffix, count = line.split(':')
        if hash_suffix == suffix:
            return True, int(count)

    return False, 0

# Usage in signup endpoint
async def validate_password(password: str) -> None:
    is_pwned, count = await check_password_pwned(password)
    if is_pwned:
        raise ValueError(
            f"This password has been exposed in {count} data breaches. "
            "Please choose a different password."
        )
```

### Alternatives Considered
- **Direct API with full hash**: Rejected - less secure, sends full password hash
- **Local database**: Rejected - 30GB+ database, maintenance overhead
- **Third-party library (pwnedpasswords)**: Considered - adds dependency, but may simplify implementation

### References
- Have I Been Pwned API: https://haveibeenpwned.com/API/v3#PwnedPasswords
- k-anonymity model: https://www.troyhunt.com/ive-just-launched-pwned-passwords-version-2/

---

## 9. Email Service for Contact Form Notifications

### Decision
**Use SendGrid for email notifications**

### Rationale
- Free tier: 100 emails/day (sufficient for contact form)
- Simple REST API with Python SDK
- Better developer experience than AWS SES
- Built-in email templates and analytics
- No AWS account/credentials required
- Easier setup and testing

### Implementation Pattern
```python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

async def send_contact_notification(submission: ContactSubmission):
    """Send email notification when contact form submitted."""
    message = Mail(
        from_email='noreply@agentic-todo.com',
        to_emails='support@agentic-todo.com',
        subject=f'New Contact Form Submission: {submission.subject}',
        html_content=f'''
            <h2>New Contact Form Submission</h2>
            <p><strong>ID:</strong> {submission.id}</p>
            <p><strong>Name:</strong> {submission.name}</p>
            <p><strong>Email:</strong> {submission.email}</p>
            <p><strong>Subject:</strong> {submission.subject}</p>
            <p><strong>Message:</strong></p>
            <p>{submission.message}</p>
            <p><strong>Submitted:</strong> {submission.created_at}</p>
        '''
    )

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        return response.status_code == 202
    except Exception as e:
        # Log error but don't fail submission
        print(f"Email notification failed: {e}")
        return False
```

### Alternatives Considered
- **AWS SES**: Rejected - more complex setup, requires AWS account, harder to test locally
- **Mailgun**: Rejected - similar to SendGrid but less popular, smaller free tier
- **SMTP (Gmail)**: Rejected - rate limits, authentication issues, not production-ready

### References
- SendGrid Python SDK: https://github.com/sendgrid/sendgrid-python
- SendGrid API Docs: https://docs.sendgrid.com/api-reference/mail-send/mail-send

---

## 10. Typography: Font Selection and Loading

### Decision
**Use Google Fonts with preconnect optimization**

### Rationale
- Free, reliable CDN with global coverage
- Large selection of high-quality typefaces
- Variable font support for better performance
- Easy integration with React
- Automatic font subsetting and optimization

### Recommended Fonts
- **Headings**: Inter (modern, readable, excellent at all sizes)
- **Body**: Inter (single typeface for consistency, reduces HTTP requests)
- **Fallback**: system-ui, -apple-system, sans-serif

### Implementation Pattern
```html
<!-- In index.html head -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```

```css
/* styles/typography.css */
:root {
  --font-family-base: 'Inter', system-ui, -apple-system, sans-serif;
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  /* Type Scale (Major Third 1.25) */
  --font-size-base: 16px;
  --line-height-base: 1.5;
  --line-height-heading: 1.2;
}

body {
  font-family: var(--font-family-base);
  font-size: var(--font-size-base);
  line-height: var(--line-height-base);
}
```

### Alternatives Considered
- **FontShare/Uncut**: Rejected - less reliable CDN, smaller selection
- **Self-hosted fonts**: Rejected - adds build complexity, CDN is faster globally
- **System fonts only**: Rejected - inconsistent appearance across platforms

### References
- Google Fonts: https://fonts.google.com
- Web Font Best Practices: https://web.dev/font-best-practices/

---

## 11. Image Optimization and WebP Conversion

### Decision
**Use sharp library for build-time image optimization + lazy loading**

### Rationale
- Sharp is the fastest Node.js image processing library
- Automatic WebP conversion with fallback to original format
- Resize and optimize images during build process
- Lazy loading with Intersection Observer API for below-fold images
- Reduces bundle size and improves performance

### Implementation Pattern
```javascript
// build-scripts/optimize-images.js
const sharp = require('sharp');
const fs = require('fs').promises;
const path = require('path');

async function optimizeImage(inputPath, outputDir) {
  const filename = path.basename(inputPath, path.extname(inputPath));

  // Generate WebP version
  await sharp(inputPath)
    .webp({ quality: 85 })
    .toFile(path.join(outputDir, `${filename}.webp`));

  // Generate optimized fallback
  await sharp(inputPath)
    .jpeg({ quality: 85, progressive: true })
    .toFile(path.join(outputDir, `${filename}.jpg`));
}
```

```typescript
// components/OptimizedImage.tsx
interface OptimizedImageProps {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  lazy?: boolean;
}

export function OptimizedImage({ src, alt, width, height, lazy = true }: OptimizedImageProps) {
  const webpSrc = src.replace(/\.(jpg|png)$/, '.webp');

  return (
    <picture>
      <source srcSet={webpSrc} type="image/webp" />
      <img
        src={src}
        alt={alt}
        width={width}
        height={height}
        loading={lazy ? 'lazy' : 'eager'}
      />
    </picture>
  );
}
```

### Alternatives Considered
- **Next.js Image component**: Rejected - not using Next.js framework
- **Cloudinary**: Rejected - adds external dependency, costs for high traffic
- **Manual optimization**: Rejected - time-consuming, inconsistent results

### References
- Sharp: https://sharp.pixelplumbing.com/
- Lazy Loading: https://web.dev/lazy-loading-images/

---

## 12. Brand Color Palette Research Methodology

### Decision
**Structured competitor analysis + color psychology + accessibility validation**

### Rationale
- User explicitly selected research-based approach in clarification session
- Data-driven decisions reduce subjective disagreements
- Ensures accessibility compliance from the start
- Provides rationale for stakeholder buy-in

### Research Process
1. **Competitor Analysis** (3-5 task management apps)
   - Todoist, Asana, ClickUp, Notion, Microsoft To Do
   - Document primary colors, accent colors, neutral palettes
   - Identify common patterns and differentiators

2. **Color Psychology Mapping**
   - Blue: Trust, productivity, calm (common for productivity apps)
   - Green: Growth, completion, positive action
   - Purple: Creativity, premium feel
   - Orange/Red: Urgency, energy (use sparingly)

3. **Palette Generation** (2-3 options)
   - Option A: Blue primary (trust/productivity)
   - Option B: Green primary (growth/completion)
   - Option C: Purple primary (creativity/premium)
   - Each with complementary accent color

4. **Accessibility Validation**
   - Test all combinations with WebAIM Contrast Checker
   - Ensure 4.5:1 ratio for text, 3:1 for interactive elements
   - Test with color blindness simulators

5. **A/B Testing Plan** (post-implementation)
   - Track CTA click-through rates by palette
   - Measure task completion rates
   - Survey user preference (qualitative feedback)

### Deliverable
- Color palette documentation with hex codes, usage guidelines, accessibility scores
- Rationale for each color choice based on research findings
- Implementation as CSS custom properties

### References
- WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/
- Color Psychology: https://www.colorpsychology.org/

---

## Summary of Decisions

| Category | Decision | Rationale |
|----------|----------|-----------|
| **Routing** | React Router v7 | Latest version, middleware-based auth, TypeScript support |
| **Form Validation** | React Hook Form + Zod | Performance, type safety, real-time validation |
| **CSS Architecture** | CSS Modules + Design Tokens | Scoped styles, design system approach, maintainability |
| **Icons** | Heroicons v2 | MIT licensed, high quality, React components |
| **E2E Testing** | Playwright | Modern, TypeScript support, cross-browser, reliable |
| **Backend API** | FastAPI + Pydantic v2 | Type safety, automatic validation, OpenAPI docs |
| **Database ORM** | SQLModel | Type-safe ORM, Pydantic integration, FastAPI compatible |
| **Password Security** | Have I Been Pwned k-anonymity API | Industry standard, secure, free |
| **Email Service** | SendGrid | Simple API, free tier, good DX |
| **Typography** | Google Fonts (Inter) | Free, reliable CDN, modern typeface |
| **Image Optimization** | Sharp + lazy loading | Fast processing, WebP support, performance |
| **Brand Colors** | Research-based methodology | Data-driven, accessibility-first, stakeholder buy-in |

---

## Next Steps

1. **Phase 1: Design & Contracts**
   - Create data-model.md with ContactSubmission schema
   - Generate OpenAPI contract for POST /api/contact
   - Create TypeScript types for frontend
   - Document quickstart guide for local development

2. **Phase 2: Task Breakdown** (via `/sp.tasks`)
   - Generate dependency-ordered tasks
   - Organize by user story priority (P1 → P2 → P3)
   - Include test-first approach for each task

3. **Implementation** (via `/sp.implement`)
   - Follow TDD cycle: Red → Green → Refactor
   - Implement design system foundation first
   - Then auth pages → chat enhancement → landing → contact

---

**Research Complete**: All technical unknowns resolved. Ready to proceed to Phase 1 (Design & Contracts).
