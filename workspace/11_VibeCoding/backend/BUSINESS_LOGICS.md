# Business Logics

> 근거: `frontend/PLAN.md` §6 API 계약, `frontend/mocks/service.ts`·`handlers.ts`·`fixtures.ts`(mock 구현), `docs/product/FEATURE_SPEC.md`, `docs/product/TECH_STACK.md`
> 목적: 프론트엔드가 MSW mock으로 대신하고 있는 로직 중 **실제 백엔드(FastAPI)가 구현해야 하는 비즈니스 로직**을 4개 영역으로 분류한다.

외부 서비스 연동 로직 기획 문서 (`logics/`)

| 문서 | 내용 |
|---|---|
| [`logics/RECIPE_ANALYSIS.md`](logics/RECIPE_ANALYSIS.md) | 수집 레시피 분석 (출처별): Gemini 유튜브 영상 분석·댓글 보완, 웹페이지 구조화, 재료·단위 정리 |
| [`logics/MEAL_RECOMMENDATION.md`](logics/MEAL_RECOMMENDATION.md) | 자동 식단 추천: 저장 레시피 기반 주 레시피 선정, 곁들임 레시피 선정 |
| [`logics/UNIT_CONVERSION.md`](logics/UNIT_CONVERSION.md) | 단위체계 변환: 수량 파싱, 단위 정규화, 인분 환산, 합산, 표시 |
| [`logics/PREP_SUBSTITUTE_BASE_DATA.md`](logics/PREP_SUBSTITUTE_BASE_DATA.md) | [사전 작업] 대체 재료 베이스 데이터 구축 (런타임 로직 아님) |

| 영역 | 핵심 내용 | 관련 API |
|---|---|---|
| 1. 크롤링 | 레시피 URL 본문 수집, SSRF 방어, 유튜브 `video_id`·만개의레시피 레시피 ID 중복 확인, 비동기 수집 작업 | `POST /recipes/import`, `/retry`, `/revision-requests` |
| 2. AI 연동 분석 | 레시피 구조화(유튜브: Gemini 영상 분석 → 댓글 보완), 식단 추천·변경, 곁들임 추천 (대체 재료는 사전 작업 베이스 데이터) | `/recipes/import`, `/meal-plans/generate`, `/regenerate` |
| 3. 3rd party API | LLM 공급자, Gemini API, YouTube Data API, Supabase Auth/DB, 쿠팡 검색 URL | 전체 |
| 4. CRUD | 레시피·식단·조리 기록·장보기 목록 저장과 결정론적 도메인 계산 | 전체 |

---

## 1. 크롤링

Mock에서는 `advanceJobs()`가 2.5초 뒤 `EXTRACTION_TEMPLATES`를 채워 넣고, `plannedOutcome()`이 호스트·URL 문자열(`fail`)로 성공/실패를 흉내 낸다. 실제로는 아래 로직이 필요하다.

### 1.1 URL 검증 (`POST /recipes/import`)
- `http`/`https`만 허용, 그 외 → `422 validation_error` + `fieldErrors.url`
- 출처는 레시피와 분리된 `recipe_sources` 테이블로 관리, 출처 1 : 레시피 1..N — 한 출처에 레시피가 여러 개면 분리 저장 (`DATA_STRUCTURE.md`, `logics/RECIPE_ANALYSIS.md` §5)
- 동일 사용자·동일 출처 중복(`normalized_url`, 유튜브는 `video_id` 기준 1.3, 만개의레시피는 레시피 ID 기준 1.4) → `409 duplicate_recipe` + `details.existingRecipe`. 별도 저장하지 않고, 결과를 바꾸려면 기존 레시피에 수정 요청(`revision-requests`)
- 같은 출처의 레시피가 soft delete(`is_delete=true`) 상태면 **기존 레시피(분리된 레시피 포함)를 복구**(`is_delete=false`)하고 `200` + 복구된 레시피 반환. 재료·조리 순서·분석 이력은 삭제 전 상태 그대로, 재수집 job은 만들지 않음
- 생성 시 `recipe_sources` 1건 + 대표 `recipes` 1건(`importing`) + 출처 단위 `recipe_import_jobs` 1건(`job_type=import`), 분석 결과 레시피가 여러 개면 나머지 레시피 추가 생성
- 지원 호스트 정책: mock 기준 `youtube.com`, `youtu.be`, `10000recipe.com`, `blog.naver.com`, `m.blog.naver.com` (미지원 호스트는 수집 실패 처리)

### 1.2 본문 수집 (`httpx` + `trafilatura`, 필요 시 `beautifulsoup4`)
- **SSRF 방어**: 내부망·루프백·링크로컬 주소 차단(리다이렉트 이후 최종 IP 재검증), 요청 타임아웃, 응답 본문 크기 제한
- 사이트별 처리: 네이버 블로그 iframe 본문, 만개의레시피 구조화 페이지 (유튜브는 HTML 크롤링 대신 Gemini 영상 분석 사용, `logics/RECIPE_ANALYSIS.md` §3)
- 대표 이미지(`og:image`) 추출 → `imageUrl`
- 차단·동적 렌더링·본문 없음 등 실패 시 원본 URL 보존, `status=failed` + `failureReason`

### 1.3 유튜브 URL 처리 (`video_id` 기준 중복 확인)
- 대상 URL: `youtube.com/watch?v=`, `youtu.be/{id}`, `youtube.com/shorts/{id}` → `video_id` 추출, 추출 실패 시 `422 validation_error`
- 중복 확인은 URL 문자열이 아닌 **`video_id`** 기준: 형식이 달라도(`youtu.be` ↔ `watch?v=`, 쿼리 파라미터 차이) 같은 영상이면 `409 duplicate_recipe` + 기존 레시피, 분석 요청을 보내지 않음
- `recipe_sources`에 `source_type=youtube`, `video_id` 저장 (`(user_id, video_id)` 유니크)
- 썸네일: `https://i.ytimg.com/vi/{video_id}/hqdefault.jpg` → `imageUrl`
- 중복이 아니면 1.5 비동기 작업으로 유튜브 레시피 분석 실행 (`logics/RECIPE_ANALYSIS.md` §3)

### 1.4 만개의레시피 URL 처리 (레시피 ID 기준 중복 확인)
- 대상 URL: `https://www.10000recipe.com/recipe/{id}` (예: `https://www.10000recipe.com/recipe/7069580`) → 경로 맨 뒤 숫자를 **레시피 ID**로 추출
- 정규표현식으로 형식 확인 + ID 추출 (1번 캡처 그룹 = 레시피 ID):
  ```text
  ^https?://(?:www\.|m\.)?10000recipe\.com/recipe/(\d+)/?(?:[?#].*)?$
  ```
- 추출 실패(목록·검색·카테고리 페이지 등 레시피 페이지가 아닌 URL) 시 `422 validation_error` + `fieldErrors.url`
- 중복 확인은 URL 문자열이 아닌 **레시피 ID** 기준: 형식이 달라도(스킴, `www.`·`m.` 유무, 끝 `/`, 쿼리·프래그먼트 차이) 같은 ID면 `409 duplicate_recipe` + 기존 레시피, 페이지 수집·분석을 하지 않음
- `recipe_sources`에 `source_type=10000recipe`, `normalized_url=https://www.10000recipe.com/recipe/{id}` 저장 → `(user_id, normalized_url)` 유니크가 레시피 ID 기준으로 동작
- 중복이 아니면 1.5 비동기 작업으로 페이지 파싱·분석 실행 (`logics/RECIPE_ANALYSIS.md` §4.1)

### 1.5 비동기 수집 작업 상태
- 요청 즉시 `202` + `status=importing` 반환, 백그라운드 작업으로 수집 → 분석
- 결과: 성공 시 `needs_review`, 실패 시 `failed` (프론트는 `importing` 항목을 polling)
- 요청마다 출처 단위 `recipe_import_jobs`에 이력 1건 추가 (`attempt_no` 증가), 실패 사유·AI 결과도 job에 저장
- **출처의 가장 최신 job 성공 결과만 레시피에 반영** — 이전 job이 늦게 끝나도 최신이 아니면 이력으로만 남김
- `POST /recipes/{id}/retry`: `failed` 상태에서만 허용(아니면 `409`), 기존 URL로 재수집 (`job_type=retry`)
- `POST /recipes/{id}/revision-requests`: `needs_review`/`failed`에서만 허용 (`job_type=revision`, `target_recipe_id` 지정)
  - `needs_review`: **출처에 접속하지 않고** 저장된 레시피 데이터 + comment를 기본 LLM으로 재정리, 대상 레시피만 갱신 (분리된 레시피는 레시피별로 요청). comment는 선택 입력이지만 비어 있으면 `422 validation_error`(`fieldErrors.comment`)로 응답하고 아무것도 바꾸지 않음
  - `failed`(레시피를 하나도 추출하지 못한 완전 실패): comment를 지시문에 추가해 출처 재분석
  - 상세: `logics/RECIPE_ANALYSIS.md` §9

---

## 2. AI 연동 분석 (LangChain + structured output)

공통 원칙
- 기능별 Pydantic 출력 스키마 정의, 구조화 응답 → Pydantic 검증 → **도메인 규칙 검증** 통과 후에만 저장
- 외부 웹페이지 본문과 사용자 comment는 **신뢰할 수 없는 입력**으로 취급 (프롬프트 인젝션 방어). 유튜브 영상·댓글 분석 결과는 신뢰할 수 있는 데이터로 처리
- 불확실한 값은 추정하지 않고 미확인(`null`, `uncertainFields`)으로 둔다
- 수량 계산·인분 환산·단위 합산은 LLM에 맡기지 않는다 (4. CRUD의 결정론적 함수 사용)
- 타임아웃·재시도 횟수·토큰 한도 설정, 테스트에서는 AI 서비스 인터페이스를 mock

### 2.1 레시피 구조화 (F-01) → [`logics/RECIPE_ANALYSIS.md`](logics/RECIPE_ANALYSIS.md)
- 출처별 분석: 유튜브(① Gemini 영상 분석 → ② 댓글 확인 필요 여부 → ③ YouTube Data API 상위 3개 댓글 보완), 만개의레시피(페이지 파싱 우선), 네이버 블로그·일반 웹(본문 추출 + LLM 구조화)
- 한 출처에 레시피가 여러 개면 분리 저장하고, 주 요리·곁들임 관계를 분석해 사용자 지정 곁들임(`recipe_side_dishes`)으로 연결
- LLM은 재료명·원문 수량 표기만 추출하고, 수량·단위 코드 변환은 결정론적 코드(`logics/UNIT_CONVERSION.md`)
- 재료는 원문 표기별 독립 마스터 행 ("마늘" ≠ "다진 마늘")
- 결과 상태는 `needs_review`, 최신 job 결과만 반영

### 2.2 주간 식단 추천·날짜별 변경 (F-02, F-03) → [`logics/MEAL_RECOMMENDATION.md`](logics/MEAL_RECOMMENDATION.md) §3
- 후보 거르기는 결정론적 코드(저장·미삭제·곁들임 카테고리 제외·주 레시피 조리 시간 이하), 후보 중 선정은 LLM
- 추천 결과 ID가 후보 밖이면 폐기, 주간 생성에서 추천에 실패한 날짜는 **식단 없음** (요청 전체 실패·날짜별 변경 실패는 기존 식단 유지)
- 추천 진행 상태를 실행·날짜별로 저장 (`generating` → `complete`/`partial`/`failed`), 같은 주 중복 실행 방지
- 날짜별 변경은 현재 주 레시피 제외 + 코멘트(선택) 반영

### 2.3 곁들임 추천 (F-04) → [`logics/MEAL_RECOMMENDATION.md`](logics/MEAL_RECOMMENDATION.md) §4
- 사용자 지정 곁들임(`recipe_side_dishes`) 우선, 없으면 저장된 side/soup 레시피 중 LLM 선택, 곁들임 조리 시간은 조건에 넣지 않음
- 결과는 날짜별 식단 조합(`meal_plan_entry_sides`)으로만 저장, 적절한 후보가 없으면 곁들임 없이 구성

### 2.4 대체 재료 (F-06) — 런타임 AI 호출 없음
- 운영 전 사전 작업으로 재료별 대체 후보를 생성·검수해 `ingredient_substitutes` 베이스 데이터로 적재 ([`logics/PREP_SUBSTITUTE_BASE_DATA.md`](logics/PREP_SUBSTITUTE_BASE_DATA.md))
- 서비스는 재료 ID로 베이스 데이터를 조회해 후보 최대 2개 제공, 필요량은 `factor`로 결정론적 계산 (`factor = null`이면 확인 필요)
- 베이스 데이터가 없는 재료는 대체 후보 없음

---

## 3. 3rd party API

| 대상 | 용도 | 비고 |
|---|---|---|
| LLM 공급자 (`langchain-openai` 등) | 웹 본문·댓글 구조화, 식단·곁들임 추천, 대체 재료 사전 작업 | 모델명·키는 `pydantic-settings`로 관리, 프론트에 키 노출 금지 |
| Supabase Auth | 로그인·세션, Access Token 발급 | FastAPI에서 JWT 서명·발급자·만료 검증 → `401 unauthorized` (mock `?scenario=unauthorized`) |
| Supabase PostgreSQL (`supabase-py`) | 전체 데이터 저장 | 사용자 토큰 + RLS로 접근 제한, 일반 요청에 `service_role` 키 사용 금지 |
| Gemini API (`langchain-google-genai` / `google-genai`) | 유튜브 영상 분석 (`logics/RECIPE_ANALYSIS.md` §3.1): 영상 URL로 재료·조리 순서 추출, `needsCommentCheck` 판단 | API 키는 서버 환경변수에만 보관. 모델명·타임아웃은 설정 모듈에서 관리, 영상 길이에 비례하는 토큰 비용 모니터링 |
| YouTube Data API v3 | 댓글 보완 (`logics/RECIPE_ANALYSIS.md` §3.3): `commentThreads.list` 인기순 상위 3개 | `needsCommentCheck=true`일 때만 호출(1 unit/건, 일일 기본 10,000 unit). API 키는 서버 환경변수에만 보관 |
| 쿠팡 | 재료 검색 링크 (F-07) | **API 호출 없음**. `https://www.coupang.com/np/search?q=` URL 생성만, 현재 프론트 `lib/coupang.ts`에서 처리. 대체 적용 시 대체 재료명 사용 |

---

## 4. CRUD (도메인 규칙 포함)

### 4.1 레시피
| Method | Path | 로직 |
|---|---|---|
| GET | `/recipes?category=` | 카테고리 필터, `createdAt` 내림차순, 레시피별 조리 기록(`cookingLogs`) 포함 |
| GET | `/recipes/{id}` | 상세, 없으면 `404 not_found` |
| POST | `/recipes/import` | 1.1 검증 후 `importing` 레코드 생성 |
| POST | `/recipes/{id}/confirm` | `needs_review`에서만 허용(`409`), 재료·레시피명 필수(`422 fieldErrors`), `saved`로 전환 + `uncertainFields` 비움 |
| DELETE | `/recipes/{id}` | 오늘 이후 식단(주/곁들임)에 사용 중이면 `409`, 아니면 **soft delete**(`is_delete=true`) + 사용자 지정 곁들임 관계에서 제거 → `204`. 과거 식단·조리 기록 참조는 유지, 이후 목록·식단 후보·추천에서 제외 |

### 4.2 식단
| Method | Path | 로직 |
|---|---|---|
| GET | `/meal-plans/weeks/{weekStart}` | 주 시작(월요일 가정) 정규화, 7일 범위 항목 + 생성 상태(`none/partial/complete/failed`, 아직 채워지지 않은 실패 날짜) |
| GET | `/meal-plans/months/{YYYY-MM}` | 월의 주차별 시작·종료일, 식단 존재 여부 |
| POST | `/meal-plans/generate` | 입력 검증(날짜 1개 이상, 인분 1 이상 정수), 하루 1개 항목 upsert, 기존 항목 갱신 시 대체 재료 기록 삭제, 생성 즉시 확정(draft 없음) |
| GET | `/meal-plans/entries/{id}` | 주·곁들임별 인분 환산 재료, 대체 반영 재료명(`substitutedFrom`), 대체 조리 안내, 이전 조리 기록 |
| GET | `/meals/today` | 오늘 식단 상세 + 저장 레시피 존재 여부 |

### 4.3 조리 기록
| Method | Path | 로직 |
|---|---|---|
| POST | `/meal-plans/entries/{id}/complete` | **멱등**: 이미 완료면 기존 상태 반환, 아니면 완료 시각 저장 + 조리 기록 1건 생성 (식단 항목·날짜별 분리) |
| PUT | `/cooking-logs/{id}/review` | 별점(선택, 1~5 정수, 범위는 미확정) + 메모(선택, trim 후 빈 값은 `null`), 완료 상태와 독립 |

### 4.4 장보기 목록
| Method | Path | 로직 |
|---|---|---|
| GET | `/shopping-lists/{weekStart}` | 해당 주 식단의 주·곁들임 재료를 계산(아래 규칙), 항목별 출처·대체 정보·대체 후보 존재 여부, 미준비 개수(`neededCount`) |
| PATCH | `/shopping-lists/{weekStart}/items/{itemId}` | 준비 여부(`checked`)만 저장, 없는 항목이면 `404` |
| POST | `.../items/{itemId}/substitutes/apply` | 해당 식단 항목·레시피의 재료에만 적용(전역 아님), 해당 재료의 베이스 대체 후보(`ingredient_substitutes`)만 허용, 불확실 후보는 `confirmedUncertain` 없으면 `422`, 적용 후 목록 재계산 |

장보기 계산 규칙 (결정론적 Python 함수, `services/scaling.ts`·`services/shopping.ts`를 그대로 옮김)
- 필요량 = 기준 수량 × (계획 인분 ÷ 기준 인분), 기준 인분·수량이 없으면 `null`
- 같은 재료(`ingredient_id`) + 같은 단위 차원만 합산 (`logics/UNIT_CONVERSION.md` §5), 합산 불가 단위는 별도 표기
- 장보기 항목은 마스터 재료 단위로 분리 — "마늘"과 "다진 마늘"은 합산하지 않고 별도 항목
- 항목별 레시피·날짜 출처 관계 보존
- 식단 변경 시: 유지되는 항목은 준비 여부 유지, 사라진 항목 삭제, 새 항목은 미준비로 시작 (`syncChecked`)
- 식단·대체 재료·장보기 갱신은 **하나의 트랜잭션**으로 처리, 실패 시 기존 상태 유지

### 4.5 단위 체계 및 환산 규칙 → [`logics/UNIT_CONVERSION.md`](logics/UNIT_CONVERSION.md)
- 무게(g)·부피(ml)·개수·비정량 4개 차원, 컵 200ml, 같은 차원 안에서만 환산
- 원문 수량(`raw_amount`) 보존, 해석 불가 시 `quantity`·`unit_code`는 `null`
- 사용자 안내는 레시피 상세 재료 영역의 `환산 규칙` 외부 링크 (`docs/design/pages/RECIPE_DETAIL.md`)

### 4.6 공통
- 에러 응답 형식: `{ code, message, details?, fieldErrors? }` (`validation_error`, `duplicate_recipe`, `conflict`, `not_found`, `no_candidates`, `unauthorized`, `server_error`)
- JSON 필드는 camelCase (Pydantic `alias_generator=to_camel`)
- 모든 조회·수정은 인증된 사용자 범위로 제한 (요청 본문의 사용자 ID 신뢰 금지)
