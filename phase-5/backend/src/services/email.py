"""
Email service using Resend for sending transactional emails.
Handles password reset emails and other notifications.
"""
import resend
from core.config import settings


class EmailService:
    """Service class for sending emails via Resend."""

    def __init__(self):
        """Initialize the email service with Resend API key."""
        self.api_key = settings.RESEND_API_KEY
        self.from_email = settings.RESEND_FROM_EMAIL
        self.app_name = settings.APP_NAME
        self.frontend_url = settings.FRONTEND_URL
        
        if self.api_key:
            resend.api_key = self.api_key

    def is_configured(self) -> bool:
        """Check if the email service is properly configured."""
        return bool(self.api_key)

    def send_password_reset_code(self, to_email: str, code: str) -> dict:
        """
        Send a password reset email with a 6-digit verification code.

        Args:
            to_email: Recipient email address
            code: The 6-digit verification code

        Returns:
            Response from Resend API
        """
        if not self.is_configured():
            raise ValueError("Email service is not configured. Set RESEND_API_KEY environment variable.")

        # Format code with spaces for better readability
        formatted_code = ' '.join(code)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reset Your Password</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f4f4f5; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); padding: 32px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 700;">{self.app_name}</h1>
                </div>
                
                <!-- Content -->
                <div style="padding: 32px;">
                    <h2 style="color: #1f2937; margin: 0 0 16px 0; font-size: 24px;">Password Reset Code</h2>
                    <p style="color: #4b5563; font-size: 16px; line-height: 1.6; margin: 0 0 24px 0;">
                        We received a request to reset your password. Use the verification code below to reset your password.
                    </p>
                    
                    <!-- Code Display -->
                    <div style="text-align: center; margin: 32px 0;">
                        <div style="display: inline-block; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); border: 2px solid #3B82F6; border-radius: 12px; padding: 20px 40px;">
                            <span style="font-size: 36px; font-weight: 700; letter-spacing: 8px; color: #1e40af; font-family: 'Courier New', monospace;">
                                {code}
                            </span>
                        </div>
                    </div>
                    
                    <p style="color: #6b7280; font-size: 14px; line-height: 1.6; margin: 24px 0 0 0; text-align: center;">
                        This code will expire in <strong>15 minutes</strong>.
                    </p>
                    
                    <!-- Warning -->
                    <div style="margin-top: 24px; padding: 16px; background-color: #fef3c7; border-radius: 8px; border-left: 4px solid #f59e0b;">
                        <p style="color: #92400e; font-size: 14px; margin: 0;">
                            <strong>Security tip:</strong> If you didn't request this password reset, please ignore this email. Your password will remain unchanged.
                        </p>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="background-color: #f9fafb; padding: 24px; text-align: center; border-top: 1px solid #e5e7eb;">
                    <p style="color: #9ca3af; font-size: 12px; margin: 0;">
                        © {self.app_name}. All rights reserved.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        params = {
            "from": f"{self.app_name} <{self.from_email}>",
            "to": [to_email],
            "subject": f"Your {self.app_name} password reset code: {code}",
            "html": html_content,
        }

        response = resend.Emails.send(params)
        return response


# Global instance
email_service = EmailService()


