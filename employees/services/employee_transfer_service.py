from django.db import transaction
from django.core.exceptions import ValidationError

from employees.models import Employee, EmployeeTransfer, Department


class EmployeeTransferService:

    @staticmethod
    @transaction.atomic
    def transfer_employee(
        employee_id,
        to_department_id,
        reason,
        transferred_by,
    ):
        # 1. Find employee
        try:
            employee = Employee.objects.select_related("department").get(
                id=employee_id
            )
        except Employee.DoesNotExist:
            raise ValidationError("Employee does not exist.")

        # 2. Validate employee is active
        if not employee.is_active:
            raise ValidationError("Inactive employees cannot be transferred.")

        # 3. Validate reason
        if not reason or not reason.strip():
            raise ValidationError("Transfer reason is required.")

        # 4. Find target department
        try:
            to_department = Department.objects.get(id=to_department_id)
        except Department.DoesNotExist:
            raise ValidationError("Target department does not exist.")

        # 5. Validate target department
        if employee.department_id == to_department.id:
            raise ValidationError(
                "Employee is already in the selected department."
            )

        if not to_department.is_active:
            raise ValidationError(
                "Employee cannot be transferred to an inactive department."
            )

        from_department = employee.department

        # 6. Create transfer history
        transfer = EmployeeTransfer.objects.create(
            employee=employee,
            from_department=from_department,
            to_department=to_department,
            reason=reason.strip(),
            transferred_by=transferred_by,
            status="COMPLETED",
        )

        # 7. Update employee department
        employee.department = to_department
        employee.save(update_fields=["department", "updated_at"])

        return transfer