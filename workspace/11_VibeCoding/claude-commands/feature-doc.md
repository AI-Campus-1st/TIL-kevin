---
description: Write a Feature Request document with its implementation plan (docs/feature/FR_*.md) from a feature idea
argument-hint: <feature description, URLs or sample inputs to check>
---

# Feature Request Document

Request: `$ARGUMENTS`

Write a Feature Request (FR) document that includes its implementation plan. Do not change code or other documents; this command only writes the one new file. Implementing the FR is done later with `/feature-request <FR name>`.

If `$ARGUMENTS` is empty, ask the user what feature to write up and stop.

## 1. Understand the current state

Read only what the feature touches:

- Product docs: `docs/product/FEATURE_SPEC.md` (find the related `F-nn`), and other `docs/product/*.md` if relevant.
- Existing FRs: `docs/feature/FR_*.md` — avoid duplicates; if one already covers this, tell the user and stop.
- Target modules: `backend/`, `frontend/`, `admin/` — their `CLAUDE.md`, the related logic/spec docs (e.g. `backend/logics/*.md`, `backend/API_SPEC.md`, `backend/ERD.md`), and the code the feature will change (entry points, services, adapters, schemas, tests and their fakes).
- Note current decisions and policies the feature must follow or would change (supported sources, enums, error messages, config keys).

## 2. Pre-validate (when possible)

If the feature depends on an external service, library or input format, check it before writing:

- Run small experiments with the URLs or sample inputs the user gave (fetch, parse, call the API).
- Use a scratch virtualenv or scratchpad, not the project's dependencies. Read keys from the module's `.env` without printing them.
- Put downloaded or fetched files in a new empty temp directory.
- Record what worked, what failed (with the exact error), timing and token cost. These go in the FR's pre-validation section.
- If validation needs something you cannot do (paid call, missing key, login), say so in the FR instead of guessing.

## 3. Write the FR document (with the implementation plan)

Path: `docs/feature/FR_<UPPER_SNAKE_NAME>.md`. The FR and its implementation plan go in this **one file**; do not create `PLAN_*.md` files in module folders. Write in Korean, matching the style of existing docs. Sections:

```markdown
# Feature Request: <기능 이름>

> 작성일: <YYYY-MM-DD>
> 상태: 제안 (검토 대기)
> 관련: <related docs, e.g. `docs/product/FEATURE_SPEC.md` F-01>

## 1. 배경            — current limitation and why the feature is needed
## 2. 목표 / 비목표    — what is in scope, and what is explicitly out of scope
## 3. 사용자 시나리오  — numbered steps from the user's point of view
## 4. 기능 요구사항    — FR-1, FR-2, ... each testable; tables for rules, inputs, failure cases
## 5. 비기능 요구사항  — time, cost, security, prompt injection, logging, limits
## 6. 사전 검증 결과   — table from step 2 (omit only if nothing could be validated, and say why)
## 7. 결정 필요 사항   — | # | 항목 | 제안 | 대안 | — every open choice, with a recommended option
## 8. 수용 기준        — checklist (- [ ]) that a reviewer can verify

---

## 9. 구현 계획

> 전제: <which §7 options this plan assumes>. 결정 사항 확정 후 착수
> 대상: <target modules, e.g. `backend/`, and what each one changes>

### 9.1 처리 흐름   — text diagram of the new flow
### 9.2 변경 파일   — | 영역 | 파일 | 변경 | — every file to add or change, incl. DB, config, deps, tests, docs
### 9.3 단계별 작업 — per layer (#### 9.3.n): signatures, short code sketches, error mapping, config defaults
### 9.4 작업 순서   — | # | 작업 | 완료 기준 | — small steps, each committable with passing checks
### 9.5 위험과 대응 — | 위험 | 영향 | 대응 |
### 9.6 테스트      — unit (with fakes, no live calls), API, and manual live checks
### 9.7 문서 갱신   — | 문서 | 내용 | — docs that must change when the feature lands
```

Rules for §1–§8:

- Status is always `제안 (검토 대기)`. Only the user approves it.
- Every requirement must be concrete: exact URL patterns, field names, messages, limits, defaults.
- Follow existing decisions. If the feature must change one, put it in §7 instead of deciding it.
- Put risks such as terms of service, blocking, cost and data retention in §5 or §7.

Rules for §9:

- Use real file paths, class and function names from the codebase. Do not invent modules when an existing one fits.
- Follow each target module's `CLAUDE.md` (layering, adapters, config, testing rules).
- Include DB migration steps when enums or tables change (`db/init.sql`, existing dev DB).
- If several modules are involved, cover all of them in the same §9 and label each file and step with its module.
- Keep §9 consistent with §4. Each FR-n should map to plan steps and tests.

## 4. Report

Keep it short:

- Link to the FR file.
- Pre-validation results in one or two lines.
- The §7 decisions the user needs to make, as a short list.
- Next step: approve the FR (set `상태: 승인`, resolve §7), then run `/feature-request <FR name>`.
