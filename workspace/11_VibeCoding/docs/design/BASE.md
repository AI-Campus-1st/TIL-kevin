# Design System — Meal Planning & Recipe App

> **목적**: 레시피 저장, 주간 식단 구성, 장보기, 조리 기록을 일관된 UI로 제공한다.  
> **모듈 원칙**: `Brand Core`는 모든 매체에서 공유하고, `Medium Profile`만 교체해 PPT·웹·네이티브 앱에 대응한다.

## 0. 적용 원칙

- **Brand Core**: 컬러, 폰트, 형태, 아이콘 스타일 등 브랜드 공통 규칙.
- **Foundation**: 간격, 곡률, 그림자, 타이포그래피 위계.
- **Components**: 기능명세에 필요한 UI만 정의. P0는 MVP, P1은 확장 기능.
- **Medium Profile**: 캔버스, 화면 배치, 매체별 크기 규칙.
- 토큰은 CSS 변수로 관리한다. 컴포넌트에서 동일 값을 임의로 재정의하지 않는다.

---

# 1. Brand Core — 모든 매체 공통

## 1.1 비주얼 방향

- **키워드**: 신선함, 간결함, 실용성, 정돈된 생활.
- 장식보다 정보 위계와 짧은 행동 흐름을 우선한다.
- 레시피 사진은 보조 요소이며, 이미지가 없어도 콘텐츠 구조가 유지되어야 한다.

## 1.2 컬러

### 브랜드 팔레트

| 토큰 | 값 | 사용 |
|---|---|---|
| `primary` | `#7FF518` | 주요 CTA, 선택 상태, 핵심 진행 표시 |
| `primary-hover` | `#6BE600` | 호버 |
| `primary-active` | `#59C900` | 눌림 |
| `primary-soft` | `#F0FCE7` | 선택 배경, 연한 강조 영역 |
| `primary-disabled` | `#DDF6C7` | 비활성 CTA |
| `on-primary` | `#19210F` | primary 위 텍스트·아이콘 |
| `secondary` | `#385634` | 보조 강조 및 아이콘 |

### 중립·상태 팔레트

| 토큰 | 값 | 사용 |
|---|---|---|
| `canvas` / `surface` | `#FFFFFF` | 페이지·카드 기본 배경 |
| `surface-soft` | `#F6F8F3` | 보조 영역·비활성 배경 |
| `surface-strong` | `#EDF1E8` | 강조된 중립 배경 |
| `ink` | `#20251D` | 제목·주요 텍스트 |
| `body` | `#50574C` | 본문 |
| `muted` | `#7B8275` | 보조 정보·메타 |
| `hairline` | `#E0E5DA` | 테두리·구분선 |
| `border-strong` | `#BCC5B5` | 강조 테두리 |
| `success` | `#267A35` | 완료·성공 |
| `warning` | `#A65A00` | 주의·확인 필요 |
| `error` | `#B42318` | 오류·실패 |
| `info` | `#2563EB` | 안내 |
| `scrim` | `#20251D` / 50% | 모달 오버레이 |

**규칙**: primary는 핵심 행동에 제한적으로 사용한다. 밝은 `#7FF518` 위에는 흰색 대신 `on-primary`를 사용한다. 상태는 색상만이 아니라 텍스트·아이콘도 함께 표시한다. 서브 브랜드 팔레트는 정의하지 않는다.

## 1.3 폰트

- **기본**: Pretendard
- **Fallback**: `Pretendard, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`
- 별도 디스플레이 폰트 없이 크기·굵기·행간으로 위계를 만든다.

| 토큰 | 크기 / 굵기 | 행간 | 사용 |
|---|---|---|---|
| `display` | 28px / 700 | 1.25 | 화면 대표 제목 |
| `heading-lg` | 24px / 700 | 1.3 | 주요 섹션 제목 |
| `heading-md` | 20px / 600 | 1.35 | 카드 그룹·모달 제목 |
| `heading-sm` | 18px / 600 | 1.4 | 카드 제목 |
| `body-lg` | 16px / 400 | 1.5 | 본문·조리 순서 |
| `body-md` | 14px / 400 | 1.45 | 카드 메타·재료 정보 |
| `caption` | 12px / 400 | 1.4 | 보조 설명·상태 |
| `label` | 13px / 600 | 1.35 | 필드 라벨·탭 |
| `button` | 15px / 600 | 1.3 | 버튼 라벨 |
| `badge` | 11px / 600 | 1.2 | 상태 배지 |

- 본문은 14–16px을 기본으로 한다. 수량·인분·시간은 숫자와 단위를 함께 표시한다.

## 1.4 형태·간격·그림자

**Radius**: `sm 8px`(필드·작은 버튼) · `md 12px`(기본 카드) · `lg 16px`(주요 카드·시트) · `xl 24px`(큰 패널) · `full 9999px`(칩·원형 버튼).

**Spacing**: `4 / 8 / 12 / 16 / 20 / 24 / 32 / 40 / 48px`, 주요 섹션 간격 `56px`. 카드 패딩 기본 16px, 기본 콘텐츠 간격 16px.

**Elevation**: 기본 화면은 평면적으로 유지한다. 드롭다운·바텀시트 등 떠 있는 표면에만 `0 4px 16px rgba(32,37,29,.10)`을 사용한다. 영역 구분은 그림자보다 여백·표면색·1px 선을 우선한다.

## 1.5 아이콘·이미지·모션

- 단순한 선형 아이콘과 일관된 굵기를 사용한다. 아이콘 단독 버튼에는 접근 가능한 이름을 제공한다.
- 이미지 실패 시에도 제목·시간·재료 정보가 보이도록 플레이스홀더를 제공한다.
- 선택·열림·완료 상태만 짧고 절제된 모션으로 표현한다.

---

# 2. Components — 기능 기반 UI

> P0는 MVP 필수, P1은 확장 기능이다. 아래 목록은 기능명세에 필요한 범위로 한정한다.

## 2.1 공통 셸과 탐색

- **`app-shell`**: 헤더, 스크롤 콘텐츠, 하단 내비게이션. 탐색 구조 제안은 `오늘 · 식단 · 레시피 · 장보기`이며 최종 IA에 맞춰 조정한다.
- **`screen-header`**: 화면 제목, 필요한 날짜/주차 정보, 화면 주요 액션.
- **`status-chip`**: `초안`, `확정`, `완료`, `보유함`, `확인 필요` 등을 텍스트와 함께 표시.

## 2.2 레시피 저장·탐색

- **`recipe-url-form` (P0)**: URL 입력, 가져오기 CTA, 필드 오류, 제출 중 상태.
- **`recipe-import-status` (P0)**: `가져오는 중 / 검토 필요 / 실패`. 실패 시 원본 URL 유지, 재시도·직접 입력 제공.
- **`recipe-review-form` (P0)**: 레시피명, 인분, 조리 시간, 재료·수량, 조리 순서, 원본 링크. 사용자가 추출 결과를 수정한 뒤 저장한다.
- **`recipe-card` / `recipe-list-item` (P0)**: 레시피명, 조리 시간, 주요 재료, 선택적 이미지·카테고리. 카드형은 탐색용, 리스트형은 조밀한 목록용.
- **`recipe-search-filter` (P1)**: 저장 레시피 검색·정렬 및 확정된 카테고리/시간/재료 필터.

## 2.3 주간·월간 식단

- **`week-date-selector` (P0)**: 요리할 날짜 선택. 선택하지 않은 날짜에는 메뉴를 배정하지 않는다.
- **`meal-plan-settings` (P0)**: 날짜별 조리 시간과 인원. 기본값은 평일 30분, 주말 70분, 1명.
- **`meal-plan-day-card` (P0)**: 날짜, 레시피명, 예상 시간, 주요 재료, 선택적 곁들임, 초안/확정 상태.
- **`menu-change-panel` (P0)**: 자연어 변경 요청과 후보 목록. 사용자가 후보를 선택하기 전에는 기존 메뉴를 유지하며, 추천은 저장 레시피 안에서만 한다.
- **`meal-plan-confirmation` (P0)**: 확정 전 식단 확인. 확정 후 통합 장보기 목록을 생성한다.
- **`monthly-week-strip` (P1)**: 달력 대신 월의 주차를 가로 블록으로 표시. 주 시작일과 식단 구성 여부를 색상 외에 도트·라벨·채움으로도 표현한다.

## 2.4 장보기·대체 재료

- **`shopping-list-item` (P0)**: 재료명, 통합 필요량, 편집 가능한 구매 수량, 보유 여부, 사용 레시피/메뉴, 쿠팡 검색 링크. `필요량`과 `구매 수량`은 분리한다.
- **`ingredient-usage-details` (P0)**: 재료별 사용 출처 및 레시피/메뉴별 수량을 펼쳐 본다.
- **`substitute-ingredient-panel` (P0)**: 후보 1–2개, 필요량/비율, 맛 차이, 조리법 변경 여부, 주의사항·불확실성. 선택한 메뉴에만 적용한다.
- **`coupang-search-link` (P0)**: 현재 구매 대상 재료명으로 쿠팡 검색 페이지를 새 탭에서 연다. 상품 선택·주문·가격 집계는 지원하지 않는다.

## 2.5 오늘의 메뉴·조리 기록

- **`today-meal-card` (P0)**: 오늘의 확정 메뉴, 레시피명, 예상 시간, 주요 재료. 메뉴가 없으면 `주간 식단 보기` CTA 제공.
- **`recipe-cooking-view` (P0)**: 예상 시간·인분, 재료와 수량, 조리 순서, 곁들임 메뉴.
- **`cooking-complete-action` (P0)**: `요리 완료` 한 번의 동작으로 완료 상태와 시각을 저장. 날짜별 메뉴 항목에 연결하고 중복 기록을 방지한다.
- **`cooking-review-form` (P0 최소)**: 선택 입력인 별점·자유 메모. 요리 완료의 필수 조건이 아니며, 미확정 별점 범위를 임의로 고정하지 않는다.

## 2.6 공통 피드백

- **`empty-state`**: 빈 상태 이유와 다음 행동 CTA 제공(예: 레시피 없음 → 레시피 추가).
- **`loading-state` / `error-state`**: 진행 상황, 원인, 재시도·직접 입력 등 다음 행동 표시. 기존 데이터를 임의로 덮어쓰지 않는다.
- **`confirm-dialog` / `bottom-sheet` / `toast`**: 확인이 필요한 동작, 모바일 선택 UI, 짧은 성공 알림에 사용한다. 중요한 오류를 토스트만으로 전달하지 않는다.

---

# 3. Interaction Rules — 상태와 데이터 표현

- 후보 선택·확정 전까지 기존 메뉴와 값을 보존한다.
- 통합 재료는 레시피/메뉴별 사용량 출처를 확인할 수 있어야 한다.
- 보유 재료는 구매 필요 집계에서 제외하되, 별도 냉장고 재고 관리 UI는 제공하지 않는다.
- 추출·대체·단위 환산이 불확실하면 숫자를 추정하지 않고 `미확인` 또는 `확인 필요`로 표시한다.
- 평가·메모는 선택 사항이며 요리 완료 흐름을 막지 않는다.
- 상태는 색상뿐 아니라 텍스트·아이콘으로 구분한다. 터치 컨트롤은 가능한 한 44×44px 이상으로 구성한다.

---

# 4. Medium Profile — 매체별 설정

> Brand Core와 공통 토큰은 유지하고, 대상 매체가 바뀌면 이 장의 해당 프로필만 교체한다.

## 4.1 활성 프로필: Web App in Mobile Dimensions

**웹으로 구현하되 모바일 앱 크기를 유지한다. 반응형 breakpoint에 따른 레이아웃 변경은 하지 않는다.**

- 기준 캔버스: **390 × 844 CSS px**, 최대 너비 **430px**.
- 좁은 뷰포트에서는 가용 너비만큼 줄이며, 컴포넌트 순서·정보 구조는 바꾸지 않는다.
- 데스크톱에서는 캔버스를 화면 중앙에 놓고 바깥 배경을 `surface-soft`로 처리한다. 휴대폰에서는 전체 화면 너비를 사용한다.
- 콘텐츠는 기본 세로 스크롤. `monthly-week-strip` 등 필요한 영역에만 가로 스크롤을 허용한다.
- 하단 내비게이션은 고정하고 본문 하단에 충분한 여백을 둔다. 하단 CTA와 서로 겹치지 않게 한다.
- 상·하단은 기기의 `safe-area-inset`을 고려한다. 별도의 태블릿·데스크톱 레이아웃은 만들지 않는다.

| 토큰 | 값 | 용도 |
|---|---:|---|
| `app.max-width` | 430px | 앱 캔버스 최대 너비 |
| `app.reference-width` | 390px | 기준 시안 |
| `app.page-padding-x` | 20px | 좌우 패딩 |
| `app.header-height` | 56px | 상단 헤더 |
| `app.bottom-nav-height` | 64px + safe area | 하단 내비게이션 |
| `app.content-gap` | 16px | 콘텐츠 간격 |
| `app.card-padding` | 16px | 카드 내부 패딩 |

---

# 5. CSS Token Starter

```css
:root {
  /* Brand Core */
  --color-primary: #7ff518;
  --color-primary-hover: #6be600;
  --color-primary-active: #59c900;
  --color-primary-soft: #f0fce7;
  --color-primary-disabled: #ddf6c7;
  --color-on-primary: #19210f;
  --color-secondary: #385634;
  --color-canvas: #ffffff;
  --color-surface-soft: #f6f8f3;
  --color-surface-strong: #edf1e8;
  --color-ink: #20251d;
  --color-body: #50574c;
  --color-muted: #7b8275;
  --color-hairline: #e0e5da;
  --color-border-strong: #bcc5b5;
  --color-success: #267a35;
  --color-warning: #a65a00;
  --color-error: #b42318;
  --color-info: #2563eb;
  --font-sans: "Pretendard", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 24px;
  --radius-full: 9999px;
  --space-1: 4px; --space-2: 8px; --space-3: 12px;
  --space-4: 16px; --space-5: 20px; --space-6: 24px;
  --space-8: 32px; --space-10: 40px; --space-12: 48px;
  --shadow-overlay: 0 4px 16px rgba(32, 37, 29, .10);
  /* Active Medium Profile: Web App in Mobile Dimensions */
  --app-max-width: 430px;
  --app-page-padding-x: 20px;
  --app-header-height: 56px;
  --app-bottom-nav-height: 64px;
}
```

# 6. 미확정·범위 밖 항목

- 반응형 태블릿·데스크톱 레이아웃은 범위 밖이다.
- 장보기 그룹 기준, 별점 척도, 카테고리 목록, 주간 시작 요일 등은 기능 정책 확정 후 반영한다.
- 쿠팡 연동은 검색 링크만 제공하며 상품 선택·장바구니·주문·가격 계산 UI는 포함하지 않는다.
- 세부 로딩 스켈레톤, 애니메이션 시간, 플랫폼별 네이티브 UI는 필요한 시점에 추가한다.


앱 전체에서 Header 제외
