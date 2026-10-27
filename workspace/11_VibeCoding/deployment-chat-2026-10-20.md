# Deployment chat log (2026-10-20)

Deploying recipe_app with the DB on Supabase, the backend (BE) on Render and the frontend (FE) on Vercel.
User messages are quoted as written; assistant replies are lightly condensed, and actions taken through tools are summarized in *italics*.

---

## 1. Planning the deployment

**User:** 배포를 진행하려고 해. db는 supabase에, FE는 vercel에, BE는 render를 사용할거야. 관련해서 진행 절차를 알려줘

*Looked at the project: FE is Next.js 16 (pnpm), BE is FastAPI + uv with a Dockerfile and SQLAlchemy asyncpg, the schema lives in `db/init.sql`, and `frontend/` and `backend/` are separate GitHub repos (`AI-Campus-1st/Recipe-Frontend`, `AI-Campus-1st/Recipe-Backend`).*

**Assistant:**

### 0. Decide this first: how login works
`backend/app/core/config.py` refuses to start with `APP_ENV=production` and `AUTH_MODE=dev`. The frontend has no Supabase login yet, so with `AUTH_MODE=supabase` every API call returns 401.

| Option | Settings | Notes |
|---|---|---|
| **A. Demo / test deployment** | `APP_ENV=staging`, `AUTH_MODE=dev` | Every user shares one dev account |
| B. Real production | `APP_ENV=production`, `AUTH_MODE=supabase` | Needs frontend login built first |

### 1. Supabase (DB)
1. Create a project and save the DB password.
2. Run `db/init.sql` in the SQL Editor. With option A, also run `db/seed.sql`, which inserts the dev user into `auth.users`.
3. Use the **Session pooler** (port 5432) for the connection string.
   - The direct connection only works over IPv6, which Render can't reach.
   - The Transaction pooler (6543) breaks asyncpg's prepared statements.
   - Format: `postgresql+asyncpg://postgres.<ref>:<password>@<pooler-host>:5432/postgres`

### 2. Render (BE)
- New Web Service from the `Recipe-Backend` repo, Docker runtime, health check at `/health`.
- Env vars: `APP_ENV`, `AUTH_MODE`, `DEV_USER_ID`, `PORT=8000`, `DATABASE_URL`, `SUPABASE_URL`, `CORS_ORIGINS`, `ADMIN_API_KEY`, and the AI keys.
- Free plan: the service sleeps after 15 minutes idle. `BackgroundTasks` jobs are lost if it sleeps mid-job, and Instagram downloads are often blocked from data center IPs.

### 3. Vercel (FE)
- Import `Recipe-Frontend` and set `NEXT_PUBLIC_API_BASE_URL` to the Render URL. `NEXT_PUBLIC_*` values are baked in at build time, so change one means redeploy.

### 4. Connect them
- Add the Vercel domain to `CORS_ORIGINS` on Render. Preview deployments get different domains, so CORS blocks them.

### 5. (Optional) Admin page
- `admin/` isn't in a git repo, so deploying it needs a separate repo and a second Vercel project.

---

## 2. Doing it with MCP and CLIs

**User:** mcp나 cli 활용해서 연동 진행하고 싶어

*Checked tools: Node, pnpm, npx and gh are installed; the supabase, vercel and render CLIs are not. Found Supabase, Render and Vercel connectors in the MCP registry and suggested connecting them.*

**Assistant:**

| Service | Tool | What it can do |
|---|---|---|
| Supabase | Supabase MCP | Create the project, apply migrations, look up connection info |
| Render | Render MCP | Create the web service, set env vars, check deploys and logs |
| Vercel | Vercel CLI (`npx vercel`) | Link the project, set env vars, deploy |

What you need to do: connect the three connectors, log in to the Vercel CLI, and connect GitHub in the Render dashboard.

---

## 3. Logging in

**User:** vercel login, render github 연결하는거 띄워줘

*Opened a terminal tab and ran `npx vercel login`. PowerShell's execution policy blocked `npx.ps1`, so it was rerun as `npx.cmd vercel login`, which needs no policy change. Opened the Render dashboard Git Credentials page in the browser pane.*

**Assistant:** Type `y` at the install prompt in the terminal and finish the login in the browser. In the Render dashboard, sign in and connect GitHub under Git Credentials, allowing access to the `AI-Campus-1st` org.

---

## 4. Supabase setup

**User:** 설정완료

*Confirmed the Vercel CLI login succeeded. The Supabase org `ai-campus` already had an empty project, `recipe-app-test` (ap-southeast-1), which the local backend uses for Auth. A new project would cost $0/month.*

**Assistant (question):** Create a new Seoul project or reuse `recipe-app-test`?
**User (answer):** Reuse recipe-app-test

*Applied `db/init.sql` as migration `init_schema`. Inserted the dev user (`f72a20a5-9840-4409-b272-220d32a472a1`) into `auth.users`. Checked: 21 rows in `units`.*

## 5. Creating the Render service

*Created the Render web service `recipe-api` with Docker, region singapore (the same as the DB), the free plan, and branch `main`, setting the non-secret env vars only:*
`APP_ENV=staging`, `TIMEZONE=Asia/Seoul`, `PORT=8000`, `AUTH_MODE=dev`, `DEV_USER_ID`, `SUPABASE_URL`, `CORS_ORIGINS`, `LLM_PROVIDER`, `LLM_MODEL`, `LLM_REASONING_EFFORT`, `GEMINI_MODEL`
→ URL: `https://recipe-api-nr4q.onrender.com`

*Creating the Vercel Git project failed: the Vercel account had no GitHub login connection. Opened the Vercel Authentication settings page.*

---

## 6. How to enter the secrets on Render

**User:** vercel에 github 연동은 했어. 근데 render에 secret은 어떤 양식으로 어떻게 넣으면 돼?

*Retrying the Vercel project failed with `repo_not_found`: the Vercel GitHub App wasn't installed on the org.*

**Assistant:**

Where: recipe-api → Environment → Edit → Add Environment Variable. Type the key and the value in separate fields with no quotes or spaces, then click Save, rebuild, and deploy.

| Key | Value |
|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://postgres.twpbxktvqoceaynfltzc:<DB password>@<pooler host>:5432/postgres` |
| `OPENAI_API_KEY` / `GEMINI_API_KEY` / `YOUTUBE_API_KEY` | Same values as local `backend/.env` |
| `ADMIN_API_KEY` | A new random string; blank disables the admin API |
| `SUPABASE_JWT_SECRET` | Same as local `.env` (optional in dev mode) |

- Don't paste the local `.env` as is: lines like `DATABASE_URL=localhost` and `APP_ENV=local` would overwrite the values already set.
- Building `DATABASE_URL`: in Supabase, go to Connect → Session pooler, copy the string, change `postgresql://` to `postgresql+asyncpg://`, and fill in the password. URL-encode special characters.
- Vercel: install the Vercel GitHub App on the `AI-Campus-1st` org at github.com/apps/vercel/installations/new.

---

## 7. Vercel deploy, CORS and verification

**User:** I entered the secrets on Render and installed the Vercel GitHub App on the AI-Campus-1st org. Continue with the Vercel deploy and the CORS setup.

*Vercel Git linking failed with `repo_owned_by_org`: the Hobby plan can't link a private repo owned by an org. Switched to deploying from the local `frontend/` folder with the CLI:*

```bash
npx vercel link --yes --project recipe-frontend --scope jason-5948
npx vercel env add NEXT_PUBLIC_API_BASE_URL production   # https://recipe-api-nr4q.onrender.com
npx vercel env add NEXT_PUBLIC_API_BASE_URL preview
npx vercel deploy --prod --yes --scope jason-5948
```

*Backend check: `/health` and `/recipes` both returned 200, so the DB connection works.
Updated `CORS_ORIGINS` on Render to `["https://recipe-frontend-phi.vercel.app","https://recipe-frontend-jason-5948.vercel.app","http://localhost:3000","http://localhost:3100"]`. After the redeploy, confirmed the `access-control-allow-origin` header.
Browser check: the deployed site's calls to `/meals/today` and `/shopping-lists/...` returned 200, and the home screen rendered.
Removed the `.env*` line that Vercel added to `frontend/.gitignore`, because it would stop git from tracking `.env.example`. Kept only `.vercel`.*

**Assistant: summary**

| | URL | Status |
|---|---|---|
| Frontend (Vercel) | https://recipe-frontend-phi.vercel.app | Home loads with data from the API |
| Backend (Render) | https://recipe-api-nr4q.onrender.com | `/health` and `/recipes` return 200 |
| DB (Supabase) | `recipe-app-test` | Schema, units data and dev user in place |

Things to know:
- **The frontend doesn't redeploy on push.** Because of the Hobby plan limit, redeploy from `frontend/` with `npx vercel deploy --prod --scope jason-5948`. The backend redeploys automatically when you push to `main`.
- `AUTH_MODE=dev` is a demo setup, so everyone shares the same account.
- On the Render free plan, the first request after sleeping takes 30–60 seconds, and background jobs can be lost.
- Not tested yet: recipe import and the AI features on the deployed site.
- Uncommitted: the `.vercel` line added to `frontend/.gitignore`.
- The admin page isn't deployed.
