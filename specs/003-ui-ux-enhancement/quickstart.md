# Quickstart Guide: UI/UX Enhancement Development

**Feature**: 003-ui-ux-enhancement
**Date**: 2026-01-31
**Branch**: `003-ui-ux-enhancement`

## Overview

This guide provides step-by-step instructions for setting up the development environment and implementing the UI/UX Enhancement feature.

---

## Prerequisites

- **Node.js**: v18+ (for frontend)
- **Python**: 3.11+ (for backend)
- **PostgreSQL**: 14+ (Neon Serverless or local)
- **Git**: Latest version
- **Code Editor**: VS Code recommended (with extensions: ESLint, Prettier, Python, Pylance)

---

## Initial Setup

### 1. Clone Repository and Switch to Feature Branch

```bash
git clone <repository-url>
cd agentic-todo
git checkout 003-ui-ux-enhancement
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Copy environment template
cp .env.example .env

# Edit .env and configure:
# - DATABASE_URL (Neon PostgreSQL connection string)
# - SENDGRID_API_KEY (for email notifications)
# - JWT_SECRET_KEY (generate with: openssl rand -hex 32)
# - HIBP_API_KEY (optional, for Have I Been Pwned API)
```

### 3. Database Migration

```bash
# Run migrations to create contact_submissions table
alembic upgrade head

# Verify table created
psql $DATABASE_URL -c "\d contact_submissions"
```

### 4. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env.local

# Edit .env.local and configure:
# - VITE_API_BASE_URL=http://localhost:8000
```

### 5. Verify Setup

```bash
# Terminal 1: Start backend
cd backend
source venv/bin/activate
uvicorn src.main:app --reload --port 8000

# Terminal 2: Start frontend
cd frontend
npm run dev

# Terminal 3: Run tests
cd backend
pytest

cd ../frontend
npm test
```

---

## Development Workflow

### Phase 1: Design System Foundation (P1 - MVP)

**Goal**: Create reusable design system components

**Tasks**:
1. Create CSS design tokens (colors, typography, spacing)
2. Implement Button component with variants
3. Implement Input component with validation states
4. Implement Form component with error handling
5. Create Typography components (Heading, Text)
6. Test components for accessibility (WCAG AA)

**Commands**:
```bash
# Create design tokens
touch frontend/src/styles/design-tokens.css
touch frontend/src/styles/typography.css
touch frontend/src/styles/colors.css
touch frontend/src/styles/spacing.css
touch frontend/src/styles/grid.css

# Create component files
mkdir -p frontend/src/components/design-system
touch frontend/src/components/design-system/Button.tsx
touch frontend/src/components/design-system/Input.tsx
touch frontend/src/components/design-system/Form.tsx

# Create test files
mkdir -p frontend/src/components/design-system/__tests__
touch frontend/src/components/design-system/__tests__/Button.test.tsx
touch frontend/src/components/design-system/__tests__/Input.test.tsx
```

**Testing**:
```bash
# Run component tests
npm test -- Button.test.tsx

# Run accessibility tests
npm run test:a11y

# Visual regression tests (optional)
npm run test:visual
```

### Phase 2: Authentication Pages (P1 - MVP)

**Goal**: Implement login and signup pages with validation

**Backend Tasks**:
1. Implement password validation service (Have I Been Pwned)
2. Implement JWT session management (24h/30d)
3. Add password strength validation
4. Write tests for auth endpoints

**Frontend Tasks**:
1. Create Login page with form validation
2. Create Signup page with password strength indicator
3. Implement protected route middleware
4. Add session management (localStorage + refresh tokens)

**Commands**:
```bash
# Backend
touch backend/src/services/password_service.py
touch backend/tests/unit/test_password_service.py

# Frontend
mkdir -p frontend/src/pages
touch frontend/src/pages/Login.tsx
touch frontend/src/pages/Signup.tsx
touch frontend/src/pages/__tests__/Login.test.tsx
touch frontend/src/pages/__tests__/Signup.test.tsx
```

**Testing**:
```bash
# Backend: Test password validation
pytest backend/tests/unit/test_password_service.py -v

# Frontend: Test login flow
npm test -- Login.test.tsx

# E2E: Test full auth flow
npx playwright test tests/e2e/auth-flow.spec.ts
```

### Phase 3: Contact Form Backend (P1 - MVP)

**Goal**: Implement contact form API with email notifications

**Tasks**:
1. Create ContactSubmission SQLModel
2. Implement POST /api/contact endpoint
3. Add email notification service (SendGrid)
4. Implement rate limiting (5 submissions/hour/IP)
5. Write integration tests

**Commands**:
```bash
# Create model and service
touch backend/src/models/contact_submission.py
touch backend/src/services/contact_service.py
touch backend/src/services/email_service.py

# Create API route
touch backend/src/api/routes/contact.py
touch backend/src/api/schemas/contact.py

# Create tests
touch backend/tests/unit/test_contact_service.py
touch backend/tests/integration/test_contact_api.py
```

**Testing**:
```bash
# Unit tests
pytest backend/tests/unit/test_contact_service.py -v

# Integration tests
pytest backend/tests/integration/test_contact_api.py -v

# Test email sending (use SendGrid sandbox)
pytest backend/tests/integration/test_email_service.py -v
```

### Phase 4: Contact Page Frontend (P1 - MVP)

**Goal**: Implement contact page with form validation

**Tasks**:
1. Create Contact page component
2. Implement form with React Hook Form + Zod
3. Add FAQ section
4. Implement success/error states
5. Write E2E tests

**Commands**:
```bash
# Create page and components
touch frontend/src/pages/Contact.tsx
touch frontend/src/pages/__tests__/Contact.test.tsx

# Create E2E test
touch frontend/tests/e2e/contact-form.spec.ts
```

**Testing**:
```bash
# Component tests
npm test -- Contact.test.tsx

# E2E tests
npx playwright test tests/e2e/contact-form.spec.ts

# Test form validation
npx playwright test tests/e2e/contact-form.spec.ts --grep "validation"
```

### Phase 5: Landing Page (P2)

**Goal**: Create marketing landing page with hero section

**Tasks**:
1. Create Landing page component
2. Implement hero section with CTA
3. Add features section
4. Optimize images (WebP conversion)
5. Test performance (Lighthouse)

**Commands**:
```bash
touch frontend/src/pages/Landing.tsx
touch frontend/src/pages/__tests__/Landing.test.tsx
touch frontend/tests/e2e/landing-to-signup.spec.ts
```

**Testing**:
```bash
# Performance testing
npm run lighthouse -- http://localhost:5173/

# E2E user journey
npx playwright test tests/e2e/landing-to-signup.spec.ts
```

### Phase 6: Chat Page Enhancement (P2)

**Goal**: Apply design system to existing chat interface

**Tasks**:
1. Refactor chat components to use design system
2. Add responsive sidebar/drawer
3. Implement empty state
4. Test virtual scrolling performance

**Commands**:
```bash
# Refactor existing components
# (Edit existing files in frontend/src/components/chat/)
```

---

## Testing Strategy

### Unit Tests (90%+ coverage target)

```bash
# Backend
pytest --cov=src --cov-report=html

# Frontend
npm test -- --coverage
```

### Integration Tests

```bash
# Backend API tests
pytest backend/tests/integration/ -v

# Frontend integration tests
npm test -- --testPathPattern=integration
```

### E2E Tests (Playwright)

```bash
# Run all E2E tests
npx playwright test

# Run specific test file
npx playwright test tests/e2e/contact-form.spec.ts

# Run in headed mode (see browser)
npx playwright test --headed

# Debug mode
npx playwright test --debug
```

### Accessibility Tests

```bash
# Run WAVE accessibility audit
npm run test:a11y

# Run axe-core tests
npm test -- --testPathPattern=accessibility

# Manual testing with screen reader
# - macOS: VoiceOver (Cmd+F5)
# - Windows: NVDA (free)
```

### Performance Tests

```bash
# Lighthouse CI
npm run lighthouse:ci

# Manual Lighthouse audit
npm run lighthouse -- http://localhost:5173/

# Check bundle size
npm run build
npm run analyze
```

---

## Common Commands

### Development

```bash
# Start backend dev server
cd backend && uvicorn src.main:app --reload

# Start frontend dev server
cd frontend && npm run dev

# Run type checking
cd backend && mypy src/
cd frontend && npm run type-check

# Run linting
cd backend && ruff check src/
cd frontend && npm run lint

# Format code
cd backend && black src/
cd frontend && npm run format
```

### Database

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Reset database (WARNING: deletes all data)
alembic downgrade base && alembic upgrade head
```

### Git Workflow

```bash
# Create feature branch from 003-ui-ux-enhancement
git checkout -b feature/design-system-components

# Commit with conventional commits
git commit -m "feat(design-system): add Button component with variants"

# Push and create PR
git push origin feature/design-system-components
gh pr create --base 003-ui-ux-enhancement --title "Add design system Button component"
```

---

## Troubleshooting

### Backend Issues

**Issue**: Database connection error
```bash
# Check DATABASE_URL in .env
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"

# Check Neon dashboard for connection string
```

**Issue**: Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version
python --version  # Should be 3.11+
```

### Frontend Issues

**Issue**: Module not found
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Issue**: Type errors
```bash
# Regenerate types from OpenAPI spec
npm run generate:types

# Check TypeScript version
npx tsc --version
```

### Test Issues

**Issue**: Playwright tests failing
```bash
# Install browsers
npx playwright install

# Update Playwright
npm install -D @playwright/test@latest
npx playwright install
```

---

## Environment Variables Reference

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# JWT Authentication
JWT_SECRET_KEY=<generate-with-openssl-rand-hex-32>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS=30

# Email Service (SendGrid)
SENDGRID_API_KEY=<your-sendgrid-api-key>
SENDGRID_FROM_EMAIL=noreply@agentic-todo.com
SENDGRID_SUPPORT_EMAIL=support@agentic-todo.com

# Have I Been Pwned (optional)
HIBP_API_KEY=<optional-api-key>

# Rate Limiting
RATE_LIMIT_CONTACT_FORM=5  # submissions per hour per IP
```

### Frontend (.env.local)

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000

# Feature Flags (optional)
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_ERROR_TRACKING=false
```

---

## Resources

- **Design System**: See `specs/003-ui-ux-enhancement/research.md`
- **API Contracts**: See `specs/003-ui-ux-enhancement/contracts/contact-api.yaml`
- **Data Models**: See `specs/003-ui-ux-enhancement/data-model.md`
- **Tasks**: See `specs/003-ui-ux-enhancement/tasks.md` (generated by `/sp.tasks`)

---

## Next Steps

1. Review this quickstart guide
2. Set up development environment
3. Run `/sp.tasks` to generate detailed task breakdown
4. Start implementation with Phase 1 (Design System Foundation)
5. Follow TDD workflow: Red → Green → Refactor

**Ready to start? Run `/sp.tasks` to generate the task list!**
