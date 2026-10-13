# 오늘뭐먹지

점심 메뉴 추천 웹 서비스. 외부 의존성 없이 Node.js만으로 동작.

## 실행

```bash
npm start        # http://localhost:3000
npm run dev      # 파일 변경 시 자동 재시작
npm test         # 단위 테스트
```

- 포트는 `PORT` 환경변수로 변경 가능
- Node.js 20.12 이상 필요

### 근처 식당 검색 API 키 설정

추천 메뉴로 근처 식당 5곳을 보여주려면 지도 검색 API 키 필요.
`.env.example` 을 `.env` 로 복사하고 아래 둘 중 하나를 채운 뒤 서버 재시작.

| 제공자 | 환경변수 | 발급처 |
| --- | --- | --- |
| 카카오 로컬 (권장, 음식점만 검색) | `KAKAO_REST_API_KEY` | [Kakao Developers](https://developers.kakao.com) → 내 애플리케이션 → REST API 키 |
| 네이버 지역 검색 | `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET` | [NAVER Developers](https://developers.naver.com) → 애플리케이션 등록 → 검색 API |

- 둘 다 있으면 카카오 사용
- 카카오는 키 발급 외에 **제품 설정 → 카카오맵 → 사용 설정 ON** 필요 (꺼져 있으면 `SERVICE_DISABLED` 오류)
- 키가 없어도 메뉴 추천은 그대로 동작하고, 식당 목록 자리에 안내 문구 표시

## 기능

- **검색 바**: 지역(시/도 → 시/군/구), 예산, 매운맛을 한 줄에서 선택 후 검색 버튼으로 추천
  - 2026년 10월 행정구역 기준, 선택한 지역은 브라우저에 저장
  - 일반구가 있는 시는 `수원시 장안구`처럼 구 단위로 선택
- **카테고리 스트립**: 전체·한식·중식·일식·양식·분식·아시안 중 하나 선택
- **오늘의 기분**: 국물·든든하게·가볍게·빨리·밥·면 (여러 개 선택 시 모두 만족하는 메뉴만)
- **추천 결과**: 메뉴 1개 + 대안 2개 (대안 카드를 누르면 메인과 교체)
- **근처 식당 5곳**: `지역 + 추천 메뉴`(예: `서울 강남구 김치찌개`)로 지도 검색한 결과를 추천 아래에 표시
  - 식당 이름, 업종, 주소, 전화번호, 지도 링크
  - 대안 메뉴나 지역을 바꾸면 자동 재검색
- **최근 먹은 메뉴 기록** (브라우저 localStorage)
  - 최근 3번 먹은 메뉴는 추천에서 제외
  - 직전에 먹은 메뉴와 같은 종류는 덜 나오도록 가중치 조정

## 디자인

Airbnb 디자인 가이드(`DESIGN-airbnb.md`) 기반.

- 흰 캔버스 + 잉크(`#222222`) 텍스트, 강조색은 Rausch(`#ff385c`) 하나만 사용 (주요 버튼, 검색 버튼)
- 알약형 검색 바 + 원형 검색 버튼, 밑줄형 카테고리 스트립, 알약형 기분 필터
- 데스크톱은 왼쪽 상세 + 오른쪽 고정 카드(가격·지역·메뉴·주요 버튼) 2단 구성, 1128px 미만은 1단
- 그림자는 한 단계만 사용, 모서리는 버튼 8px · 카드 14px · 검색 바 완전 원형
- 글꼴은 Airbnb Cereal 대신 Pretendard(Inter 기반 + 한글) 사용
- 사진 자리는 메뉴 이모지로 대체

## 구조

```
server.js            HTTP 서버 (정적 파일 + API)
src/menus.js         메뉴 데이터 (46종)
src/recommend.js     필터링 · 가중치 랜덤 추천 로직
src/regions.js       전국 시/도 · 시/군/구 목록
src/places.js        카카오/네이버 장소 검색 (응답 정규화, 10분 캐시)
public/              프론트엔드 (index.html, style.css, app.js)
test/                node:test 단위 테스트
```

## API

| 메서드 | 경로 | 설명 |
| --- | --- | --- |
| GET | `/api/options` | 카테고리·태그·지역 목록 |
| GET | `/api/menus` | 전체 메뉴 |
| GET | `/api/recommend` | 메뉴 추천 |
| GET | `/api/places?sido=&district=&menu=` | 지역+메뉴로 식당 최대 5곳 검색 |

- `/api/places` 는 목록에 있는 지역·메뉴 id만 허용 (임의 검색어 프록시 방지)
- API 키가 없으면 `503` (`code: "NO_API_KEY"`) 반환

`/api/recommend` 쿼리 파라미터 (모두 선택):

- `categories` — 쉼표 구분, 예: `korean,japanese`
- `tags` — 쉼표 구분, 모두 만족하는 메뉴만, 예: `soup,noodle`
- `maxPrice` — 최대 가격(원)
- `maxSpicy` — 최대 매운맛 0~3
- `recent` — 최근 먹은 메뉴 id (최근 순, 쉼표 구분)

조건에 맞는 메뉴가 없으면 `404` 반환.

## 메뉴 추가

`src/menus.js`의 `MENUS` 배열에 항목 추가.
