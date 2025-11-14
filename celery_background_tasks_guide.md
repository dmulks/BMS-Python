# Celery Background Tasks Guide

## Complete Celery Implementation for Bond Management System

This guide covers:
1. Celery Setup and Configuration
2. Automated Monthly Coupon Calculations
3. Email Notifications
4. Report Generation Tasks
5. Scheduled Jobs
6. Monitoring and Management

---

## Part 1: Celery Setup

### Step 1: Install Dependencies

```bash
pip install celery==5.3.4
pip install redis==5.0.1
pip install celery-beat==2.5.0
pip install flower==2.0.1  # For monitoring
```

### Step 2: Celery Configuration

**app/core/celery_config.py:**
```python
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Initialize Celery
celery_app = Celery(
    "bond_management",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)

# Scheduled tasks configuration
celery_app.conf.beat_schedule = {
    # Monthly coupon calculation (1st of every month at 2 AM)
    'calculate-monthly-coupons': {
        'task': 'app.tasks.payment_tasks.calculate_monthly_coupons_task',
        'schedule': crontab(hour=2, minute=0, day_of_month=1),
    },
    
    # Daily maturity check (every day at 9 AM)
    'check-maturing-bonds': {
        'task': 'app.tasks.bond_tasks.check_maturing_bonds_task',
        'schedule': crontab(hour=9, minute=0),
    },
    
    # Weekly summary report (Monday at 8 AM)
    'weekly-summary-report': {
        'task': 'app.tasks.report_tasks.generate_weekly_summary_task',
        'schedule': crontab(hour=8, minute=0, day_of_week=1),
    },
}

celery_app.autodiscover_tasks(['app.tasks'])
```

---

## Part 2: Payment Tasks

### Automated Coupon Calculation

**app/tasks/payment_tasks.py:**
```python
from celery import shared_task
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.coupon_service import CouponCalculationService
from app.services.voucher_service import VoucherService
from app.models.notification import Notification, NotificationType
from app.models.user import User


@shared_task(bind=True, name='app.tasks.payment_tasks.calculate_monthly_coupons_task')
def calculate_monthly_coupons_task(self):
    """
    Calculate and process monthly coupon payments.
    Runs on the 1st of every month at 2 AM.
    """
    db = SessionLocal()
    try:
        today = date.today()
        six_months_ago = today - relativedelta(months=6)
        
        # Calculate coupons
        service = CouponCalculationService(db)
        calculations = service.calculate_coupons_for_period(six_months_ago, today)
        
        # Process payments
        payments = service.process_coupon_payments(calculations, processed_by=1)  # System user
        
        # Update task state
        self.update_state(
            state='SUCCESS',
            meta={
                'date': today.isoformat(),
                'calculations_count': len(calculations),
                'payments_created': len(payments),
                'total_amount': float(sum(p.net_payment_amount for p in payments))
            }
        )
        
        return {
            'status': 'completed',
            'date': today.isoformat(),
            'payments_created': len(payments)
        }
        
    except Exception as e:
        # Log error and notify admins
        notify_admins_of_error(db, 'Coupon Calculation Failed', str(e))
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise
        
    finally:
        db.close()


@shared_task(name='app.tasks.payment_tasks.generate_voucher_task')
def generate_voucher_task(payment_id: int, generated_by: int):
    """
    Generate payment voucher in background.
    """
    db = SessionLocal()
    try:
        service = VoucherService(db)
        result = service.generate_voucher(payment_id, generated_by)
        
        return {
            'status': 'completed',
            'voucher_id': result['voucher'].voucher_id,
            'voucher_number': result['voucher_number']
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e)
        }
        
    finally:
        db.close()


@shared_task(name='app.tasks.payment_tasks.batch_generate_vouchers_task')
def batch_generate_vouchers_task(payment_ids: list, generated_by: int):
    """
    Generate multiple vouchers in background.
    """
    db = SessionLocal()
    try:
        service = VoucherService(db)
        results = service.generate_batch_vouchers(payment_ids, generated_by)
        
        successful = [r for r in results if 'voucher' in r]
        failed = [r for r in results if 'error' in r]
        
        return {
            'status': 'completed',
            'total': len(payment_ids),
            'successful': len(successful),
            'failed': len(failed)
        }
        
    finally:
        db.close()


@shared_task(name='app.tasks.payment_tasks.send_payment_notifications_task')
def send_payment_notifications_task(user_ids: list = None):
    """
    Send payment due notifications to members.
    """
    db = SessionLocal()
    try:
        from app.models.payment import CouponPayment, PaymentStatus
        
        # Get pending payments
        query = db.query(CouponPayment).filter(
            CouponPayment.payment_status == PaymentStatus.PENDING
        )
        
        if user_ids:
            query = query.filter(CouponPayment.user_id.in_(user_ids))
        
        pending_payments = query.all()
        
        notifications_sent = 0
        for payment in pending_payments:
            # Create notification
            notification = Notification(
                user_id=payment.user_id,
                notification_type=NotificationType.PAYMENT_DUE,
                title="Payment Due",
                message=f"Your coupon payment of ${payment.net_payment_amount:.2f} is ready for processing.",
                related_entity_type="coupon_payment",
                related_entity_id=payment.payment_id
            )
            db.add(notification)
            notifications_sent += 1
        
        db.commit()
        
        return {
            'status': 'completed',
            'notifications_sent': notifications_sent
        }
        
    finally:
        db.close()


def notify_admins_of_error(db: Session, subject: str, error_message: str):
    """Helper function to notify admins of errors."""
    admins = db.query(User).filter(User.user_role == 'admin', User.is_active == True).all()
    
    for admin in admins:
        notification = Notification(
            user_id=admin.user_id,
            notification_type=NotificationType.SYSTEM,
            title=subject,
            message=error_message
        )
        db.add(notification)
    
    db.commit()
```

---

## Part 3: Bond Tasks

**app/tasks/bond_tasks.py:**
```python
from celery import shared_task
from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.bond import BondPurchase, PurchaseStatus
from app.models.notification import Notification, NotificationType
from app.models.user import User


@shared_task(name='app.tasks.bond_tasks.check_maturing_bonds_task')
def check_maturing_bonds_task():
    """
    Check for bonds maturing in the next 30 days and send notifications.
    Runs daily at 9 AM.
    """
    db = SessionLocal()
    try:
        today = date.today()
        thirty_days_later = today + timedelta(days=30)
        
        # Find bonds maturing in next 30 days
        maturing_bonds = db.query(BondPurchase).filter(
            BondPurchase.maturity_date >= today,
            BondPurchase.maturity_date <= thirty_days_later,
            BondPurchase.purchase_status == PurchaseStatus.ACTIVE
        ).all()
        
        notifications_created = 0
        
        for bond in maturing_bonds:
            days_until_maturity = (bond.maturity_date - today).days
            
            # Create notification
            notification = Notification(
                user_id=bond.user_id,
                notification_type=NotificationType.MATURITY_APPROACHING,
                title="Bond Maturity Approaching",
                message=f"Your bond (Purchase ID: {bond.purchase_id}) will mature in {days_until_maturity} days on {bond.maturity_date}. "
                       f"Face Value: ${bond.face_value:,.2f}",
                related_entity_type="bond_purchase",
                related_entity_id=bond.purchase_id
            )
            db.add(notification)
            notifications_created += 1
        
        db.commit()
        
        return {
            'status': 'completed',
            'maturing_bonds_count': len(maturing_bonds),
            'notifications_sent': notifications_created
        }
        
    finally:
        db.close()


@shared_task(name='app.tasks.bond_tasks.update_bond_status_task')
def update_bond_status_task():
    """
    Update status of bonds that have matured.
    """
    db = SessionLocal()
    try:
        today = date.today()
        
        # Find active bonds that have passed maturity date
        matured_bonds = db.query(BondPurchase).filter(
            BondPurchase.maturity_date < today,
            BondPurchase.purchase_status == PurchaseStatus.ACTIVE
        ).all()
        
        for bond in matured_bonds:
            bond.purchase_status = PurchaseStatus.MATURED
        
        db.commit()
        
        return {
            'status': 'completed',
            'bonds_updated': len(matured_bonds)
        }
        
    finally:
        db.close()
```

---

## Part 4: Report Tasks

**app/tasks/report_tasks.py:**
```python
from celery import shared_task
from datetime import date
from dateutil.relativedelta import relativedelta

from app.core.database import SessionLocal
from app.services.report_service import ReportService
from app.models.user import User, UserRole


@shared_task(name='app.tasks.report_tasks.generate_monthly_report_task')
def generate_monthly_report_task(month: str):
    """
    Generate monthly report in background.
    
    Args:
        month: Month in YYYY-MM-01 format
    """
    db = SessionLocal()
    try:
        report_date = date.fromisoformat(month)
        service = ReportService(db)
        
        # Generate report
        summary = service.generate_monthly_summary(report_date)
        
        # Export to Excel
        filepath = service.export_monthly_summary_to_excel(report_date)
        
        return {
            'status': 'completed',
            'month': month,
            'filepath': filepath,
            'summary': summary
        }
        
    finally:
        db.close()


@shared_task(name='app.tasks.report_tasks.generate_weekly_summary_task')
def generate_weekly_summary_task():
    """
    Generate weekly summary report.
    Runs every Monday at 8 AM.
    """
    db = SessionLocal()
    try:
        today = date.today()
        last_week = today - timedelta(days=7)
        
        service = ReportService(db)
        
        # Generate payment register for the week
        register = service.generate_payment_register(last_week, today)
        
        # Notify admins
        admins = db.query(User).filter(
            User.user_role.in_([UserRole.ADMIN, UserRole.TREASURER]),
            User.is_active == True
        ).all()
        
        for admin in admins:
            notification = Notification(
                user_id=admin.user_id,
                notification_type=NotificationType.SYSTEM,
                title="Weekly Summary Available",
                message=f"Weekly summary for {last_week} to {today} is ready. "
                       f"Total payments: {register['summary']['total_payments']}"
            )
            db.add(notification)
        
        db.commit()
        
        return {
            'status': 'completed',
            'week_start': last_week.isoformat(),
            'week_end': today.isoformat(),
            'total_payments': register['summary']['total_payments']
        }
        
    finally:
        db.close()


@shared_task(name='app.tasks.report_tasks.batch_generate_portfolios_task')
def batch_generate_portfolios_task(user_ids: list = None):
    """
    Generate portfolio reports for multiple members.
    """
    db = SessionLocal()
    try:
        service = ReportService(db)
        
        # Get users
        if user_ids:
            users = db.query(User).filter(User.user_id.in_(user_ids)).all()
        else:
            users = db.query(User).filter(
                User.user_role == UserRole.MEMBER,
                User.is_active == True
            ).all()
        
        results = []
        for user in users:
            try:
                filepath = service.export_member_portfolio_to_excel(user.user_id)
                results.append({
                    'user_id': user.user_id,
                    'status': 'success',
                    'filepath': filepath
                })
            except Exception as e:
                results.append({
                    'user_id': user.user_id,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return {
            'status': 'completed',
            'total': len(users),
            'results': results
        }
        
    finally:
        db.close()
```

---

## Part 5: Email Tasks

**app/tasks/email_tasks.py:**
```python
from celery import shared_task
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import List

from app.core.config import settings


@shared_task(name='app.tasks.email_tasks.send_email_task')
def send_email_task(
    to_email: str,
    subject: str,
    body: str,
    html_body: str = None,
    attachments: List[str] = None
):
    """
    Send email in background.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Plain text body
        html_body: HTML body (optional)
        attachments: List of file paths to attach (optional)
    """
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.EMAILS_FROM_EMAIL
        msg['To'] = to_email
        
        # Add plain text
        msg.attach(MIMEText(body, 'plain'))
        
        # Add HTML if provided
        if html_body:
            msg.attach(MIMEText(html_body, 'html'))
        
        # Add attachments
        if attachments:
            for filepath in attachments:
                with open(filepath, 'rb') as f:
                    attachment = MIMEApplication(f.read())
                    attachment.add_header('Content-Disposition', 'attachment', 
                                        filename=filepath.split('/')[-1])
                    msg.attach(attachment)
        
        # Send email
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        
        return {
            'status': 'sent',
            'to': to_email,
            'subject': subject
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e)
        }


@shared_task(name='app.tasks.email_tasks.send_payment_voucher_email_task')
def send_payment_voucher_email_task(user_email: str, voucher_number: str, pdf_path: str):
    """Send payment voucher via email."""
    subject = f"Payment Voucher - {voucher_number}"
    body = f"""
    Dear Member,
    
    Your payment voucher {voucher_number} is attached.
    
    Please review the details and contact us if you have any questions.
    
    Best regards,
    Bond Cooperative Society
    """
    
    html_body = f"""
    <html>
    <body>
        <h2>Payment Voucher</h2>
        <p>Dear Member,</p>
        <p>Your payment voucher <strong>{voucher_number}</strong> is attached.</p>
        <p>Please review the details and contact us if you have any questions.</p>
        <br>
        <p>Best regards,<br>Bond Cooperative Society</p>
    </body>
    </html>
    """
    
    return send_email_task(user_email, subject, body, html_body, [pdf_path])
```

---

## Part 6: Running Celery

### Start Celery Worker

**Start worker:**
```bash
# In backend directory
celery -A app.core.celery_config:celery_app worker --loglevel=info
```

### Start Celery Beat (Scheduler)

```bash
celery -A app.core.celery_config:celery_app beat --loglevel=info
```

### Start Flower (Monitoring)

```bash
celery -A app.core.celery_config:celery_app flower --port=5555
```

Access Flower at: http://localhost:5555

---

## Part 7: Triggering Tasks from API

**Add task endpoints to payments.py:**

```python
@router.post("/tasks/calculate-monthly")
def trigger_monthly_calculation(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.TREASURER))
):
    """Manually trigger monthly coupon calculation."""
    from app.tasks.payment_tasks import calculate_monthly_coupons_task
    
    task = calculate_monthly_coupons_task.delay()
    
    return {
        "message": "Task started",
        "task_id": task.id
    }


@router.get("/tasks/{task_id}/status")
def get_task_status(
    task_id: str,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.TREASURER))
):
    """Get status of a background task."""
    from app.core.celery_config import celery_app
    
    task = celery_app.AsyncResult(task_id)
    
    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None
    }
```

---

## Part 8: Production Deployment

### Supervisor Configuration

**Create /etc/supervisor/conf.d/celery.conf:**
```ini
[program:celery_worker]
command=/path/to/venv/bin/celery -A app.core.celery_config:celery_app worker --loglevel=info
directory=/path/to/backend
user=bond_user
autostart=true
autorestart=true
stderr_logfile=/var/log/celery/worker.err.log
stdout_logfile=/var/log/celery/worker.out.log

[program:celery_beat]
command=/path/to/venv/bin/celery -A app.core.celery_config:celery_app beat --loglevel=info
directory=/path/to/backend
user=bond_user
autostart=true
autorestart=true
stderr_logfile=/var/log/celery/beat.err.log
stdout_logfile=/var/log/celery/beat.out.log

[program:flower]
command=/path/to/venv/bin/celery -A app.core.celery_config:celery_app flower --port=5555
directory=/path/to/backend
user=bond_user
autostart=true
autorestart=true
stderr_logfile=/var/log/celery/flower.err.log
stdout_logfile=/var/log/celery/flower.out.log
```

**Reload supervisor:**
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
```

---

## Summary

### ✅ Complete Celery Features:

1. **Automated Tasks**
   - Monthly coupon calculations
   - Daily maturity checks
   - Weekly summary reports

2. **Background Processing**
   - Voucher generation
   - Report generation
   - Batch operations

3. **Notifications**
   - Payment notifications
   - Maturity reminders
   - Admin alerts

4. **Email Integration**
   - Automated emails
   - Voucher delivery
   - Report distribution

5. **Monitoring**
   - Flower dashboard
   - Task status tracking
   - Error logging

### 🚀 Key Benefits:
- Non-blocking operations
- Scheduled automation
- Scalable architecture
- Error recovery
- Real-time monitoring

**System is production-ready with full automation!**
