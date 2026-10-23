from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from employees.models import Employee, Notification
from employees.tasks import send_welcome_email


User = get_user_model()


class SendWelcomeEmailTaskTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="celery_test_user",
            email="celery@example.com",
            password="testpass123",
        )

        self.employee = Employee.objects.create(
            user=self.user,
            employee_code="CELERY001",
            first_name="Celery",
            last_name="Test",
            email="celery@example.com",
            phone="9876543210",
            designation="Developer",
            salary=50000,
            joining_date="2026-01-01",
            is_active=True,
        )

    @patch(
        "employees.services.notification_service.EmailMultiAlternatives.send"
    )
    def test_successful_task_creates_one_welcome_notification(
        self,
        mock_send,
    ):
        mock_send.return_value = 1

        result = send_welcome_email.run(
            self.employee.id
        )

        self.assertIn(
            "Welcome email processed",
            result,
        )

        self.assertEqual(
            Notification.objects.filter(
                recipient=self.user,
                notification_type="WELCOME",
                email_sent=True,
            ).count(),
            1,
        )

    @patch(
        "employees.services.notification_service.EmailMultiAlternatives.send"
    )
    def test_failed_email_requests_bounded_retry(
        self,
        mock_send,
    ):
        mock_send.side_effect = RuntimeError(
            "Temporary email service failure"
        )

        with self.assertRaises(Exception):
            send_welcome_email.apply(
                args=[self.employee.id],
                throw=True,
            )

        self.assertEqual(
            mock_send.call_count,
            4,
        )

    @patch(
        "employees.services.notification_service.EmailMultiAlternatives.send"
    )
    def test_failed_email_requests_bounded_retry(
        self,
        mock_send,
    ):
        mock_send.side_effect = RuntimeError(
            "Temporary email service failure"
        )

        with self.assertRaises(Exception) as context:
            send_welcome_email.apply(
                args=[self.employee.id],
                throw=True,
            )

        self.assertIsNotNone(
            context.exception
        )

        mock_send.assert_called_once()

    def test_task_retry_configuration_is_bounded(self):
        self.assertEqual(
            send_welcome_email.max_retries,
            3,
        )

        self.assertTrue(
            send_welcome_email.autoretry_for
        )

        self.assertIn(
            RuntimeError,
            send_welcome_email.autoretry_for,
        )

        self.assertTrue(
            send_welcome_email.retry_backoff
        )

        self.assertEqual(
            send_welcome_email.retry_backoff_max,
            60,
        )

        self.assertTrue(
            send_welcome_email.retry_jitter
        )

        self.assertEqual(
            send_welcome_email.soft_time_limit,
            30,
        )

        self.assertEqual(
            send_welcome_email.time_limit,
            60,
        )