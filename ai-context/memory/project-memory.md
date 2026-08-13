---
# PROJECT MEMORY -- Employee HR Module
# This file is the AI's long-term memory for this migration.
# It is small, structured, and kept up to date as each module is migrated.
# It gets loaded in FULL on every task. The raw legacy code does NOT --
# that's retrieved on demand from ai-context/chunks/ (see retrieval step).
status: in-progress
last_updated: 2026-08-06
source_system: LegacyHR (.NET Framework 4.5, ASP.NET Web API 2, ADO.NET)
target_system: FastAPI (Python) + React frontend
---

## Entities

### Employee
| Legacy field    | Legacy type          | New field     | New type   | Notes |
|-----------------|-----------------------|---------------|------------|-------|
| EmployeeId      | int (PK, identity)     | id            | int (PK)   | unchanged |
| FirstName       | string                 | first_name    | str        | required |
| LastName        | string                 | last_name     | str        | required |
| Department      | string (free text)     | department    | str        | keep free text for now; do NOT convert to FK/enum, flagged for future ticket |
| Salary          | string ("50000"/"TBD"/"Confidential") | salary | Optional[float] | see Business Rule #3 |
| Status          | int (0-3)              | status        | enum: active, inactive, on_leave, terminated | see mapping below |
| HireDate        | DateTime               | hire_date     | date       | unchanged |
| ManagerEmpId    | string ("0" = none)    | manager_id    | Optional[int] | "0" maps to null |

Status code mapping (legacy int -> new enum):
0=active, 1=inactive, 2=on_leave, 3=terminated

## Business Rules (extracted from code, not from any spec doc)

1. **List endpoint excludes terminated employees by default.**
   Source: EmployeeController.GetAll(). At least 2 downstream reports
   depend on this. New API must replicate via default `status != terminated`
   filter, with an explicit `include_terminated=true` query param added
   for modern clients (improvement, not a behavior change to existing consumers).

2. **HR department employees cannot be deleted/terminated via the API.**
   Source: EmployeeController.Delete(). Added after a 2015 incident.
   Must be preserved exactly. Returns 400 in legacy; keep as 400/403 in new API.

3. **Salary is never updatable through the main Employee update endpoint.**
   It's handled by a separate, more restricted endpoint in the legacy system.
   New system: keep `salary` update out of `PUT /employees/{id}`, expose a
   separate `PATCH /employees/{id}/salary` with stricter auth (mirrors legacy
   security intent, not just accidental omission).

4. **Department changes for HR/Finance employees are blocked via API.**
   Source: EmployeeController.Update(). Must go through an offline/approval
   process. Preserve the block; the offline process itself is out of scope
   for this migration (still paper-based on legacy side, no digital record).

5. **New hires always start with status=active (0) and salary defaults to "TBD"
   equivalent** -- new system should default `salary` to `null` and treat
   null as "pending payroll assignment" rather than reusing a string sentinel.

6. **Deletes are always soft deletes.** There is no hard-delete anywhere in
   the legacy system (compliance requirement). Must remain soft-delete
   (status -> terminated) in the new system too.

## Known Data Quirks (for migration/ETL, not just API behavior)
- `Salary` column contains non-numeric strings ("TBD", "Confidential") in
  production data. Migration script must convert these to `NULL` and log
  a count of how many rows were affected.
- `ManagerEmpId` uses `"0"` as a string sentinel for "no manager" instead of
  NULL. Migration script must convert `"0"` -> `NULL`.
- `Department` has no referential integrity -- expect inconsistent casing
  ("HR", "hr", "Human Resources") in real data. Do NOT auto-correct during
  migration; flag mismatches for manual review instead.

## API Contract Decisions (legacy -> modern)
- `GET /api/employee` -> `GET /employees` (excludes terminated by default, Rule #1)
- `GET /api/employee/{id}` -> `GET /employees/{id}`
- `POST /api/employee` -> `POST /employees` (Rules #5)
- `PUT /api/employee/{id}` -> `PUT /employees/{id}` (Rules #3, #4)
- `DELETE /api/employee/{id}` -> `DELETE /employees/{id}` (Rules #2, #6 - soft delete only)

## Migration Progress Log
- [x] Employee model + schema mapped
- [x] Business rules extracted from EmployeeController.cs
- [ ] FastAPI backend generated (see modern-app/backend)
- [ ] React frontend generated (see modern-app/frontend)
- [ ] Data migration script for Salary/ManagerEmpId cleanup
- [ ] Parity test suite (old vs new behavior)
