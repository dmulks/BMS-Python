"""
Email Notification Service for sending emails to members.
"""
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.models.payment import CouponPayment
from app.models.bond import BondPurchase


class EmailService:
    """Service for sending email notifications."""

    @staticmethod
    def _send_email(
        to_email: str,
        subject: str,
        html_content: str,
        cc: Optional[List[str]] = None
    ) -> bool:
        """
        Send an email using SMTP.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of email
            cc: Optional list of CC email addresses

        Returns:
            True if successful, False otherwise
        """
        # Check if email is configured
        if not settings.SMTP_HOST or not settings.SMTP_USER:
            print("Warning: SMTP not configured. Email not sent.")
            return False

        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = settings.SMTP_USER
            message['To'] = to_email

            if cc:
                message['Cc'] = ', '.join(cc)

            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)

            # Connect to SMTP server and send
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

                recipients = [to_email]
                if cc:
                    recipients.extend(cc)

                server.sendmail(settings.SMTP_USER, recipients, message.as_string())

            return True

        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False

    @staticmethod
    def send_payment_notification(
        db: Session,
        payment: CouponPayment,
        currency: str = "ZMW"
    ) -> bool:
        """
        Send payment notification to member.

        Args:
            db: Database session
            payment: CouponPayment object
            currency: Currency code

        Returns:
            True if successful
        """
        user = db.query(User).filter(User.user_id == payment.user_id).first()

        if not user:
            return False

        subject = f"Coupon Payment Notification - {payment.payment_reference}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #1a237e; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f5f5f5; padding: 20px; }}
                .payment-details {{ background-color: white; padding: 15px; margin: 15px 0; border-radius: 5px; }}
                .amount {{ font-size: 24px; font-weight: bold; color: #1a237e; text-align: center; margin: 20px 0; }}
                table {{ width: 100%; border-collapse: collapse; }}
                td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
                .label {{ font-weight: bold; width: 50%; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Bond Cooperative Society</h1>
                    <h2>Payment Notification</h2>
                </div>
                <div class="content">
                    <p>Dear {user.first_name} {user.last_name},</p>
                    <p>We are pleased to inform you that a coupon payment has been processed for your bond holding.</p>

                    <div class="amount">
                        Net Payment: {currency} {float(payment.net_payment_amount):,.2f}
                    </div>

                    <div class="payment-details">
                        <h3>Payment Details</h3>
                        <table>
                            <tr>
                                <td class="label">Payment Reference:</td>
                                <td>{payment.payment_reference}</td>
                            </tr>
                            <tr>
                                <td class="label">Payment Type:</td>
                                <td>{payment.payment_type.value.replace('_', ' ').title()}</td>
                            </tr>
                            <tr>
                                <td class="label">Payment Date:</td>
                                <td>{payment.payment_date.strftime('%B %d, %Y')}</td>
                            </tr>
                            <tr>
                                <td class="label">Period:</td>
                                <td>{payment.payment_period_start.strftime('%B %d, %Y')} to {payment.payment_period_end.strftime('%B %d, %Y')}</td>
                            </tr>
                            <tr>
                                <td class="label">Calendar Days:</td>
                                <td>{payment.calendar_days}</td>
                            </tr>
                        </table>
                    </div>

                    <div class="payment-details">
                        <h3>Payment Breakdown</h3>
                        <table>
                            <tr>
                                <td class="label">Gross Coupon Amount:</td>
                                <td>{currency} {float(payment.gross_coupon_amount):,.2f}</td>
                            </tr>
                            <tr>
                                <td class="label">Less: Withholding Tax (15%):</td>
                                <td>-{currency} {float(payment.withholding_tax):,.2f}</td>
                            </tr>
                            <tr>
                                <td class="label">Less: BOZ Fees (1%):</td>
                                <td>-{currency} {float(payment.boz_fees):,.2f}</td>
                            </tr>
                            <tr>
                                <td class="label">Less: Co-op Fees (2%):</td>
                                <td>-{currency} {float(payment.coop_fees):,.2f}</td>
                            </tr>
                            <tr style="font-weight: bold; background-color: #f0f0f0;">
                                <td class="label">Net Payment Amount:</td>
                                <td>{currency} {float(payment.net_payment_amount):,.2f}</td>
                            </tr>
                        </table>
                    </div>

                    <p>If you have any questions about this payment, please contact us.</p>

                    <p>Best regards,<br>
                    Bond Cooperative Society<br>
                    Finance Department</p>
                </div>
                <div class="footer">
                    <p>This is an automated email. Please do not reply to this message.</p>
                    <p>&copy; {payment.payment_date.year} Bond Cooperative Society. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return EmailService._send_email(user.email, subject, html_content)

    @staticmethod
    def send_maturity_reminder(
        db: Session,
        bond_purchase: BondPurchase,
        days_until_maturity: int,
        currency: str = "ZMW"
    ) -> bool:
        """
        Send maturity reminder to member.

        Args:
            db: Database session
            bond_purchase: BondPurchase object
            days_until_maturity: Days until bond matures
            currency: Currency code

        Returns:
            True if successful
        """
        user = db.query(User).filter(User.user_id == bond_purchase.user_id).first()

        if not user:
            return False

        subject = f"Bond Maturity Reminder - {days_until_maturity} Days"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #ff6f00; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #fff8e1; padding: 20px; }}
                .bond-details {{ background-color: white; padding: 15px; margin: 15px 0; border-radius: 5px; }}
                .warning {{ background-color: #fff3cd; border-left: 4px solid #ff6f00; padding: 15px; margin: 15px 0; }}
                table {{ width: 100%; border-collapse: collapse; }}
                td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
                .label {{ font-weight: bold; width: 50%; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Bond Cooperative Society</h1>
                    <h2>Bond Maturity Reminder</h2>
                </div>
                <div class="content">
                    <p>Dear {user.first_name} {user.last_name},</p>

                    <div class="warning">
                        <strong>Important:</strong> Your bond will mature in {days_until_maturity} days.
                    </div>

                    <div class="bond-details">
                        <h3>Bond Details</h3>
                        <table>
                            <tr>
                                <td class="label">Transaction Reference:</td>
                                <td>{bond_purchase.transaction_reference}</td>
                            </tr>
                            <tr>
                                <td class="label">Purchase Date:</td>
                                <td>{bond_purchase.purchase_date.strftime('%B %d, %Y')}</td>
                            </tr>
                            <tr>
                                <td class="label">Maturity Date:</td>
                                <td>{bond_purchase.maturity_date.strftime('%B %d, %Y')}</td>
                            </tr>
                            <tr>
                                <td class="label">Bond Shares:</td>
                                <td>{float(bond_purchase.bond_shares):,.2f}</td>
                            </tr>
                            <tr>
                                <td class="label">Face Value:</td>
                                <td>{currency} {float(bond_purchase.face_value):,.2f}</td>
                            </tr>
                        </table>
                    </div>

                    <p><strong>What happens at maturity?</strong></p>
                    <ul>
                        <li>Final coupon payment will be calculated and processed</li>
                        <li>Principal amount will be returned</li>
                        <li>Bond will be marked as matured</li>
                    </ul>

                    <p>No action is required from your side. We will process everything automatically on the maturity date.</p>

                    <p>If you have any questions, please contact us.</p>

                    <p>Best regards,<br>
                    Bond Cooperative Society</p>
                </div>
                <div class="footer">
                    <p>This is an automated reminder. Please do not reply to this message.</p>
                    <p>&copy; {bond_purchase.maturity_date.year} Bond Cooperative Society. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return EmailService._send_email(user.email, subject, html_content)

    @staticmethod
    def send_welcome_email(user: User) -> bool:
        """
        Send welcome email to new member.

        Args:
            user: User object

        Returns:
            True if successful
        """
        subject = "Welcome to Bond Cooperative Society"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #1a237e; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f5f5f5; padding: 20px; }}
                .features {{ background-color: white; padding: 15px; margin: 15px 0; border-radius: 5px; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to Bond Cooperative Society!</h1>
                </div>
                <div class="content">
                    <p>Dear {user.first_name} {user.last_name},</p>
                    <p>Welcome to the Bond Cooperative Society! We are excited to have you as a member.</p>

                    <div class="features">
                        <h3>Your Member Benefits</h3>
                        <ul>
                            <li>Access to competitive bond investment opportunities</li>
                            <li>Regular coupon interest payments</li>
                            <li>Online portfolio management</li>
                            <li>Real-time payment notifications</li>
                            <li>Detailed transaction reports</li>
                        </ul>
                    </div>

                    <div class="features">
                        <h3>Getting Started</h3>
                        <ol>
                            <li>Log in to your member portal</li>
                            <li>Complete your profile information</li>
                            <li>Browse available bond types</li>
                            <li>Contact us to make your first investment</li>
                        </ol>
                    </div>

                    <p>If you have any questions, please don't hesitate to contact us.</p>

                    <p>Best regards,<br>
                    Bond Cooperative Society Team</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 Bond Cooperative Society. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return EmailService._send_email(user.email, subject, html_content)
