from rest_framework import serializers

from employees.models import (
    Employee,
    EmployeeProfile,
    EmployeeTransfer,
    Notification,
)


class EmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = [
            "id",
            "employee_code",
            "first_name",
            "last_name",
            "email",
            "phone",
            "department",
            "designation",
            "salary",
            "joining_date",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_employee_code(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Employee code cannot be empty."
            )

        if len(value) > 20:
            raise serializers.ValidationError(
                "Employee code cannot exceed 20 characters."
            )

        return value

    def validate_first_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "First name cannot be empty."
            )

        if len(value) > 100:
            raise serializers.ValidationError(
                "First name cannot exceed 100 characters."
            )

        return value

    def validate_last_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Last name cannot be empty."
            )

        if len(value) > 100:
            raise serializers.ValidationError(
                "Last name cannot exceed 100 characters."
            )

        return value

    def validate_email(self, value):
        value = value.strip().lower()

        if not value:
            raise serializers.ValidationError(
                "Email cannot be empty."
            )

        return value

    def validate_salary(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Salary cannot be negative."
            )

        return value


class EmployeeTransferSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmployeeTransfer
        fields = [
            "id",
            "employee",
            "from_department",
            "to_department",
            "reason",
            "transferred_by",
            "transferred_at",
            "status",
        ]
        read_only_fields = [
            "id",
            "employee",
            "from_department",
            "transferred_by",
            "transferred_at",
            "status",
        ]


class EmployeeProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmployeeProfile
        fields = [
            "date_of_birth",
            "address",
            "emergency_contact",
            "blood_group",
            "profile_image",
        ]

    def validate_address(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Address cannot be empty."
            )

        return value

    def validate_emergency_contact(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Emergency contact cannot be empty."
            )

        if len(value) > 15:
            raise serializers.ValidationError(
                "Emergency contact cannot exceed 15 characters."
            )

        return value
class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = [
            "id",
            "notification_type",
            "title",
            "message",
            "is_read",
            "email_sent",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "notification_type",
            "title",
            "message",
            "email_sent",
            "created_at",
            "updated_at",
        ]