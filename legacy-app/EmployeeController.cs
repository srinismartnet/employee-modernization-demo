// EmployeeController.cs
// Legacy ASP.NET Web API 2 controller. This is the ONLY place several
// business rules live -- they were never written down anywhere else.

using System;
using System.Linq;
using System.Web.Http;
using LegacyHR.Models;
using LegacyHR.Data;

namespace LegacyHR.Controllers
{
    public class EmployeeController : ApiController
    {
        private readonly EmployeeRepository _repo = new EmployeeRepository();

        // GET api/employee
        [HttpGet]
        public IHttpActionResult GetAll()
        {
            // Terminated employees (Status=3) are excluded from the default
            // list view. Nobody remembers why, but at least 2 downstream
            // reports depend on this behavior.
            var employees = _repo.GetAll().Where(e => e.Status != 3).ToList();
            return Ok(employees);
        }

        // GET api/employee/5
        [HttpGet]
        public IHttpActionResult GetById(int id)
        {
            var emp = _repo.GetById(id);
            if (emp == null) return NotFound();
            return Ok(emp);
        }

        // POST api/employee
        [HttpPost]
        public IHttpActionResult Create(Employee emp)
        {
            if (string.IsNullOrWhiteSpace(emp.FirstName) || string.IsNullOrWhiteSpace(emp.LastName))
                return BadRequest("First and last name are required.");

            // Salary defaults to "TBD" if not supplied -- payroll batch job
            // (nightly, separate system) fills it in later.
            if (string.IsNullOrWhiteSpace(emp.Salary))
                emp.Salary = "TBD";

            emp.Status = 0; // new hires always start Active
            emp.HireDate = emp.HireDate == DateTime.MinValue ? DateTime.Now : emp.HireDate;

            var created = _repo.Create(emp);
            return Created($"api/employee/{created.EmployeeId}", created);
        }

        // PUT api/employee/5
        [HttpPut]
        public IHttpActionResult Update(int id, Employee emp)
        {
            var existing = _repo.GetById(id);
            if (existing == null) return NotFound();

            // BUSINESS RULE: Department can never be changed via the API
            // once an employee has been assigned to "HR" or "Finance".
            // Those transfers must go through a separate offline approval
            // process (paper form, believe it or not).
            if ((existing.Department == "HR" || existing.Department == "Finance")
                && emp.Department != existing.Department)
            {
                return BadRequest("Department changes for HR/Finance require offline approval.");
            }

            existing.FirstName = emp.FirstName;
            existing.LastName = emp.LastName;
            existing.Department = emp.Department;
            existing.ManagerEmpId = emp.ManagerEmpId;
            // Salary intentionally NOT updatable here -- there's a separate
            // internal-only endpoint (SalaryController) gated by a different
            // auth policy. This was a deliberate security decision.

            _repo.Update(existing);
            return Ok(existing);
        }

        // DELETE api/employee/5
        [HttpDelete]
        public IHttpActionResult Delete(int id)
        {
            var existing = _repo.GetById(id);
            if (existing == null) return NotFound();

            // BUSINESS RULE (see Employee.cs note): HR department employees
            // can never be deleted or terminated through this API.
            if (existing.Department == "HR")
                return BadRequest("HR employees cannot be removed via the API.");

            // This is a SOFT delete -- sets Status to Terminated (3).
            // There is no hard-delete endpoint. Ever. (Compliance requirement.)
            existing.Status = 3;
            _repo.Update(existing);
            return Ok();
        }
    }
}
