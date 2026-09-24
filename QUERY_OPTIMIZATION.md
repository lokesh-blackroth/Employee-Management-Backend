# Query Optimization & N+1 Problem

## 1. Objective

The objective of this task was to identify and optimize inefficient Django ORM queries, specifically the N+1 query problem, and measure the performance improvement.

---

## 2. N+1 Problem

The employee details endpoint initially used:

```python
employees = Employee.objects.all()
The code then accessed:

employee.department
employee.profile
employee.projects.all()

The code then accessed:

employee.department
employee.profile
employee.projects.all()

inside a loop.

Because these relationships were not loaded in advance, Django executed additional database queries for each employee.

With 30 employees:

1 query for employees
30 queries for departments
30 queries for profiles
30 queries for projects

Total = 91 queries

Formula:

1 + (30 × 3) = 91 queries
3. Unoptimized Queryset
employees = Employee.objects.all()

Relationships were accessed inside the loop:

for employee in employees:
    employee.department
    employee.profile
    list(employee.projects.all())

This resulted in the N+1 query problem.

4. Optimized Queryset

The queryset was optimized using select_related() and prefetch_related():

employees = (
    Employee.objects
    .select_related("department", "profile")
    .prefetch_related("projects")
)
select_related()

Used for:

Department (ForeignKey)
EmployeeProfile (OneToOneField)

These relationships are loaded using SQL joins.

prefetch_related()

Used for:

Projects (ManyToManyField)

Django retrieves the related projects using a separate query and associates them with the employees in memory.

5. Query Count Comparison
Before Optimization
Employee query: 1
Department queries: 30
Profile queries: 30
Project queries: 30

Total: 91 queries
After Optimization
Employee + Department + Profile: 1 query
Projects: 1 query

Total: 2 queries
Result
91 queries → 2 queries

This removed the N+1 query pattern for the tested employee details workflow.

6. Performance Comparison
Metric	Before	After
Employees	30	30
Database Queries	91	2
Department Loading	N+1	select_related
Profile Loading	N+1	select_related
Project Loading	N+1	prefetch_related
Execution Time	0.2099 sec	0.2204 sec

The optimized benchmark produced an execution time of approximately 0.2204 seconds.

The timing difference is small because the development database contains only 30 employees. The significant result is the reduction in database queries from 91 to 2.

7. Optimized SQL Queries

The optimized implementation generated two database queries.

Query 1 — Employee, Department and Profile

select_related() generated a query joining the employee table with the department and employee profile tables.

Conceptually:

Employee
   |
   +-- Department
   |
   +-- EmployeeProfile
Query 2 — Projects

prefetch_related("projects") generated a separate query to retrieve projects for all employees using the employee IDs.

Conceptually:

Employees
    |
    +-- Employee_Project mapping
            |
            +-- Projects

This avoids executing one project query for every employee.

8. API Endpoint

The intentional N+1 endpoint is:

GET /api/v1/employees/details/

The endpoint returns:

Employee information
Department information
Employee profile information
Project information

The endpoint was tested successfully before and after optimization.

9. Optimization Techniques
select_related()

Use select_related() for single-valued relationships such as:

ForeignKey
OneToOneField

Example:

Employee.objects.select_related(
    "department",
    "profile",
)
prefetch_related()

Use prefetch_related() for multi-valued relationships such as:

ManyToManyField
Reverse ForeignKey relationships

Example:

Employee.objects.prefetch_related(
    "projects",
)
10. Key Findings
The original implementation generated 91 queries for 30 employees.
The problem was caused by accessing related objects inside the employee loop.
select_related() eliminated repeated queries for Department and EmployeeProfile.
prefetch_related() eliminated repeated queries for Projects.
The optimized implementation generated only 2 queries.
The response data remained available for all 30 employees and their projects.
Query count is a more meaningful optimization measurement for this small local dataset than the small timing difference.
11. Conclusion

The N+1 query problem was successfully identified, measured and optimized.

The final optimized queryset is:

employees = (
    Employee.objects
    .select_related("department", "profile")
    .prefetch_related("projects")
)

The database query count was reduced from:

91 → 2

while maintaining the employee details response structure.