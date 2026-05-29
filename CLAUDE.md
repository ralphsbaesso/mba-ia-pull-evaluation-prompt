# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project purpose

A course challenge ("MBA IA — Pull, Otimização e Avaliação de Prompts"). The goal is to pull a deliberately bad prompt (`leonanluppi/bug_to_user_story_v1`) from LangSmith Prompt Hub, refactor it into a v2 that converts bug reports to user stories, push the optimized version back to LangSmith, and run an evaluation that must score >= 0.9 on **all five** metrics (Helpfulness, Correctness, F1-Score, Clarity, Precision) — not just the average.

The prompt v1 in `prompts/bug_to_user_story_v1.yml` is intentionally low-quality (duplicate `{bug_report}` in system + user, vague instructions, no persona, no examples). v2 must apply **Few-shot Learning (mandatory)** plus at least one other technique (CoT, ToT, SoT, ReAct, or Role Prompting), and metadata must list **at least 2** techniques in `techniques_applied`.

## Commands

**Prefer the Taskfile.** Use `task <target>` whenever an equivalent exists — only fall back to raw `python` calls for steps that don't have a task yet.

```bash
# Primary workflow — via Taskfile (run from repo root)
task setup     # creates venv, installs deps, copies .env.example → .env (idempotent)
task pull      # pulls v1 → prompts/bug_to_user_story_v1.yml (depends on setup)
task --list    # lists every available task
```

```bash
# No task yet — run via the venv's Python
./venv/bin/python src/push_prompts.py   # pushes prompts/bug_to_user_story_v2.yml → LangSmith Hub (PUBLIC)
./venv/bin/python src/evaluate.py       # pulls v2 from Hub, scores against datasets/bug_to_user_story.jsonl
```

```bash
# Tests (run inside the venv)
./venv/bin/pytest tests/test_prompts.py
./venv/bin/pytest tests/test_prompts.py::TestPrompts::test_prompt_has_few_shot_examples -v
```

`evaluate.py` always pulls the v2 prompt **from LangSmith Hub** (not local YAML) — so iteration loop is: edit YAML → `push_prompts.py` → `evaluate.py`. Skipping push means evaluating the previous version.

## Architecture

**Single source of truth = LangSmith Hub.** Local YAML is the editing surface; the Hub is what gets evaluated. This is why the loop requires push between edits.

**Provider abstraction** lives in `src/utils.py::get_llm` / `get_eval_llm`. The `LLM_PROVIDER` env var switches between OpenAI (`gpt-4o-mini` / `gpt-4o`), Google (`gemini-2.5-flash`), and DeepSeek (`deepseek-v4-flash`, OpenAI-compatible via `base_url=https://api.deepseek.com`). All scripts call `get_llm()` — never instantiate `ChatOpenAI` / `ChatGoogleGenerativeAI` directly.

**Metrics pipeline** (`src/metrics.py` + `src/evaluate.py`):
- 3 base metrics (`f1_score`, `clarity`, `precision`) are computed per-example via LLM-as-judge.
- 2 derived metrics: `helpfulness = (clarity + precision) / 2`, `correctness = (f1 + precision) / 2`. Pass criterion is all 5 ≥ 0.9. Improving `precision` lifts both derived metrics.

**Username gate.** `evaluate.py` constructs the prompt name from `USERNAME_LANGSMITH_HUB` env var (e.g. `{username}/bug_to_user_story_v2`). Without it, evaluation aborts.

**YAML prompt schema** expected by `utils.validate_prompt_structure` and the tests: top-level key (e.g. `bug_to_user_story_v2`) containing `description`, `system_prompt`, `user_prompt`, `version`, `techniques_applied` (≥2 entries), plus `tags`. Templates use LangChain variable syntax (`{bug_report}`).

## Files that are off-limits

`src/evaluate.py`, `src/metrics.py`, `src/utils.py`, and `datasets/bug_to_user_story.jsonl` are stated as "ready — do not alter" in the README. If a change to these seems necessary, flag it rather than editing silently.

## Files to implement (skeletons exist)

- `src/pull_prompts.py` — body of `pull_prompts_from_langsmith()` and `main()`; use `langchain.hub.pull` + `utils.save_yaml`.
- `src/push_prompts.py` — body of `push_prompt_to_langsmith()`, `validate_prompt()`, `main()`; use `langchain.hub.push` with `ChatPromptTemplate` built from the YAML, push **public** (`is_public=True`).
- `prompts/bug_to_user_story_v2.yml` — create from scratch.
- `tests/test_prompts.py` — six tests listed in README §5 (currently all `pass`).
