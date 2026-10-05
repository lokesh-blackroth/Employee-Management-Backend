import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import AuditLog, Employee


logger = logging.getLogger("employees")


@receiver(post_save, sender=Employee)
def employee_audit_log(sender, instance, created, **kwargs):
    try:
        if created:
            AuditLog.objects.create(
                employee=instance,
                action=AuditLog.ACTION_CREATED,
                description=f"Employee {instance.employee_code} was created.",
            )
        else:
            AuditLog.objects.create(
                employee=instance,
                action=AuditLog.ACTION_UPDATED,
                description=f"Employee {instance.employee_code} was updated.",
            )

    except Exception:
        logger.exception(
            "Failed to create audit log for employee %s",
            instance.employee_code,
        )