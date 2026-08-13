// EmployeeRepository.cs
// Legacy ADO.NET data access -- raw SQL, no ORM.

using System;
using System.Collections.Generic;
using System.Data.SqlClient;
using LegacyHR.Models;

namespace LegacyHR.Data
{
    public class EmployeeRepository
    {
        private readonly string _connStr =
            System.Configuration.ConfigurationManager
                .ConnectionStrings["HRConnection"].ConnectionString;

        public List<Employee> GetAll()
        {
            var list = new List<Employee>();
            using (var conn = new SqlConnection(_connStr))
            using (var cmd = new SqlCommand("SELECT * FROM Employees", conn))
            {
                conn.Open();
                using (var reader = cmd.ExecuteReader())
                {
                    while (reader.Read())
                        list.Add(Map(reader));
                }
            }
            return list;
        }

        public Employee GetById(int id)
        {
            using (var conn = new SqlConnection(_connStr))
            using (var cmd = new SqlCommand("SELECT * FROM Employees WHERE EmployeeId=@id", conn))
            {
                cmd.Parameters.AddWithValue("@id", id);
                conn.Open();
                using (var reader = cmd.ExecuteReader())
                {
                    if (reader.Read()) return Map(reader);
                }
            }
            return null;
        }

        public Employee Create(Employee emp)
        {
            using (var conn = new SqlConnection(_connStr))
            using (var cmd = new SqlCommand(
                @"INSERT INTO Employees (FirstName,LastName,Department,Salary,Status,HireDate,ManagerEmpId)
                  OUTPUT INSERTED.EmployeeId
                  VALUES (@fn,@ln,@dept,@sal,@status,@hire,@mgr)", conn))
            {
                cmd.Parameters.AddWithValue("@fn", emp.FirstName);
                cmd.Parameters.AddWithValue("@ln", emp.LastName);
                cmd.Parameters.AddWithValue("@dept", emp.Department ?? "");
                cmd.Parameters.AddWithValue("@sal", emp.Salary ?? "TBD");
                cmd.Parameters.AddWithValue("@status", emp.Status);
                cmd.Parameters.AddWithValue("@hire", emp.HireDate);
                cmd.Parameters.AddWithValue("@mgr", emp.ManagerEmpId ?? "0");
                conn.Open();
                emp.EmployeeId = (int)cmd.ExecuteScalar();
            }
            return emp;
        }

        public void Update(Employee emp)
        {
            using (var conn = new SqlConnection(_connStr))
            using (var cmd = new SqlCommand(
                @"UPDATE Employees SET FirstName=@fn,LastName=@ln,Department=@dept,
                  Status=@status,ManagerEmpId=@mgr WHERE EmployeeId=@id", conn))
            {
                cmd.Parameters.AddWithValue("@fn", emp.FirstName);
                cmd.Parameters.AddWithValue("@ln", emp.LastName);
                cmd.Parameters.AddWithValue("@dept", emp.Department ?? "");
                cmd.Parameters.AddWithValue("@status", emp.Status);
                cmd.Parameters.AddWithValue("@mgr", emp.ManagerEmpId ?? "0");
                cmd.Parameters.AddWithValue("@id", emp.EmployeeId);
                conn.Open();
                cmd.ExecuteNonQuery();
            }
        }

        private Employee Map(SqlDataReader r)
        {
            return new Employee
            {
                EmployeeId = (int)r["EmployeeId"],
                FirstName = r["FirstName"].ToString(),
                LastName = r["LastName"].ToString(),
                Department = r["Department"].ToString(),
                Salary = r["Salary"].ToString(),
                Status = (int)r["Status"],
                HireDate = (DateTime)r["HireDate"],
                ManagerEmpId = r["ManagerEmpId"].ToString()
            };
        }
    }
}
