"""
SQLAlchemy model for Employee.
See ai-context/memory/project-memory.md -> Entities table for the
legacy-to-modern field mapping this is based on.
"""

import enum
from datetime import date

from sqlalchemy import Column, Integer, String, Float, Date, Enum, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class EmployeeStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    on_leave = "on_leave"
    terminated = "terminated"


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    department = Column(String, nullable=False)  # still free text, see memory notes
    salary = Column(Float, nullable=True)         # NULL = pending payroll assignment
    status = Column(Enum(EmployeeStatus), default=EmployeeStatus.active, nullable=False)
    hire_date = Column(Date, default=date.today, nullable=False)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
