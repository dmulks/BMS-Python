"""
Payment Voucher PDF Generation Service using ReportLab.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal
import os

from app.models.payment import PaymentVoucher, CouponPayment, VoucherStatus
from app.models.user import User
from app.models.bond import BondPurchase


class VoucherService:
    """Service for generating payment vouchers as PDFs."""

    @staticmethod
    def generate_voucher(
        db: Session,
        payment_id: int,
        generated_by: int,
        currency: str = "ZMW"
    ) -> dict:
        """
        Generate a payment voucher for a coupon payment.

        Args:
            db: Database session
            payment_id: ID of the coupon payment
            generated_by: User ID generating the voucher
            currency: Currency code (default: ZMW)

        Returns:
            Dictionary with voucher info and PDF path
        """
        # Get payment with related data
        payment = db.query(CouponPayment).filter(
            CouponPayment.payment_id == payment_id
        ).first()

        if not payment:
            raise ValueError("Payment not found")

        # Get user details
        user = db.query(User).filter(User.user_id == payment.user_id).first()

        # Get bond purchase details
        bond_purchase = db.query(BondPurchase).filter(
            BondPurchase.purchase_id == payment.purchase_id
        ).first()

        # Generate voucher number
        voucher_number = f"VOC{datetime.now().year}{payment_id:06d}"

        # Create voucher record
        voucher = PaymentVoucher(
            voucher_number=voucher_number,
            user_id=payment.user_id,
            payment_id=payment_id,
            voucher_date=datetime.now().date(),
            voucher_type=payment.payment_type,
            total_amount=payment.net_payment_amount,
            voucher_status=VoucherStatus.DRAFT,
            generated_by=generated_by
        )

        db.add(voucher)
        db.commit()
        db.refresh(voucher)

        # Generate PDF
        pdf_path = VoucherService._generate_pdf(
            voucher=voucher,
            payment=payment,
            user=user,
            bond_purchase=bond_purchase,
            currency=currency
        )

        return {
            "voucher": voucher,
            "pdf_path": pdf_path,
            "voucher_number": voucher_number
        }

    @staticmethod
    def _generate_pdf(
        voucher: PaymentVoucher,
        payment: CouponPayment,
        user: User,
        bond_purchase: BondPurchase,
        currency: str
    ) -> str:
        """
        Generate the PDF document for the voucher.

        Args:
            voucher: PaymentVoucher object
            payment: CouponPayment object
            user: User object
            bond_purchase: BondPurchase object
            currency: Currency code

        Returns:
            Path to generated PDF file
        """
        # Create temp directory if it doesn't exist
        temp_dir = os.path.join(os.path.dirname(__file__), '../../temp')
        os.makedirs(temp_dir, exist_ok=True)

        # PDF file path
        filename = f"voucher_{voucher.voucher_number}.pdf"
        filepath = os.path.join(temp_dir, filename)

        # Create document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Container for document elements
        elements = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#283593'),
            spaceAfter=20,
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=12,
            spaceBefore=12
        )

        # Header
        elements.append(Paragraph("Bond Cooperative Society", title_style))
        elements.append(Paragraph("Payment Voucher", subtitle_style))
        elements.append(Spacer(1, 0.3 * inch))

        # Voucher details table
        voucher_data = [
            ['Voucher Number:', voucher.voucher_number],
            ['Voucher Date:', voucher.voucher_date.strftime('%B %d, %Y')],
            ['Payment Type:', payment.payment_type.value.replace('_', ' ').title()],
            ['Payment Reference:', payment.payment_reference or 'N/A']
        ]

        voucher_table = Table(voucher_data, colWidths=[2 * inch, 4 * inch])
        voucher_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1a237e')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('LEFTPADDING', (1, 0), (1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(voucher_table)
        elements.append(Spacer(1, 0.4 * inch))

        # Payee details
        elements.append(Paragraph("Payee Information", heading_style))

        payee_data = [
            ['Name:', f"{user.first_name} {user.last_name}"],
            ['Email:', user.email],
            ['Phone:', user.phone_number or 'N/A'],
            ['Member ID:', f"M{user.user_id:04d}"]
        ]

        payee_table = Table(payee_data, colWidths=[2 * inch, 4 * inch])
        payee_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1a237e')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('LEFTPADDING', (1, 0), (1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(payee_table)
        elements.append(Spacer(1, 0.4 * inch))

        # Payment calculation breakdown
        elements.append(Paragraph("Payment Calculation", heading_style))

        payment_data = [
            ['Description', 'Amount'],
            ['Gross Coupon Amount', f'{currency} {float(payment.gross_coupon_amount):,.2f}'],
            ['Less: Withholding Tax (15%)', f'-{currency} {float(payment.withholding_tax):,.2f}'],
            ['Less: BOZ Fees (1%)', f'-{currency} {float(payment.boz_fees):,.2f}'],
            ['Less: Co-op Fees (2%)', f'-{currency} {float(payment.coop_fees):,.2f}'],
        ]

        payment_table = Table(payment_data, colWidths=[4 * inch, 2 * inch])
        payment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8eaf6')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica'),
            ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(payment_table)
        elements.append(Spacer(1, 0.2 * inch))

        # Net payment (highlighted)
        net_data = [['Net Payment Amount', f'{currency} {float(payment.net_payment_amount):,.2f}']]
        net_table = Table(net_data, colWidths=[4 * inch, 2 * inch])
        net_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1a237e')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))

        elements.append(net_table)
        elements.append(Spacer(1, 0.4 * inch))

        # Payment period
        elements.append(Paragraph("Payment Period", heading_style))
        period_data = [
            ['Period Start:', payment.payment_period_start.strftime('%B %d, %Y')],
            ['Period End:', payment.payment_period_end.strftime('%B %d, %Y')],
            ['Calendar Days:', str(payment.calendar_days)],
        ]

        period_table = Table(period_data, colWidths=[2 * inch, 4 * inch])
        period_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1a237e')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('LEFTPADDING', (1, 0), (1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        elements.append(period_table)
        elements.append(Spacer(1, 0.6 * inch))

        # Footer with signature lines
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_CENTER
        )

        signature_data = [
            ['_' * 30, '_' * 30],
            ['Prepared By', 'Approved By'],
            ['', ''],
            ['Date: ______________', 'Date: ______________']
        ]

        signature_table = Table(signature_data, colWidths=[3 * inch, 3 * inch])
        signature_table.setStyle(TableStyle([
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 1), (-1, 1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 20),
        ]))

        elements.append(signature_table)
        elements.append(Spacer(1, 0.3 * inch))
        elements.append(Paragraph(
            "This is a computer-generated document and does not require a signature.",
            footer_style
        ))

        # Build PDF
        doc.build(elements)

        return filepath
