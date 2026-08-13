"""
CRUD operations.
Every business rule referenced here maps to a numbered rule in
ai-context/memory/project-memory.md so the connection to the legacy
system is traceable, not guessed.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException

from . import models, schemas


def get_employees(db: Session, include_terminated: bool = False):
    # Rule #1: exclude terminated by default (legacy behavior), but expose
    # an explicit opt-in for modern clients that need the full list.
    query = db.query(models.Employee)
    if not include_terminated:
        query = query.filter(models.Employee.status != models.EmployeeStatus.terminated)
    return query.all()


def get_employee(db: Session, employee_id: int):
    return db.query(models.Employee).filter(models.Employee.id == employee_id).first()


def create_employee(db: Session, employee: schemas.EmployeeCreate):
    # Rule #5: new hires always start active; salary null == "TBD" equivalent.
    db_employee = models.Employee(
        first_name=employee.first_name,
        last_name=employee.last_name,
        department=employee.department,
        manager_id=employee.manager_id,
        salary=employee.salary,
        status=models.EmployeeStatus.active,
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def update_employee(db: Session, employee_id: int, employee: schemas.EmployeeUpdate):
    db_employee = get_employee(db, employee_id)
    if not db_employee:
        return None

    # Rule #4: block department change for HR/Finance employees via API.
    if (
        db_employee.department in ("HR", "Finance")
        and employee.department is not None
        and employee.department != db_employee.department
    ):
        raise HTTPException(
            status_code=400,
            detail="Department changes for HR/Finance require offline approval.",
        )

    update_data = employee.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_employee, field, value)

    db.commit()
    db.refresh(db_employee)
    return db_employee


def update_salary(db: Session, employee_id: int, salary_update: schemas.SalaryUpdate):
    # Rule #3: salary lives behind its own endpoint/permission boundary,
    # intentionally separate from the general update endpoint.
    db_employee = get_employee(db, employee_id)
    if not db_employee:
        return None
    db_employee.salary = salary_update.salary
    db.commit()
    db.refresh(db_employee)
    return db_employee


def delete_employee(db: Session, employee_id: int):
    db_employee = get_employee(db, employee_id)
    if not db_employee:
        return None

    # Rule #2: HR department employees can never be removed via the API.
    if db_employee.department == "HR":
        raise HTTPException(
            status_code=400,
            detail="HR employees cannot be removed via the API.",
        )

    # Rule #6: soft delete only -- there is no hard delete, ever.
    db_employee.status = models.EmployeeStatus.terminated
    db.commit()
    db.refresh(db_employee)
    return db_employee
