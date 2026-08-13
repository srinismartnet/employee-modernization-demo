"""
Pydantic schemas for Employee.
Field mapping and rules sourced from ai-context/memory/project-memory.md
(Entities table + Business Rules #3, #5).
"""

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class EmployeeStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    on_leave = "on_leave"
    terminated = "terminated"


class EmployeeBase(BaseModel):
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    department: str
    manager_id: Optional[int] = None


class EmployeeCreate(EmployeeBase):
    # salary is intentionally NOT accepted here in a settable way beyond
    # optional initial value -- mirrors legacy Rule #5 (defaults, payroll
    # fills it in later). Left in as optional for initial data entry only.
    salary: Optional[float] = None


class EmployeeUpdate(BaseModel):
    # Rule #3: salary is never updatable through this schema, by design --
    # it's excluded entirely, not just optional. See salary.py router for
    # the dedicated, more restricted endpoint.
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    department: Optional[str] = None
    manager_id: Optional[int] = None


class SalaryUpdate(BaseModel):
    # Separate schema for the restricted salary endpoint (Rule #3).
    salary: float


class EmployeeOut(EmployeeBase):
    id: int
    salary: Optional[float]
    status: EmployeeStatus
    hire_date: date

    class Config:
        from_attributes = True
