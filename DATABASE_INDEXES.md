# Database Index Analysis

## 1. Objective

The objective of this task was to inspect existing PostgreSQL indexes, analyze query execution plans using `EXPLAIN ANALYZE`, and determine whether additional indexes are justified.

Indexes were evaluated based on actual query patterns rather than being added blindly.

---

## 2. Existing Indexes

The `employees_employee` table currently has the following indexes:

| Index | Column | Type/Purpose |
|---|---|---|
| `employees_employee_pkey` | `id` | Primary key |
| `employees_employee_employee_code_key` | `employee_code` | Unique index |
| `employees_employee_email_key` | `email` | Unique index |
| `employees_employee_employee_code_fb9b0c8f_like` | `employee_code` | Pattern matching |
| `employees_employee_email_14fffd5e_like` | `email` | Pattern matching |
| `employees_employee_department_id_410c23c8` | `department_id` | ForeignKey index |

---

## 3. Employee Code

Query tested:

```sql
EXPLAIN ANALYZE
SELECT *
FROM employees_employee
WHERE employee_code = 'EMP048';

PostgreSQL selected a Sequential Scan.

The table contains only 30 employees, so scanning the small table was inexpensive.

The existing unique index on employee_code was retained.

Finding

No additional index is required.

4. Email

The email field already has a unique constraint and corresponding unique index.

Therefore, an additional index on email would be redundant.

Finding

No additional index is required.

5. Department

Query tested:

EXPLAIN ANALYZE
SELECT *
FROM employees_employee
WHERE department_id = 1;

PostgreSQL selected a Sequential Scan.

The query returned 9 employees from the current 30-row dataset.

The existing department_id ForeignKey index was retained.

Finding

No additional index is required for the current dataset.

6. Is Active

Query tested:

EXPLAIN ANALYZE
SELECT *
FROM employees_employee
WHERE is_active = true;

Result:

Rows returned: 28
Rows filtered out: 2
Execution Time: 0.051 ms

The field does not currently have a dedicated index.

Because the condition returns 28 of 30 rows, the query has low selectivity.

Finding

A dedicated is_active index was not added.

For the current small dataset, PostgreSQL's Sequential Scan is inexpensive.

7. Joining Date

Query tested:

EXPLAIN ANALYZE
SELECT *
FROM employees_employee
ORDER BY joining_date;

PostgreSQL used:

Seq Scan
    |
    v
Sort

The query used an in-memory quicksort.

Result:

Rows: 30
Execution Time: 2.516 ms
Finding

joining_date is a potential index candidate for a larger production dataset or frequent ordering workload.

No index was added for the current 30-row development database.

8. Salary

Query tested:

EXPLAIN ANALYZE
SELECT *
FROM employees_employee
WHERE salary > 50000;

Result:

Rows returned: 21
Rows filtered out: 9
Execution Time: 0.107 ms

The query returned 21 of the 30 employees, so the condition has relatively low selectivity for the current data.

Finding

No salary index was added for the current dataset.

A salary index could be evaluated again if the table becomes significantly larger or salary-range queries become frequent and selective.

9. Query Plan Concepts
Sequential Scan

A Sequential Scan reads rows from the table and checks the filter condition.

Example:

Seq Scan on employees_employee

For a small table, this can be cheaper than using an index.

Index Scan

An Index Scan uses an index to locate matching rows rather than scanning the entire table.

Cost

Example:

cost=0.00..2.38

The PostgreSQL planner's estimated cost.

Cost is not execution time in milliseconds.

Rows

The rows value represents the planner's estimated number of rows.

Execution Time

Example:

Execution Time: 0.107 ms

This represents the measured execution time for the query.

10. Index Evaluation Summary
Field	Existing Index	Query Pattern	Decision
id	Yes	Primary-key lookup	Keep
employee_code	Yes	Exact lookup/search	Keep
email	Yes	Unique lookup	Keep
department_id	Yes	Filtering/joining	Keep
is_active	No	Boolean filtering	No new index
joining_date	No	Ordering	Candidate for larger workload
salary	No	Range filtering	Candidate for larger/selective workload
11. Indexing Principles

Indexes should not be added to every column.

When evaluating an index, consider:

Query frequency
Filter selectivity
Table size
Sorting and ordering requirements
Join patterns
Existing indexes
Index maintenance and storage overhead

An index is useful when it reduces the work required for common queries enough to justify its maintenance cost.

12. Conclusion

The existing PostgreSQL indexes were inspected and query plans were analyzed using EXPLAIN ANALYZE.

The current 30-row development database does not require additional indexes for is_active, joining_date, or salary.

joining_date and salary remain candidates for future evaluation as the dataset and workload grow.