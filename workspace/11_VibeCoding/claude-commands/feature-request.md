---
description: Implement a Feature Request (check FR doc → GitHub issue → branch → implement with commits → PR → push)
argument-hint: <FR document path or name, e.g. FR_INSTAGRAM_REEL_IMPORT>
---

# Feature Request

FR document: `$ARGUMENTS`

Run the steps below in order. If any step fails or a stop condition is hit, stop immediately and report using the step 7 format.

## 0. Preconditions

### 0-1. Resolve the FR document

- Resolve `$ARGUMENTS` to a file. Accept a full path, a file name, or a name without `.md`; search `docs/feature/FR_*.md` first.
- If `$ARGUMENTS` is empty or no file matches, list the available `docs/feature/FR_*.md` files, ask the user which one to use, and stop.

### 0-2. GitHub access

Use the first one that works:

1. **GitHub MCP**: GitHub MCP tools (e.g. `mcp__github__*`) are available in this session.
2. **gh CLI**: `gh auth status` succeeds.

If neither works, stop and ask the user to connect the GitHub MCP:

```bash
claude mcp add --transport http github https://api.githubcopilot.com/mcp/ -H "Authorization: Bearer <GitHub PAT>"
```

- The PAT needs `repo` scope (or fine-grained: Issues and Pull requests read/write, Contents read/write).
- After adding it, the user must restart the session and run this command again.
- Never ask the user to paste the token into chat.

## 1. Check the FR document

Stop if any check below fails. Do not create an issue or branch in that case.

### 1-1. Implementation plan exists

- The plan is part of the FR document itself: the `## 9. 구현 계획` section (written by `/feature-doc`). There are no separate `PLAN_*.md` files.
- If the section is missing or has no change list (`9.2`) and work order (`9.4`), **stop**.
  - Output: `❌ No implementation plan. Add §9 구현 계획 to <FR path> (see /feature-doc), then run again.`

### 1-2. No open review items

Read the FR document, including §9. **Stop** if any of these is true:

- The status line (`> 상태:` / `> Status:`) is not approved. Approved means `승인`, `확정`, or `Approved`. Examples that stop: `제안`, `검토 대기`, `Draft`.
- The `결정 필요 사항` / `Open questions` section has an item with no final decision recorded.
- The document contains `TBD`, `TODO`, `미정`, `확인 필요`, or `결정 필요`.

When stopping, list each open item as `file:line — item`. Ask the user to resolve them and update the status, then run again.

### 1-3. Target repositories

- `frontend/` and `backend/` are **separate git repositories**:
  - `frontend/` → `AI-Campus-1st/Recipe-Frontend`
  - `backend/` → `AI-Campus-1st/Recipe-Backend`
- The workspace root is not a git repository.
- From the plan, decide which of them the work touches. Run every git step below inside each target folder, separately.
- For each target:
  - The working tree must be clean (`git status --porcelain` is empty). If it is not, stop and ask the user.
  - Read `git remote get-url origin` to get the `owner/repo` for GitHub calls.

## 2. Create GitHub issues

For each target repo, create one issue:

- **Title**: `[FR] <FR title>`. If both repos are targets, add the scope: `[FR][backend] ...`, `[FR][frontend] ...`.
- **Body**:
  - A summary of the FR (background and goal, 2–3 lines)
  - The FR's functional requirements (`FR-n`) that this repo implements
  - Acceptance criteria as a checklist (copied from the FR doc)
  - The path of the FR document (its §9 is the implementation plan)
- **Labels**: `enhancement` if it exists.
- When both repos are targets, add a link to the other repo's issue in each body.

Record each issue number for later steps.

## 3. Create the branch

In each target folder:

```bash
git switch main
git pull --ff-only
git switch -c feature/<issue#>-<short-kebab-slug>
```

Example: `feature/12-instagram-reel-import`

## 4. Implement (commit as you go)

- Follow the plan step by step. Follow the target folder's `CLAUDE.md` and existing code conventions.
- After each meaningful step (a plan step, or a self-contained piece that builds and passes tests), make a commit:
  - Run that module's checks before each commit, and only those it actually has:
    - backend: `uv run ruff check .`, `uv run mypy app`, `uv run pytest`
    - frontend: `pnpm lint`, `pnpm typecheck`, `pnpm test`
  - Do not commit with failing checks. Fix the failure first. If it cannot be fixed, stop and report.
  - Commit message in Conventional Commits format, with the issue reference:

    ```
    feat(<scope>): <what this step does>

    Refs #<issue#>
    ```

- Never commit `.env`, keys, or credentials (see `/github-init` step 5 for the check).
- If an assumption in the plan turns out wrong, stop and ask the user instead of inventing a new design.
- Update docs that the change affects, as `CLAUDE.md` scope rules require (e.g. `API_SPEC.md`, `ERD.md`).

## 5. Create the pull request

A PR needs the branch on GitHub, so push it first:

```bash
git push -u origin feature/<issue#>-<slug>
```

Create one PR per target repo:

- **Base**: `main`. **Head**: the feature branch.
- **Title**: `feat: <FR title>`
- **Body**:
  - `Closes #<issue#>`
  - A summary of what changed, grouped by plan step
  - Acceptance criteria as a checklist, checking off what is verified
  - How it was tested (commands run and their results)
  - Anything not done or not verified
  - The other repo's PR link, if both repos are targets

## 6. Push

- Push any commits made after the PR was opened (e.g. review fixes): `git push`.
- Confirm that the local and remote branches match: `git status -sb` shows no `ahead`.
- Never force push.

## 7. Report

```
## Feature Request Result: <FR title>
| Step | Result | Notes |
|---|---|---|
| FR check | ✅/❌ | plan: §9 present, open items: N |
| Issue | ✅/❌ | <repo>#<n> |
| Branch | ✅/❌ | feature/<n>-<slug> |
| Implementation | ✅/⚠️/❌ | N commits, checks: pass/fail |
| PR | ✅/❌ | <PR URL> |
| Push | ✅/❌ | up to date with origin |

### Commits
- <hash> <message>

### Not done / not verified
- ...
```

If the command stopped early, show the table up to the failed step and say what the user needs to do before running it again.
