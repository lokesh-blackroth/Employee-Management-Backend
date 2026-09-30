from django.conf import settings
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Employee(models.Model):
    user = models.OneToOneField(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    related_name="employee",
    null=True,
    blank=True,
    )
    employee_code = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="employees",
        null=True,
        blank=True,
    )

    designation = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    joining_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    projects = models.ManyToManyField(
        "Project",
        related_name="employees",
        blank=True,
    )

    def __str__(self):
        return f"{self.employee_code} - {self.first_name} {self.last_name}"
    
class UserRole(models.Model):
    ROLE_CHOICES = [
        ("ADMIN", "Admin"),
        ("HR", "HR"),
        ("MANAGER", "Manager"),
        ("EMPLOYEE", "Employee"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_role",
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="EMPLOYEE",
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class EmployeeProfile(models.Model):
    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    date_of_birth = models.DateField()
    address = models.TextField()
    emergency_contact = models.CharField(max_length=15)
    blood_group = models.CharField(max_length=5)
    profile_image = models.ImageField(
        upload_to="employee_profiles/",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile - {self.employee.employee_code}"


class Project(models.Model):
    name = models.CharField(max_length=150)
    project_code = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True)
    client_name = models.CharField(max_length=150)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.project_code} - {self.name}"
class EmployeeTransfer(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("COMPLETED", "Completed"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="transfers",
    )
    from_department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="transfers_from",
    )
    to_department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="transfers_to",
    )
    reason = models.TextField()
    transferred_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="employee_transfers",
    )
    transferred_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="COMPLETED",
    )

    def __str__(self):
        return f"{self.employee} - {self.from_department} → {self.to_department}"