---
description: GitHub setup (git init → connect remote → security check → .gitignore → initial commit/push → report)
argument-hint: <github-repo-url>
allowed-tools: Bash(git:*), Read, Edit, Write, Grep, Glob
---

# GitHub Setup

Repository URL: `$ARGUMENTS`

Run the steps below in order. If any step fails, stop immediately and report the cause using the step 6 format.

## 0. Validate arguments

- If `$ARGUMENTS` is empty, **do nothing and fail**.
  - Output: `❌ No repository URL provided. Usage: /github-init https://github.com/<owner>/<repo>.git`
  - Ask the user for the repository URL and stop.
- If the URL is not in the form `https://github.com/<owner>/<repo>(.git)` or `git@github.com:<owner>/<repo>(.git)`, fail the same way and ask for a valid URL.

## 1. git init

- If the directory is already a git repository (`git rev-parse --is-inside-work-tree`), skip init and note it.
- Otherwise run `git init -b main`.

## 2. Connect remote

- If `origin` does not exist, run `git remote add origin <url>`.
- If `origin` already exists with a different URL, do not overwrite it; ask the user to confirm.
- Check access with `git ls-remote origin`. If it fails (repository missing or no permission), fail and ask the user for a valid URL or to check permissions.

## 3. Security check and refactor

Search the whole source tree with Grep, excluding `node_modules/`, `target/`, `dist/`, `build/`, `.next/` and `.git/`.

Patterns to look for:
- Keys/tokens: `sk-[A-Za-z0-9]{20,}`, `sk-ant-`, `AKIA[0-9A-Z]{16}`, `ghp_[A-Za-z0-9]{36}`, `AIza[0-9A-Za-z_-]{35}`, `xox[baprs]-`, `-----BEGIN .*PRIVATE KEY-----`
- Hardcoded assignments: `(api[_-]?key|secret|token|password|passwd|client[_-]?secret)\s*[:=]\s*["'][^"']+["']` (case-insensitive)
- Connection strings: `postgres(ql)?://[^:]+:[^@]+@`, `mysql://`, `mongodb(\+srv)?://`
- Existing `.env*` files, `*.pem`, `*.key`, `credentials*.json`

For each finding:
1. **Replace the value with an environment variable reference**, following each module's existing convention.
   - Rust backend: `std::env::var("NAME")` or the existing config module
   - Next.js: `process.env.NEXT_PUBLIC_NAME` for client-exposed values; server-only secrets go in `process.env.NAME` without the prefix
   - Vite: `import.meta.env.VITE_NAME` (client-exposed values only)
   - Real secrets must never be in client code; if one is, flag it in the report.
   - docker-compose: `${NAME}` substitution plus `env_file`
2. Move the real value to that module's `.env` (this file is not committed).
3. Create or update a `.env.example` next to it with the key names only and empty values.
4. For development dummy values (e.g. `postgres:postgres@localhost`, seed data), decide whether to replace them and record the reasoning in the report.

After refactoring, confirm the build still works where possible (`cargo check`, `npm run build`, etc., only for what the module has).

## 4. .gitignore

Create or update the root `.gitignore` (keep existing content, do not add duplicates). Include at least:

```gitignore
# env / secrets
.env
.env.*
!.env.example
*.pem
*.key
credentials*.json

# deps / build
node_modules/
dist/
build/
target/

# OS / editor
.DS_Store
Thumbs.db
.vscode/
.idea/

# Claude local settings
.claude/settings.local.json
```

If any secret file is already tracked by git, untrack it with `git rm --cached <file>`.

## 5. Initial commit and push

1. `git add -A`
2. **Re-check before committing**: if `git diff --cached --name-only` contains a `.env` file (other than `.env.example`) or a key file, or if the staged content still matches any step 3 pattern, do not commit; stop and report.
3. `git commit -m "chore: initial commit"`
4. `git push -u origin main`
   - If the push is rejected because the remote already has commits, **do not force push**. Stop and ask the user how to proceed (pull/rebase, or use an empty repository).

## 6. Report

Report in this format:

```
## GitHub Setup Result
| Step | Result | Notes |
|---|---|---|
| git init | ✅/⏭️/❌ | |
| Connect remote | ✅/❌ | <url> |
| Security check | ✅/⚠️ | N found / N fixed |
| .gitignore | ✅ | rules added |
| Commit/push | ✅/❌ | <commit hash>, <branch> |

### Security check details
- `file:line` — what was found (value masked) → action taken (env var name)

### Files created/modified
- ...

### Follow-up needed
- If any key was already exposed, **revoke (rotate) that key**
- Teammates should copy `.env.example` to `.env` and fill it in
```

Never print secret values in the report or any output; mask everything except the first 4 characters (`sk-a****`).
