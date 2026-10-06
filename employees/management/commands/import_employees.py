import csv

from django.core.management.base import BaseCommand, CommandError

from employees.services.csv_employee_service import (
    EmployeeCSVImportService,
)


class Command(BaseCommand):
    help = "Import employees from a CSV file."

    def add_arguments(self, parser):
        parser.add_argument(
            "input",
            help="Input CSV file path.",
        )

        parser.add_argument(
            "--atomic",
            action="store_true",
            help="Rollback the entire import if any row fails.",
        )

    def handle(self, *args, **options):
        input_file = options["input"]

        service = EmployeeCSVImportService()

        try:
            with open(
                input_file,
                "r",
                newline="",
                encoding="utf-8",
            ) as csv_file:
                reader = csv.DictReader(csv_file)

                service.validate_headers(reader.fieldnames)

                rows = list(
                    enumerate(
                        reader,
                        start=2,
                    )
                )

                result = service.import_rows(
                    rows,
                    atomic=options["atomic"],
                )

        except FileNotFoundError:
            raise CommandError(
                f"File not found: {input_file}"
            )

        except ValueError as exc:
            raise CommandError(str(exc))

        self.stdout.write(
            self.style.SUCCESS(
                f"Successful: {result['successful']}"
            )
        )

        self.stdout.write(
            self.style.WARNING(
                f"Skipped: {result['skipped']}"
            )
        )

        self.stdout.write(
            self.style.ERROR(
                f"Failed: {result['failed']}"
            )
        )

        for error in result["errors"]:
            self.stdout.write(
                self.style.ERROR(
                    f"Row {error['row']}: "
                    f"{', '.join(error['errors'])}"
                )
            )