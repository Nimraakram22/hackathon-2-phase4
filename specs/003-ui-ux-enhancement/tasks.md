# Tasks: UI/UX Enhancement for Todo Chatbot

**Feature**: 003-ui-ux-enhancement
**Branch**: `003-ui-ux-enhancement`
**Date**: 2026-01-31
**Status**: Ready for Implementation

## Overview

This document contains all implementation tasks for the UI/UX Enhancement feature, organized by user story priority. Each task follows the TDD (Test-Driven Development) approach where applicable.

**Total Tasks**: 87
**MVP Scope**: User Stories 1-3 (P1) = 52 tasks
**Estimated Parallel Opportunities**: 35+ tasks can run in parallel

---

## Task Format

Each task follows this format:
```
- [ ] [TaskID] [P?] [Story?] Description with file path
```

- **TaskID**: Sequential number (T001, T002, etc.)
- **[P]**: Parallelizable (can run simultaneously with other [P] tasks)
- **[Story]**: User story label (US1, US2, etc.) - only for user story phases
- **Description**: Clear action with exact file path

---

## Phase 1: Setup & Infrastructure (8 tasks)

**Goal**: Initialize project structure and install dependencies

- [X] T001 Install frontend dependencies: React Router v7, React Hook Form, Zod, Heroicons, TypeScript types in frontend/package.json
- [X] T002 Install backend dependencies: SQLModel, SendGrid, httpx (for Have I Been Pwned API) in backend/requirements.txt
- [X] T003 [P] Create frontend directory structure: frontend/src/components/design-system/, frontend/src/pages/, frontend/src/styles/, frontend/src/services/
- [X] T004 [P] Create backend directory structure: backend/src/models/, backend/src/services/, backend/src/api/routes/, backend/src/api/schemas/
- [X] T005 [P] Create test directory structure: frontend/tests/e2e/, frontend/tests/accessibility/, backend/tests/unit/, backend/tests/integration/
- [X] T006 Configure TypeScript strict mode in frontend/tsconfig.json
- [X] T007 Configure Playwright for E2E testing in frontend/playwright.config.ts
- [X] T008 Set up environment variables template in backend/.env.example and frontend/.env.example

---

## Phase 2: Foundational Tasks (12 tasks)

**Goal**: Create blocking prerequisites needed by all user stories

### Database Migration

- [X] T009 Create Alembic migration for contact_submissions table in backend/alembic/versions/xxx_add_contact_submissions.py
- [X] T010 Run migration and verify table created with correct schema (12 fields, 3 indexes, trigger)

### Design Tokens (Foundation for US1, US2, US4, US5)

- [X] T011 [P] Create CSS design tokens file with color variables (neutrals, primary, accent) in frontend/src/styles/design-tokens.css
- [X] T012 [P] Create typography scale CSS file (Major Third 1.25 ratio, 16px base) in frontend/src/styles/typography.css
- [X] T013 [P] Create spacing system CSS file (8-point grid: 8px, 16px, 24px, 32px, 48px, 64px, 96px) in frontend/src/styles/spacing.css
- [X] T014 [P] Create grid system CSS file (12/8/4 columns for desktop/tablet/mobile) in frontend/src/styles/grid.css
- [X] T015 Import all design token CSS files in frontend/src/index.css

### Authentication Middleware (Foundation for US3)

- [X] T016 Implement React Router v7 authentication middleware in frontend/src/middleware/auth.ts
- [X] T017 Create protected route wrapper component in frontend/src/components/ProtectedRoute.tsx
- [X] T018 Configure React Router with middleware in frontend/src/App.tsx

### Backend Services (Foundation for Contact Form)

- [X] T019 [P] Implement password validation service with Have I Been Pwned k-anonymity API in backend/src/services/password_service.py
- [X] T020 [P] Implement email notification service with SendGrid in backend/src/services/email_service.py

---

## Phase 3: User Story 1 - Visual Hierarchy and Scannability (P1 MVP) (10 tasks)

**Goal**: Users can quickly scan and understand the interface within 3 seconds

**Independent Test**: Show interface to new user for 3 seconds, ask: (1) What is this application? (2) What can you do here? (3) What should you do first? Success = 90%+ correct answers.

### Design System Components

- [X] T021 [P] [US1] Create Button component with primary/secondary/ghost variants in frontend/src/components/design-system/Button.tsx
- [X] T022 [P] [US1] Create Button component tests (variants, accessibility, keyboard navigation) in frontend/src/components/design-system/__tests__/Button.test.tsx
- [X] T023 [P] [US1] Create Card component with optional title in frontend/src/components/design-system/Card.tsx
- [X] T024 [P] [US1] Create Card component tests in frontend/src/components/design-system/__tests__/Card.test.tsx
- [X] T025 [P] [US1] Create Heading component (h1-h6) with consistent sizing in frontend/src/components/design-system/Heading.tsx
- [X] T026 [P] [US1] Create Text component with size variants in frontend/src/components/design-system/Text.tsx

### Layout Components

- [X] T027 [US1] Create Navigation component with logo and CTA button in frontend/src/components/layout/Navigation.tsx
- [X] T028 [US1] Create Navigation component tests (responsive, accessibility) in frontend/src/components/layout/__tests__/Navigation.test.tsx
- [X] T029 [US1] Create Hero section component with headline, subheadline, CTA in frontend/src/components/landing/HeroSection.tsx
- [X] T030 [US1] Create Features section component with icon grid in frontend/src/components/landing/FeaturesSection.tsx

---

## Phase 4: User Story 2 - Typography System and Readability (P1 MVP) (8 tasks)

**Goal**: Users can read all text comfortably without eye strain

**Independent Test**: Users read task descriptions, chat messages, and interface text for 10+ minutes without reporting eye strain. Font sizes scale consistently across all screen sizes.

### Typography Implementation

- [X] T031 [P] [US2] Load Google Fonts (Inter) with preconnect optimization in frontend/public/index.html
- [X] T032 [P] [US2] Apply typography scale to all heading components (h1: 39px, h2: 31px, h3: 25px, h4: 20px, h5: 16px) in frontend/src/styles/typography.css
- [X] T033 [P] [US2] Set body text to 16px with 150% line height in frontend/src/styles/typography.css
- [X] T034 [P] [US2] Set heading line height to 120% in frontend/src/styles/typography.css
- [X] T035 [P] [US2] Apply dark gray text (#1a1a1a) on off-white backgrounds (#fafafa) in frontend/src/styles/design-tokens.css
- [X] T036 [US2] Create Typography showcase page for testing all text styles in frontend/src/pages/TypographyShowcase.tsx
- [X] T037 [US2] Test typography readability on mobile (320px), tablet (768px), desktop (1280px+) viewports
- [X] T038 [US2] Run accessibility audit for text contrast ratios (WCAG AA: 4.5:1 minimum)

---

## Phase 5: User Story 3 - Conversion-Optimized User Journey (P1 MVP) (16 tasks)

**Goal**: Users complete primary goal (creating tasks via chat) with minimal friction

**Independent Test**: Track task completion rate - 90%+ of users who start creating a task complete it on first attempt. Time from landing to first task < 60 seconds.

### Authentication Pages

- [X] T039 [P] [US3] Create Input component with label, error state, validation in frontend/src/components/design-system/Input.tsx
- [X] T040 [P] [US3] Create Input component tests (validation, accessibility, error states) in frontend/src/components/design-system/__tests__/Input.test.tsx
- [X] T041 [P] [US3] Create Form component wrapper with error handling in frontend/src/components/design-system/Form.tsx
- [X] T042 [US3] Create Signup page with email, password, confirm password fields in frontend/src/pages/Signup.tsx
- [X] T043 [US3] Implement password strength indicator (weak/medium/strong) in Signup page frontend/src/pages/Signup.tsx
- [X] T044 [US3] Integrate React Hook Form + Zod validation in Signup page frontend/src/pages/Signup.tsx
- [X] T045 [US3] Add Have I Been Pwned password check on signup in frontend/src/pages/Signup.tsx
- [X] T046 [US3] Create Login page with email, password, "Remember Me" checkbox in frontend/src/pages/Login.tsx
- [X] T047 [US3] Implement session management (24h default, 30d with Remember Me) in frontend/src/services/auth.ts
- [X] T048 [US3] Add "Already have account? Sign In" link to Signup page in frontend/src/pages/Signup.tsx
- [X] T049 [US3] Add "Don't have account? Sign Up" link to Login page in frontend/src/pages/Login.tsx
- [X] T050 [US3] Create Signup page tests (form validation, password strength, error messages) in frontend/src/pages/__tests__/Signup.test.tsx
- [X] T051 [US3] Create Login page tests (form validation, Remember Me, error messages) in frontend/src/pages/__tests__/Login.test.tsx

### Landing Page

- [X] T052 [US3] Create Landing page with hero section and primary CTA in frontend/src/pages/Landing.tsx
- [X] T053 [US3] Add features section with 3-4 key benefits to Landing page in frontend/src/pages/Landing.tsx
- [X] T054 [US3] Create E2E test for landing-to-signup user journey in frontend/tests/e2e/landing-to-signup.spec.ts

---

## Phase 6: User Story 4 - Color System and Accessibility (P2) (9 tasks)

**Goal**: Users with visual impairments can use the application effectively (WCAG AA compliance)

**Independent Test**: Run automated accessibility audit (WAVE, Lighthouse) - all contrast ratios pass WCAG AA (4.5:1 for text, 3:1 for interactive). Users with color blindness complete all tasks.

### Brand Color Research & Implementation

- [X] T055 [P] [US4] Research competitor color palettes (Todoist, Asana, ClickUp, Notion, Microsoft To Do) and document findings
- [X] T056 [P] [US4] Create 2-3 color palette options following 60-30-10 rule in design documentation
- [X] T057 [US4] Validate all palette options with WebAIM Contrast Checker (4.5:1 for text, 3:1 for interactive)
- [X] T058 [US4] Test palette options with color blindness simulators (protanopia, deuteranopia, tritanopia)
- [X] T059 [US4] Select final color palette and update CSS design tokens in frontend/src/styles/design-tokens.css
- [X] T060 [US4] Apply color palette to all components (Button, Input, Card, Navigation)
- [X] T061 [US4] Add ARIA labels to all interactive elements in all components
- [X] T062 [US4] Implement keyboard navigation for all interactive elements
- [X] T063 [US4] Run WAVE and Lighthouse accessibility audits on all pages (target: 95+ score)
- [ ] T063 [US4] Run WAVE and Lighthouse accessibility audits on all pages (target: 95+ score)

---

## Phase 7: User Story 5 - Responsive Layout and Spacing (P2) (8 tasks)

**Goal**: Consistent experience on any device (mobile, tablet, desktop)

**Independent Test**: Test on mobile (320px), tablet (768px), desktop (1280px+). All content readable, CTAs tappable (min 48px), spacing consistent using 8-point grid.

### Responsive Implementation

- [X] T064 [P] [US5] Apply 8-point spacing system to all components using CSS variables
- [X] T065 [P] [US5] Implement 12/8/4 column grid system for desktop/tablet/mobile in frontend/src/styles/grid.css
- [X] T066 [P] [US5] Ensure all touch targets are minimum 48x48 pixels on mobile
- [X] T067 [US5] Test Landing page responsive behavior (320px, 768px, 1280px+)
- [X] T068 [US5] Test Signup/Login pages responsive behavior (320px, 768px, 1280px+)
- [X] T069 [US5] Test Chat page responsive behavior with collapsible sidebar/drawer
- [X] T070 [US5] Test Contact page responsive behavior (320px, 768px, 1280px+)
- [X] T071 [US5] Run Google Mobile-Friendly Test on all pages (target: 95+ score)

---

## Phase 8: User Story 6 - Performance and Loading Experience (P3) (7 tasks)

**Goal**: Fast page loads and smooth interactions

**Independent Test**: Run Lighthouse performance audit - FCP < 1.8s, LCP < 2.5s, TBT < 300ms. Users report interface feels "instant."

### Performance Optimization

- [ ] T072 [P] [US6] Implement lazy loading for images below the fold in all pages
- [ ] T073 [P] [US6] Convert all images to WebP format using Sharp library
- [ ] T074 [P] [US6] Optimize hero image for Landing page (resize, compress, WebP)
- [ ] T075 [US6] Implement code splitting for routes in frontend/src/App.tsx
- [ ] T076 [US6] Run Lighthouse performance audit on Landing page (target: FCP < 1.8s, LCP < 2.5s, TBT < 300ms)
- [ ] T077 [US6] Run Lighthouse performance audit on Chat page (target: 90+ performance score)
- [ ] T078 [US6] Implement virtual scrolling for chat messages (100+ messages) in frontend/src/components/chat/ChatInterface.tsx

---

## Phase 9: User Story 7 - Form Simplification and Input Design (P3) (9 tasks)

**Goal**: Users complete forms with minimal effort and clear validation

**Independent Test**: Measure form completion rate - 95%+ of users who start a form complete it. Track form abandonment points.

### Contact Form Backend

- [X] T079 [P] [US7] Create ContactSubmission SQLModel in backend/src/models/contact_submission.py
- [X] T080 [P] [US7] Create ContactSubmission Pydantic schemas (Create, Public, Update) in backend/src/api/schemas/contact.py
- [X] T081 [P] [US7] Implement ContactService with create, list, update methods in backend/src/services/contact_service.py
- [X] T082 [US7] Implement POST /api/contact endpoint with rate limiting (5/hour/IP) in backend/src/api/routes/contact.py
- [X] T083 [US7] Implement GET /api/contact endpoint (admin only) in backend/src/api/routes/contact.py
- [X] T084 [US7] Implement PATCH /api/contact/:id endpoint (admin only) in backend/src/api/routes/contact.py
- [ ] T085 [US7] Write unit tests for ContactService in backend/tests/unit/test_contact_service.py
- [ ] T086 [US7] Write integration tests for contact API endpoints in backend/tests/integration/test_contact_api.py

### Contact Form Frontend

- [X] T087 [US7] Create Contact page with form (name, email, subject dropdown, message) in frontend/src/pages/Contact.tsx
- [X] T088 [US7] Add FAQ section to Contact page (5-7 common questions) in frontend/src/pages/Contact.tsx
- [X] T089 [US7] Implement real-time form validation with React Hook Form + Zod in frontend/src/pages/Contact.tsx
- [X] T090 [US7] Add success confirmation with submission ID after form submit in frontend/src/pages/Contact.tsx
- [ ] T091 [US7] Create Contact page tests (form validation, submission, error handling) in frontend/src/pages/__tests__/Contact.test.tsx
- [ ] T092 [US7] Create E2E test for contact form submission in frontend/tests/e2e/contact-form.spec.ts

---

## Phase 10: Chat Page Enhancement (Cross-Story) (8 tasks)

**Goal**: Apply design system to existing chat interface

**Applies to**: US1 (hierarchy), US2 (typography), US3 (conversion), US5 (responsive)

- [X] T093 [P] Refactor ChatInterface to use design system Button component in frontend/src/components/chat/ChatInterface.tsx
- [X] T094 [P] Refactor ChatInterface to use design system Input component in frontend/src/components/chat/ChatInterface.tsx
- [X] T095 [P] Apply typography scale to chat messages and task titles in frontend/src/components/chat/ChatInterface.tsx
- [X] T096 Apply 8-point spacing system to chat layout in frontend/src/components/chat/ChatInterface.tsx
- [X] T097 Implement collapsible sidebar for desktop in frontend/src/components/chat/Sidebar.tsx
- [X] T098 Implement drawer for mobile (swipe or button to open) in frontend/src/components/chat/Drawer.tsx
- [X] T099 Add empty state with onboarding message in frontend/src/components/chat/EmptyState.tsx
- [X] T100 Add loading indicator for agent processing in frontend/src/components/chat/LoadingIndicator.tsx

---

## Phase 11: Polish & Cross-Cutting Concerns (7 tasks)

**Goal**: Final touches and quality assurance

- [X] T101 [P] Create 404 Not Found page in frontend/src/pages/NotFound.tsx
- [X] T102 [P] Create Loading spinner component in frontend/src/components/design-system/Spinner.tsx
- [X] T103 [P] Add error boundary component for graceful error handling in frontend/src/components/ErrorBoundary.tsx
- [ ] T104 Run full E2E test suite (landing-to-signup, login-flow, contact-form, chat-interaction)
- [ ] T105 Run full accessibility audit suite (WAVE, Lighthouse, axe-core) on all pages
- [ ] T106 Run type checking (mypy for backend, tsc for frontend) and fix all errors
- [X] T107 Update CLAUDE.md with final implementation notes and lessons learned

---

## Dependencies & Execution Order

### User Story Completion Order

```
Phase 1 (Setup) → Phase 2 (Foundational)
                      ↓
    ┌─────────────────┴─────────────────┐
    ↓                                   ↓
Phase 3 (US1)                    Phase 4 (US2)
    ↓                                   ↓
    └─────────────────┬─────────────────┘
                      ↓
                 Phase 5 (US3) ← MVP COMPLETE
                      ↓
    ┌─────────────────┴─────────────────┐
    ↓                                   ↓
Phase 6 (US4)                    Phase 7 (US5)
    ↓                                   ↓
    └─────────────────┬─────────────────┘
                      ↓
    ┌─────────────────┴─────────────────┐
    ↓                                   ↓
Phase 8 (US6)                    Phase 9 (US7)
    ↓                                   ↓
    └─────────────────┬─────────────────┘
                      ↓
              Phase 10 (Chat Enhancement)
                      ↓
              Phase 11 (Polish)
```

### Critical Path (Blocking Dependencies)

1. **Setup (Phase 1)** → MUST complete before any other phase
2. **Foundational (Phase 2)** → MUST complete before user story phases
3. **US1 + US2** → MUST complete before US3 (design system needed for forms)
4. **US3** → MUST complete before US4-US7 (auth pages needed for testing)
5. **US4 + US5** → MUST complete before US6 (colors and layout needed for performance testing)
6. **US1-US7** → MUST complete before Chat Enhancement (Phase 10)
7. **All phases** → MUST complete before Polish (Phase 11)

### Parallel Execution Opportunities

**Within Phase 2 (Foundational)**: Tasks T011-T014 (design tokens) can run in parallel

**Within Phase 3 (US1)**: Tasks T021-T026 (design system components) can run in parallel

**Within Phase 4 (US2)**: Tasks T031-T035 (typography implementation) can run in parallel

**Within Phase 5 (US3)**: Tasks T039-T041 (form components) can run in parallel

**Within Phase 6 (US4)**: Tasks T055-T056 (color research) can run in parallel

**Within Phase 7 (US5)**: Tasks T064-T066 (responsive implementation) can run in parallel

**Within Phase 8 (US6)**: Tasks T072-T074 (performance optimization) can run in parallel

**Within Phase 9 (US7)**: Tasks T079-T081 (backend models/services) can run in parallel

**Within Phase 10 (Chat)**: Tasks T093-T095 (component refactoring) can run in parallel

**Within Phase 11 (Polish)**: Tasks T101-T103 (utility components) can run in parallel

---

## MVP Scope (Minimum Viable Product)

**MVP = User Stories 1-3 (P1) = Phases 1-5 = 52 tasks**

**MVP Deliverables**:
- ✅ Design system foundation (typography, spacing, colors, grid)
- ✅ Reusable components (Button, Input, Form, Card, Heading, Text, Navigation)
- ✅ Landing page with hero section and features
- ✅ Authentication pages (Login, Signup) with password validation
- ✅ Session management (JWT with refresh tokens)
- ✅ Protected routes with middleware
- ✅ Visual hierarchy and scannability (US1)
- ✅ Typography system and readability (US2)
- ✅ Conversion-optimized user journey (US3)

**Post-MVP** (P2 + P3):
- Color system and accessibility (US4)
- Responsive layout and spacing (US5)
- Performance and loading experience (US6)
- Form simplification and contact form (US7)
- Chat page enhancement
- Polish and cross-cutting concerns

---

## Implementation Strategy

### Week 1: MVP Foundation (Phases 1-2)
- Day 1-2: Setup and infrastructure (T001-T008)
- Day 3-5: Foundational tasks (T009-T020)

### Week 2: MVP Core (Phases 3-4)
- Day 1-3: User Story 1 - Visual Hierarchy (T021-T030)
- Day 4-5: User Story 2 - Typography (T031-T038)

### Week 3: MVP Completion (Phase 5)
- Day 1-5: User Story 3 - Conversion Journey (T039-T054)
- **MVP COMPLETE** - Deploy and gather user feedback

### Week 4: Post-MVP Enhancement (Phases 6-7)
- Day 1-3: User Story 4 - Accessibility (T055-T063)
- Day 4-5: User Story 5 - Responsive (T064-T071)

### Week 5: Post-MVP Optimization (Phases 8-9)
- Day 1-2: User Story 6 - Performance (T072-T078)
- Day 3-5: User Story 7 - Contact Form (T079-T092)

### Week 6: Final Integration (Phases 10-11)
- Day 1-3: Chat Enhancement (T093-T100)
- Day 4-5: Polish and QA (T101-T107)

---

## Testing Strategy

### Unit Tests (90%+ coverage target)
- Backend: pytest with coverage reporting
- Frontend: Jest + React Testing Library
- Run after each component/service implementation

### Integration Tests
- Backend API tests: pytest
- Frontend integration tests: Jest
- Run after each API endpoint implementation

### E2E Tests (Playwright)
- landing-to-signup.spec.ts (T054)
- login-flow.spec.ts (implied in T051)
- contact-form.spec.ts (T092)
- chat-interaction.spec.ts (implied in T100)
- Run after each page implementation

### Accessibility Tests
- WAVE extension: Manual audit
- Lighthouse Accessibility: Automated (target: 95+)
- axe-core: Automated
- Run after each page implementation (T038, T063, T105)

### Performance Tests
- Lighthouse Performance: Automated (target: 90+)
- FCP < 1.8s, LCP < 2.5s, TBT < 300ms
- Run after optimization tasks (T076, T077)

---

## Success Criteria

**MVP Success** (After Phase 5):
- [ ] All P1 user stories (US1-US3) acceptance scenarios pass
- [ ] Landing page loads in < 1.8s (FCP)
- [ ] 90%+ of test users can identify app purpose within 3 seconds
- [ ] 95%+ form completion rate for signup/login
- [ ] All components pass accessibility audit (WCAG AA)
- [ ] Type checking passes (mypy + tsc)
- [ ] 90%+ test coverage for critical paths

**Full Feature Success** (After Phase 11):
- [ ] All user stories (US1-US7) acceptance scenarios pass
- [ ] All pages pass Lighthouse audits (90+ performance, 95+ accessibility)
- [ ] Contact form backend API functional with email notifications
- [ ] Chat page enhanced with design system
- [ ] All E2E tests passing
- [ ] Zero accessibility violations (WAVE, axe-core)
- [ ] Mobile-friendly score 95+ on all pages

---

## Notes

- **TDD Approach**: Write tests before implementation for all components and services
- **Incremental Delivery**: Deploy MVP (Phases 1-5) first, then iterate with user feedback
- **Parallel Execution**: Leverage [P] tasks to speed up development
- **Type Safety**: Maintain strict TypeScript and Python type checking throughout
- **Documentation**: Update CLAUDE.md with implementation notes and lessons learned

**Ready to start? Begin with Phase 1: Setup & Infrastructure (T001-T008)**
