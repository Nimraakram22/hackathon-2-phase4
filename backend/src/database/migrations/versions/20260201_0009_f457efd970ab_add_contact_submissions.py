"""add_contact_submissions

Revision ID: f457efd970ab
Revises: 001
Create Date: 2026-02-01 00:09:08.303811

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f457efd970ab'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create contact_submissions table
    op.execute("""
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
    """)

    # Create indexes
    op.execute("CREATE INDEX idx_contact_submissions_email ON contact_submissions(email);")
    op.execute("CREATE INDEX idx_contact_submissions_status ON contact_submissions(status);")
    op.execute("CREATE INDEX idx_contact_submissions_created_at ON contact_submissions(created_at);")

    # Create trigger function for auto-updating updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    # Create trigger
    op.execute("""
        CREATE TRIGGER update_contact_submissions_updated_at
            BEFORE UPDATE ON contact_submissions
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Drop trigger
    op.execute("DROP TRIGGER IF EXISTS update_contact_submissions_updated_at ON contact_submissions;")

    # Drop trigger function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")

    # Drop table (indexes are dropped automatically)
    op.execute("DROP TABLE IF EXISTS contact_submissions;")
