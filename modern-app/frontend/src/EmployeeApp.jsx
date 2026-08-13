import { useEffect, useState } from "react";
import { getEmployees, createEmployee, deleteEmployee } from "./api";

export default function EmployeeApp() {
  const [employees, setEmployees] = useState([]);
  const [form, setForm] = useState({ first_name: "", last_name: "", department: "" });
  const [error, setError] = useState("");

  const load = () => getEmployees().then(setEmployees);

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await createEmployee(form);
      setForm({ first_name: "", last_name: "", department: "" });
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async (id) => {
    setError("");
    try {
      await deleteEmployee(id);
      load();
    } catch (err) {
      // Surfaces backend rule violations, e.g. "HR employees cannot be
      // removed via the API." -- the same rule preserved from the legacy system.
      setError(err.message);
    }
  };

  return (
    <div style={{ maxWidth: 640, margin: "40px auto", fontFamily: "sans-serif" }}>
      <h1>Employees</h1>

      <form onSubmit={handleCreate} style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <input
          placeholder="First name"
          value={form.first_name}
          onChange={(e) => setForm({ ...form, first_name: e.target.value })}
        />
        <input
          placeholder="Last name"
          value={form.last_name}
          onChange={(e) => setForm({ ...form, last_name: e.target.value })}
        />
        <input
          placeholder="Department"
          value={form.department}
          onChange={(e) => setForm({ ...form, department: e.target.value })}
        />
        <button type="submit">Add</button>
      </form>

      {error && <p style={{ color: "crimson" }}>{error}</p>}

      <table width="100%" cellPadding={6}>
        <thead>
          <tr style={{ textAlign: "left", borderBottom: "1px solid #ddd" }}>
            <th>Name</th>
            <th>Department</th>
            <th>Status</th>
            <th>Salary</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {employees.map((emp) => (
            <tr key={emp.id} style={{ borderBottom: "1px solid #eee" }}>
              <td>{emp.first_name} {emp.last_name}</td>
              <td>{emp.department}</td>
              <td>{emp.status}</td>
              <td>{emp.salary ?? "Pending"}</td>
              <td>
                <button onClick={() => handleDelete(emp.id)}>Remove</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
