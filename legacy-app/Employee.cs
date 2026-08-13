// Employee.cs
// Legacy .NET Framework 4.5 model (circa 2013). Untouched since ~2016.
// NOTE: Salary is stored as string because early versions supported
// "TBD" and "Confidential" as values. Never fully migrated to decimal.

using System;

namespace LegacyHR.Models
{
    public class Employee
    {
        public int EmployeeId { get; set; }
        public string FirstName { get; set; }
        public string LastName { get; set; }
        public string Department { get; set; } // free text, not FK'd to a table
        public string Salary { get; set; }      // "50000", "TBD", "Confidential"
        public int Status { get; set; }         // 0=Active,1=Inactive,2=OnLeave,3=Terminated
        public DateTime HireDate { get; set; }
        public string ManagerEmpId { get; set; } // nullable, stored as string, "0" means none

        // BUSINESS RULE (undocumented, found only in code):
        // Employees in the "HR" department can never be soft-deleted or
        // set to Terminated (Status=3) via the API. Only a DB admin can do it.
        // This was added after an incident in 2015 (see EmployeeController.Delete).
    }
}
