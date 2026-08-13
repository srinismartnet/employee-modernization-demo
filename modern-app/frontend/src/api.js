const BASE_URL = "http://localhost:8000";

export async function getEmployees() {
  const res = await fetch(`${BASE_URL}/employees`);
  return res.json();
}

export async function createEmployee(employee) {
  const res = await fetch(`${BASE_URL}/employees`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(employee),
  });
  if (!res.ok) throw new Error((await res.json()).detail);
  return res.json();
}

export async function updateEmployee(id, employee) {
  const res = await fetch(`${BASE_URL}/employees/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(employee),
  });
  if (!res.ok) throw new Error((await res.json()).detail);
  return res.json();
}

export async function deleteEmployee(id) {
  const res = await fetch(`${BASE_URL}/employees/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error((await res.json()).detail);
  return res.json();
}
