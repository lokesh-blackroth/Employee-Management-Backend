from django.db import migrations, models
import django.db.models.deletion


def migrate_department_data(apps, schema_editor):
    Department = apps.get_model("employees", "Department")
    Employee = apps.get_model("employees", "Employee")

    departments = {
        "Backend": ("BACK", "Backend Development"),
        "Frontend": ("FRONT", "Frontend Development"),
        "QA": ("QA", "Quality Assurance"),
        "HR": ("HR", "Human Resources"),
        "Finance": ("FIN", "Finance"),
        "DevOps": ("DEVOPS", "DevOps"),
        "Testing": ("TEST", "Testing"),
    }

    department_objects = {}

    for name, (code, description) in departments.items():
        department, created = Department.objects.get_or_create(
            name=name,
            defaults={
                "code": code,
                "description": description,
                "is_active": True,
            },
        )

        department_objects[name] = department

    for employee in Employee.objects.all():
        if employee.department:
            department = department_objects.get(employee.department)

            if department:
                employee.department_fk_id = department.id
                employee.save(update_fields=["department_fk"])


class Migration(migrations.Migration):

    dependencies = [
        (
            "employees",
            "0003_remove_employee_employees_e_departm_e28f46_idx_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="Department",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=100,
                        unique=True,
                    ),
                ),
                (
                    "code",
                    models.CharField(
                        max_length=20,
                        unique=True,
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                    ),
                ),
            ],
        ),

        migrations.AddField(
            model_name="employee",
            name="department_fk",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="employees_temp",
                to="employees.department",
            ),
        ),

        migrations.RunPython(
            migrate_department_data,
            migrations.RunPython.noop,
        ),

        migrations.RemoveField(
            model_name="employee",
            name="department",
        ),

        migrations.RenameField(
            model_name="employee",
            old_name="department_fk",
            new_name="department",
        ),
    ]