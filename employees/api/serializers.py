from rest_framework import serializers
from employees.models import EmployeeTransfer
from employees.models import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            'id',
            'employee_code',
            'first_name',
            'last_name',
            'email',
            'phone',
            'department',
            'designation',
            'salary',
            'joining_date',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
        ]
        
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