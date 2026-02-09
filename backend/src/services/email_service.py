"""
Email notification service using SendGrid
Sends email notifications for contact form submissions
"""

import os
from typing import Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content


class EmailService:
    """Email notification service using SendGrid"""

    def __init__(self):
        self.api_key = os.environ.get('SENDGRID_API_KEY')
        self.from_email = os.environ.get('SENDGRID_FROM_EMAIL', 'noreply@agentic-todo.com')
        self.support_email = os.environ.get('SENDGRID_SUPPORT_EMAIL', 'support@agentic-todo.com')

        if not self.api_key:
            raise ValueError("SENDGRID_API_KEY environment variable is required")

        self.client = SendGridAPIClient(self.api_key)

    async def send_contact_notification(
        self,
        submission_id: int,
        name: str,
        email: str,
        subject: str,
        message: str,
        created_at: str
    ) -> bool:
        """
        Send email notification when contact form is submitted.

        Args:
            submission_id: Contact submission ID
            name: Submitter's name
            email: Submitter's email
            subject: Submission subject/category
            message: Submission message
            created_at: Submission timestamp

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            mail = Mail(
                from_email=Email(self.from_email),
                to_emails=To(self.support_email),
                subject=f'New Contact Form Submission: {subject}',
                html_content=Content(
                    "text/html",
                    f'''
                    <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <h2 style="color: #1a1a1a;">New Contact Form Submission</h2>

                        <div style="background-color: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <p><strong>Submission ID:</strong> #{submission_id}</p>
                            <p><strong>Name:</strong> {name}</p>
                            <p><strong>Email:</strong> <a href="mailto:{email}">{email}</a></p>
                            <p><strong>Subject:</strong> {subject}</p>
                            <p><strong>Submitted:</strong> {created_at}</p>
                        </div>

                        <div style="margin: 20px 0;">
                            <h3 style="color: #1a1a1a;">Message:</h3>
                            <p style="white-space: pre-wrap;">{message}</p>
                        </div>

                        <hr style="border: none; border-top: 1px solid #e5e5e5; margin: 30px 0;">

                        <p style="font-size: 14px; color: #737373;">
                            This is an automated notification from the Agentic Todo contact form.
                        </p>
                    </body>
                    </html>
                    '''
                )
            )

            response = self.client.send(mail)
            return response.status_code == 202

        except Exception as e:
            # Log error but don't fail the submission
            print(f"Error sending email notification: {e}")
            return False

    async def send_confirmation_email(
        self,
        to_email: str,
        name: str,
        submission_id: int
    ) -> bool:
        """
        Send confirmation email to user who submitted contact form.

        Args:
            to_email: User's email address
            name: User's name
            submission_id: Contact submission ID

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            mail = Mail(
                from_email=Email(self.from_email),
                to_emails=To(to_email),
                subject='We received your message - Agentic Todo',
                html_content=Content(
                    "text/html",
                    f'''
                    <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <h2 style="color: #1a1a1a;">Thank you for contacting us!</h2>

                        <p>Hi {name},</p>

                        <p>We've received your message and will respond within 24 hours.</p>

                        <div style="background-color: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <p><strong>Your submission ID:</strong> #{submission_id}</p>
                            <p style="font-size: 14px; color: #737373;">
                                Please reference this ID if you need to follow up on your request.
                            </p>
                        </div>

                        <p>Best regards,<br>The Agentic Todo Team</p>

                        <hr style="border: none; border-top: 1px solid #e5e5e5; margin: 30px 0;">

                        <p style="font-size: 14px; color: #737373;">
                            This is an automated confirmation email. Please do not reply to this message.
                        </p>
                    </body>
                    </html>
                    '''
                )
            )

            response = self.client.send(mail)
            return response.status_code == 202

        except Exception as e:
            # Log error but don't fail the submission
            print(f"Error sending confirmation email: {e}")
            return False


# Singleton instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get or create EmailService singleton instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
