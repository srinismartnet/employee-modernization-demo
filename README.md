# Employee HR Modernization Demo
### Legacy .NET → FastAPI + React, using an AI memory/context pipeline

This is a small, runnable demo of the pattern from the LinkedIn post: instead
of pasting a legacy codebase into an AI chat and hoping for the best, you
build two separate layers *before* you generate any new code, then retrieve
from them per-task.

```
employee-modernization-demo/
├── legacy-app/              # the "before" - legacy .NET Employee CRUD
│   ├── Employee.cs
│   ├── EmployeeController.cs
│   └── EmployeeRepository.cs
│
├── ai-context/               # the pipeline: memory + retrievable context
│   ├── memory/
│   │   └── project-memory.md # long-term memory (see below)
│   ├── chunks/
│   │   ├── chunks_index.json # metadata for each legacy code chunk
│   │   └── *.txt              # the actual chunk content (retrieved on demand)
│   └── migrate_agent.py      # retrieval + prompt-building demo script
│
└── modern-app/               # the "after" - what the pipeline produces
    ├── backend/               # FastAPI, generated to match project-memory.md
    │   └── app/
    │       ├── models.py
    │       ├── schemas.py
    │       ├── crud.py
    │       └── main.py
    └── frontend/               # React, calls the FastAPI backend
        └── src/
            ├── api.js
            └── EmployeeApp.jsx
```

## The core idea: memory vs. context are two different things

**Memory** (`ai-context/memory/project-memory.md`)
A small, structured, hand-curated-by-AI file: entities, business rules,
API contracts, decisions already made, migration progress. It's loaded
**in full** on every task, because it's cheap — a few hundred tokens no
matter how big the legacy app is.

**Context** (`ai-context/chunks/`)
The actual legacy source code, broken into small chunks with tags and a
one-line summary each (`chunks_index.json`). This is **never** loaded in
full. For a given task ("migrate the delete endpoint"), you retrieve only
the 2-3 chunks that are actually relevant, using keyword or embedding
similarity search.

This split is what keeps token usage flat as the codebase grows. A prompt
to migrate one endpoint costs the same whether the legacy app is 5,000
lines or 500,000 — because you're retrieving by relevance, not loading
by proximity.

## How the pipeline actually ran for this demo

1. **Ingest & chunk** — `legacy-app/*.cs` was broken into 6 chunks
   (`chunks_index.json`), each tagged with what it covers (`hr-rule`,
   `soft-delete`, `salary`, etc.) and given a one-line summary.

2. **Extract memory** — reading through the legacy controller surfaced 6
   business rules that exist **only in code**, never in a spec doc (e.g.
   "HR employees can never be deleted via the API" — added after a 2015
   incident, mentioned only in a code comment). These went into
   `project-memory.md` as a numbered, traceable list.

3. **Retrieve per task** — `migrate_agent.py` takes a task description,
   scores each chunk for relevance, pulls back only the top matches, and
   builds a prompt from `memory + retrieved chunks + task`. Run it
   yourself:
   ```bash
   cd ai-context
   python3 migrate_agent.py
   ```
   It prints which chunks it retrieved and the estimated prompt token
   count — try changing `example_task` at the bottom of the file to see
   different chunks get pulled in.

4. **Generate & validate** — the FastAPI backend in `modern-app/backend`
   is the actual output of following that process: every business rule in
   `crud.py` has a comment pointing back to its rule number in
   `project-memory.md`, so the lineage from legacy code → rule → new code
   is traceable, not a black box.

5. **Update memory, not context** — once a module is migrated, you update
   `project-memory.md`'s progress log and API contract section. You do
   **not** re-summarize the legacy code again next time — memory persists
   across sessions so you're not re-paying that cost.

## Running it

**Backend**
```bash
cd modern-app/backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend** (needs a Vite/React scaffold — this demo only includes the
component + API client, drop them into a `npm create vite@latest` app)
```bash
cd modern-app/frontend
npm create vite@latest . -- --template react
# then copy src/api.js and src/EmployeeApp.jsx in, render <EmployeeApp /> from App.jsx
npm install && npm run dev
```

**Retrieval demo (no servers needed)**
```bash
cd ai-context
python3 migrate_agent.py
```

## What's deliberately simplified

- Retrieval uses keyword/tag scoring, not real embeddings — swap
  `score_chunk()` in `migrate_agent.py` for a vector similarity search
  (e.g. `sentence-transformers` + a vector DB like Chroma/pgvector) in a
  real project. The rest of the flow — load memory, retrieve, prompt,
  generate, update memory — doesn't change.
- The actual Claude API call is commented out in `migrate_agent.py` so
  the demo runs with zero API keys or network calls. The comment shows
  exactly where it plugs in.
- One entity (Employee) is used to keep the demo runnable end-to-end.
  The same chunk-and-tag structure scales to many entities — you'd just
  have more files in `ai-context/chunks/` and more sections in
  `project-memory.md`.
