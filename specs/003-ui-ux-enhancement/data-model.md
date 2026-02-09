# Data Model: UI/UX Enhancement

**Feature**: 003-ui-ux-enhancement
**Date**: 2026-01-31
**Status**: Complete

## Overview

This document defines all data entities, their fields, relationships, validation rules, and state transitions for the UI/UX Enhancement feature.

---

## Entities

### 1. ContactSubmission (NEW)

**Purpose**: Store contact form submissions with status tracking for support workflow management.

**Table Name**: `contact_submissions`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| `name` | String(100) | NOT NULL | Submitter's name |
| `email` | String(255) | NOT NULL, INDEX | Submitter's email address |
| `subject` | String(200) | NOT NULL | Submission category/subject |
| `message` | Text(5000) | NOT NULL | Message content |
| `status` | Enum | NOT NULL, INDEX, DEFAULT='new' | Workflow status: 'new', 'in-progress', 'resolved', 'closed' |
| `assigned_to` | String(255) | NULLABLE | Email/ID of support team member assigned |
| `response_sent` | Boolean | NOT NULL, DEFAULT=false | Whether response has been sent to submitter |
| `created_at` | Timestamp | NOT NULL, DEFAULT=CURRENT_TIMESTAMP | Submission timestamp |
| `updated_at` | Timestamp | NOT NULL, DEFAULT=CURRENT_TIMESTAMP ON UPDATE | Last update timestamp |
| `ip_address` | String(45) | NULLABLE | Submitter's IP address (IPv4/IPv6) |
| `user_agent` | String(500) | NULLABLE | Submitter's browser user agent |

**Indexes**:
- PRIMARY KEY: `id`
- INDEX: `email` (for querying submissions by user)
- INDEX: `status` (for filtering by workflow status)
- INDEX: `created_at` (for sorting by submission date)

**Validation Rules**:
- `name`: 1-100 characters, no special validation
- `email`: Valid email format (RFC 5322), max 255 characters
- `subject`: 1-200 characters, must be one of predefined categories or custom text
- `message`: 10-5000 characters (minimum ensures meaningful submissions)
- `status`: Must be one of: 'new', 'in-progress', 'resolved', 'closed'
- `ip_address`: Valid IPv4 or IPv6 format if provided
- `user_agent`: Max 500 characters if provided

**State Transitions**:
```
new → in-progress → resolved → closed
  ↓         ↓           ↓
  └─────────┴───────────┴─→ closed (can close from any state)
```

**Business Rules**:
- New submissions always start with `status='new'`
- `assigned_to` can be set when status changes to 'in-progress'
- `response_sent` should be set to true when support team sends response
- `updated_at` automatically updates on any field change
- Submissions cannot be deleted (soft delete via status='closed' if needed)

**SQLModel Definition**:
```python
from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime
from enum import Enum

class SubmissionStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in-progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class ContactSubmissionBase(SQLModel):
    """Base model with shared fields for create/update operations."""
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(max_length=255, regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    subject: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=10, max_length=5000)

class ContactSubmission(ContactSubmissionBase, table=True):
    """Database table model."""
    __tablename__ = "contact_submissions"

    id: Optional[int] = Field(default=None, primary_key=True)
    status: SubmissionStatus = Field(default=SubmissionStatus.NEW, index=True)
    assigned_to: Optional[str] = Field(default=None, max_length=255)
    response_sent: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)

class ContactSubmissionCreate(ContactSubmissionBase):
    """Schema for creating new submissions (API request)."""
    pass

class ContactSubmissionPublic(ContactSubmissionBase):
    """Schema for public API responses."""
    id: int
    status: SubmissionStatus
    created_at: datetime

class ContactSubmissionUpdate(SQLModel):
    """Schema for updating existing submissions (admin only)."""
    status: Optional[SubmissionStatus] = None
    assigned_to: Optional[str] = None
    response_sent: Optional[bool] = None
```

**Relationships**: None (standalone entity)

---

### 2. User (EXISTING - Enhanced)

**Purpose**: User authentication and session management.

**Enhancements for this feature**:
- Session management with JWT tokens (24h default, 30d with "Remember Me")
- Password validation against Have I Been Pwned API
- Password requirements: min 8 chars, 3 of 4 character types

**No schema changes required** - enhancements are in authentication service layer.

**New Validation Rules** (enforced in service layer):
- Password must be minimum 8 characters
- Password must contain at least 3 of 4 character types:
  - Uppercase letters (A-Z)
  - Lowercase letters (a-z)
  - Numbers (0-9)
  - Special characters (!@#$%^&*()_+-=[]{}|;:,.<>?)
- Password must not appear in Have I Been Pwned database
- Email must be valid format and unique

---

### 3. Task (EXISTING - No Changes)

**Purpose**: Task management via chat interface.

**No changes required for this feature** - UI/UX enhancements only affect presentation layer.

---

## Database Migration

### Migration: Add contact_submissions table

**Up Migration**:
```sql
CREATE TABLE contact_submissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    subject VARCHAR(200) NOT NULL,
    message TEXT NOT NULL CHECK (LENGTH(message) >= 10 AND LENGTH(message) <= 5000),
    status VARCHAR(20) NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'in-progress', 'resolved', 'closed')),
    assigned_to VARCHAR(255),
    response_sent BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500)
);

CREATE INDEX idx_contact_submissions_email ON contact_submissions(email);
CREATE INDEX idx_contact_submissions_status ON contact_submissions(status);
CREATE INDEX idx_contact_submissions_created_at ON contact_submissions(created_at);

-- Trigger to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_contact_submissions_updated_at
    BEFORE UPDATE ON contact_submissions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

**Down Migration**:
```sql
DROP TRIGGER IF EXISTS update_contact_submissions_updated_at ON contact_submissions;
DROP FUNCTION IF EXISTS update_updated_at_column();
DROP TABLE IF EXISTS contact_submissions;
```

---

## TypeScript Types (Frontend)

```typescript
// types/contact.ts

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

export interface ContactSubmissionPublic {
  id: number;
  name: string;
  email: string;
  subject: string;
  message: string;
  status: SubmissionStatus;
  created_at: string; // ISO 8601 format
}

export interface ContactSubmissionResponse {
  id: number;
  name: string;
  email: string;
  subject: string;
  message: string;
  status: SubmissionStatus;
  created_at: string;
}

// Validation schemas (using Zod)
import { z } from 'zod';

export const contactSubmissionSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100, 'Name too long'),
  email: z.string().email('Invalid email address').max(255, 'Email too long'),
  subject: z.string().min(1, 'Subject is required').max(200, 'Subject too long'),
  message: z.string()
    .min(10, 'Message must be at least 10 characters')
    .max(5000, 'Message too long (max 5000 characters)')
});

export type ContactSubmissionFormData = z.infer<typeof contactSubmissionSchema>;
```

---

## Design System Entities (Frontend)

### Typography Scale

```typescript
// types/design-system.ts

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

export interface ColorPalette {
  neutral: {
    50: string;   // #fafafa (backgrounds)
    100: string;
    200: string;
    300: string;
    400: string;
    500: string;
    600: string;
    700: string;
    800: string;
    900: string;  // #1a1a1a (text)
  };
  primary: {
    50: string;
    500: string;  // Main brand color (TBD from research)
    700: string;
  };
  accent: {
    50: string;
    500: string;  // CTA color (TBD from research)
    700: string;
  };
}
```

---

## Summary

**New Entities**: 1 (ContactSubmission)
**Enhanced Entities**: 1 (User - validation rules only)
**Unchanged Entities**: 1 (Task)

**Database Changes**:
- Add `contact_submissions` table with 12 fields
- Add 3 indexes for query performance
- Add trigger for auto-updating `updated_at` timestamp

**Type Safety**:
- SQLModel for backend (Python type hints + Pydantic validation)
- TypeScript interfaces for frontend
- Zod schemas for runtime validation

**Next Steps**: Generate API contracts in `/contracts/` directory.
