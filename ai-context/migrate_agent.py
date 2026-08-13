"""
migrate_agent.py
-----------------
A minimal, dependency-light demo of the "memory + context retrieval"
pattern used for AI-assisted legacy migration.

Core idea:
  - MEMORY  (ai-context/memory/project-memory.md) is small, structured,
    and ALWAYS loaded in full. It's the AI's durable understanding of the
    project: entities, business rules, API contracts, decisions already made.
  - CONTEXT (ai-context/chunks/*) is the raw legacy source, broken into
    chunks with metadata. It is NEVER loaded in full. Only the chunks
    relevant to the current task are retrieved.

This keeps every migration prompt small and cheap, no matter how big the
legacy codebase is -- a 500k-line legacy app costs the same per-task tokens
as a 5k-line one, because retrieval scopes the context to the task.

Retrieval here uses simple keyword/tag scoring so the demo has zero
external dependencies. In a real project, swap `score_chunk()` for a
vector similarity search (e.g. embeddings + a vector DB) -- the rest of
the flow (load memory -> retrieve chunks -> build prompt -> call model
-> update memory) stays the same.
"""

import json
import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent
MEMORY_FILE = BASE_DIR / "memory" / "project-memory.md"
CHUNKS_INDEX = BASE_DIR / "chunks" / "chunks_index.json"
CHUNKS_DIR = BASE_DIR / "chunks"


def load_memory() -> str:
    """Memory is always loaded in FULL -- it's small by design."""
    return MEMORY_FILE.read_text()


def load_chunk_index() -> list:
    return json.loads(CHUNKS_INDEX.read_text())


def score_chunk(chunk: dict, query_terms: set) -> int:
    """
    Cheap relevance scoring: overlap between query terms and the chunk's
    tags + summary words. Swap this for cosine similarity over embeddings
    for real projects -- the interface (query -> ranked chunks) is the same.
    """
    text = " ".join(chunk["tags"]) + " " + chunk["summary"]
    text_words = set(re.findall(r"[a-z]+", text.lower()))
    return len(query_terms & text_words)


def retrieve_relevant_chunks(task_description: str, top_k: int = 3) -> list:
    query_terms = set(re.findall(r"[a-z]+", task_description.lower()))
    index = load_chunk_index()
    scored = [(score_chunk(c, query_terms), c) for c in index]
    scored = [sc for sc in scored if sc[0] > 0]
    scored.sort(key=lambda sc: sc[0], reverse=True)
    top = [c for _, c in scored[:top_k]]

    # Attach actual content only for the chunks we're keeping --
    # this is the step that avoids loading the whole codebase.
    for c in top:
        content_path = CHUNKS_DIR / f"{c['chunk_id']}.txt"
        c["content"] = content_path.read_text() if content_path.exists() else ""
    return top


def build_prompt(task_description: str, memory: str, chunks: list) -> str:
    chunk_blocks = "\n\n".join(
        f"### Legacy source: {c['source_file']} ({c['chunk_id']})\n"
        f"# {c['summary']}\n```\n{c['content']}\n```"
        for c in chunks
    )

    prompt = f"""You are migrating a legacy .NET Employee HR API to FastAPI (Python).

## Project memory (persistent rules -- always authoritative)
{memory}

## Retrieved legacy source relevant to this task
{chunk_blocks}

## Task
{task_description}

Generate the FastAPI implementation. Preserve every business rule listed
in the project memory above exactly. Do not invent new rules. If a rule
isn't covered by the retrieved source or memory, say so instead of guessing.
"""
    return prompt


def estimate_tokens(text: str) -> int:
    # Rough heuristic: ~4 chars per token.
    return len(text) // 4


def run(task_description: str):
    memory = load_memory()
    chunks = retrieve_relevant_chunks(task_description)

    print(f"Task: {task_description}")
    print(f"Retrieved {len(chunks)} chunk(s): "
          f"{[c['chunk_id'] for c in chunks]}")

    prompt = build_prompt(task_description, memory, chunks)
    print(f"\nEstimated prompt tokens: ~{estimate_tokens(prompt)}")
    print("(compare: loading the full legacy repo instead of retrieval "
          "would scale this with codebase size, not task size)")

    # --- Where the actual model call happens ---
    # Swap in your Anthropic API call here, e.g.:
    #
    # import anthropic
    # client = anthropic.Anthropic()
    # response = client.messages.create(
    #     model="claude-sonnet-4-6",
    #     max_tokens=2000,
    #     messages=[{"role": "user", "content": prompt}],
    # )
    # generated_code = response.content[0].text
    #
    # For this demo we just print the prompt that WOULD be sent.
    return prompt


if __name__ == "__main__":
    example_task = (
        "Migrate the delete employee endpoint, including the HR department "
        "protection rule and the soft-delete-only requirement."
    )
    final_prompt = run(example_task)
    print("\n----- PROMPT PREVIEW (first 800 chars) -----")
    print(final_prompt[:800])
