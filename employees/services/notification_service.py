from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.template.loader import render_to_string

from employees.models import Notification


class NotificationService:

    @staticmethod
    def create_notification(
        recipient,
        notification_type,
        title,
        message,
    ):
        return Notification.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
        )

    @staticmethod
    def send_welcome_notification(employee):
        if employee.user is None:
            return None

        existing_notification = Notification.objects.filter(
            recipient=employee.user,
            notification_type="WELCOME",
            email_sent=True,
        ).first()

        if existing_notification:
            return existing_notification

        notification = NotificationService.create_notification(
            recipient=employee.user,
            notification_type="WELCOME",
            title="Welcome to Employee Management System",
            message=(
                f"Welcome {employee.first_name}! "
                "Your employee account has been created successfully."
            ),
        )

        NotificationService.send_email(
            notification=notification,
            subject="Welcome to Employee Management System",
            template_name="emails/welcome_email.html",
            context={
                "employee": employee,
            },
        )

        return notification

    @staticmethod
    def send_email(
        notification,
        subject,
        template_name,
        context,
    ):
        recipient_email = notification.recipient.email

        if not recipient_email:
            notification.email_error = "Recipient email is missing."
            notification.save(
                update_fields=["email_error"]
            )
            return False

        try:
            validate_email(recipient_email)
        except Exception:
            notification.email_error = "Invalid recipient email."
            notification.save(
                update_fields=["email_error"]
            )
            return False

        try:
            html_content = render_to_string(
                template_name,
                context,
            )

            email = EmailMultiAlternatives(
                subject=subject,
                body=notification.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email],
            )

            email.attach_alternative(
                html_content,
                "text/html",
            )

            email.send()

            notification.email_sent = True
            notification.email_error = ""

            notification.save(
                update_fields=[
                    "email_sent",
                    "email_error",
                ]
            )

            return True

        except Exception as exc:
            notification.email_sent = False
            notification.email_error = str(exc)

            notification.save(
                update_fields=[
                    "email_sent",
                    "email_error",
                ]
            )

            return False