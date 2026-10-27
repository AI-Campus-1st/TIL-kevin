---
description: Merge reviewed feature PRs (review fixes → merge → update local main → restart local Docker → report)
argument-hint: <review notes, e.g. "frontend: drop X; backend: merge as is">
---

# Merge

Review notes: `$ARGUMENTS`

Run the steps below in order. If any step fails or a stop condition is hit, stop immediately and report using the step 7 format.

## 0. Preconditions

- GitHub access: `gh auth status` succeeds (GitHub CLI is at `C:\Program Files\GitHub CLI`; add it to `PATH` if `gh` is not found). If not, stop and ask the user to run `gh auth login`.
- Repositories (separate git repos; the workspace root is not one):
  - `frontend/` → `AI-Campus-1st/Recipe-Frontend`
  - `backend/` → `AI-Campus-1st/Recipe-Backend`
- For each repo, find the open PR to merge: the PR for the current feature branch (`gh pr view`), or `gh pr list --state open`.
  - If a repo has no open PR, skip it and note that in the report.
  - If there is more than one candidate and the notes do not say which, stop and ask.
- The user must have said the review is done. A PR with requested changes, or failing checks, is not merged; stop and report it.

## 1. Apply review fixes (only what the notes ask for)

For each repo the notes give changes for:

1. Work on the PR's feature branch (`git switch <branch>`). The working tree must be clean first.
2. Make only the requested changes. Update the docs they affect, following `CLAUDE.md` scope rules. Workspace root docs (`docs/`, `db/`) are not part of either repo; edit them, but say in the report that they are not committed.
3. Run that module's checks and only commit if they pass:
   - backend (inside the container): `docker compose exec -T api sh -c 'ruff check . && ruff format --check . && mypy app && pytest -q'`
   - frontend: `pnpm lint`, `pnpm typecheck`, `pnpm test`
4. Commit in Conventional Commits format with the issue reference (`Refs #<issue#>`), then `git push`. Never force push.
5. Update the PR body: move the fixed item out of "Not done", and add what changed in the review.

## 2. Merge the PRs

For each PR:

1. Check `gh pr view <n> --json state,mergeable,mergeStateStatus`. Merge only when it is `OPEN`, `MERGEABLE`, `CLEAN`. On a conflict, stop and ask; never use `--admin` to bypass rules.
2. `gh pr merge <n> --merge` (a merge commit keeps each step's commits).
3. Confirm the PR is `MERGED` and that the linked issue (`Closes #n`) is `CLOSED`.

When frontend and backend PRs belong together, merge the backend first if the frontend depends on a new API. Otherwise the order does not matter.

## 3. Update local branches

In each merged repo folder:

```bash
git switch main
git pull --ff-only
```

- Confirm `git status -sb` shows `main...origin/main` with nothing ahead or behind, and that the feature branch appears in `git branch --merged main`.
- Do not delete local or remote branches unless the user asks.

## 4. Restart local Docker (when backend was merged)

From the workspace root:

```bash
docker compose up -d --build -V
```

- `-V` renews the api container's anonymous `/app/.venv` volume, so new dependencies from the image are used. The DB keeps its data in the named `pgdata` volume.
- **Schema changes**: `db/init.sql` only runs on a fresh DB. If the merged change edited `init.sql`, apply the equivalent **non-destructive** statement to the existing dev DB (e.g. `alter type ... add value if not exists ...`, `alter table ... add column if not exists ...`). Never run `docker compose down -v` or drop data without asking the user.
- Verify:
  - `docker compose ps` shows both services up and `db` healthy
  - `curl http://localhost:8000/docs` returns `200`
  - New dependencies import inside the container
  - A smoke request for the new feature that writes nothing (e.g. a validation error case)

## 5. Frontend after merge

- Nothing to restart for the frontend (`pnpm dev` is run by the user). If `package.json` changed, run `pnpm install`.

## 6. Clean up

- Confirm no `.env`, keys, or credentials were committed in the merged range (`git diff <base>..main --name-only`).

## 7. Report

```
## Merge Result
| Step | Result | Notes |
|---|---|---|
| Review fixes | ✅/⏭️/❌ | <repo>: <commit hash> <message> |
| Merge | ✅/❌ | <repo>#<pr> → <merge commit> (issue #<n> closed) |
| Local main | ✅/❌ | <repo>: up to date with origin |
| Local Docker | ✅/⏭️/❌ | build, schema change applied, health checks |

### Not committed (workspace root)
- ...

### Not done / not verified
- ...
```

If the command stopped early, show the table up to the failed step and say what the user needs to do before running it again.
