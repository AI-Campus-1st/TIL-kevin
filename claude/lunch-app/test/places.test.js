const test = require('node:test');
const assert = require('node:assert/strict');
const { searchPlaces, getProvider, stripHtml, clearCache } = require('../src/places');

const realFetch = globalThis.fetch;

function stubFetch(handler) {
  const calls = [];
  globalThis.fetch = async (url, opts) => {
    calls.push({ url: new URL(url), headers: opts.headers });
    return handler(new URL(url));
  };
  return calls;
}

function jsonResponse(body, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
}

test.afterEach(() => {
  globalThis.fetch = realFetch;
  clearCache();
});

test('키 설정에 따라 제공자를 고른다 (카카오 우선)', () => {
  assert.equal(getProvider({}), null);
  assert.equal(getProvider({ NAVER_CLIENT_ID: 'a' }), null);
  assert.equal(getProvider({ NAVER_CLIENT_ID: 'a', NAVER_CLIENT_SECRET: 'b' }), 'naver');
  assert.equal(getProvider({ KAKAO_REST_API_KEY: 'k', NAVER_CLIENT_ID: 'a', NAVER_CLIENT_SECRET: 'b' }), 'kakao');
});

test('키가 없으면 NO_API_KEY 오류', async () => {
  await assert.rejects(searchPlaces('서울 강남구 김치찌개', {}), { code: 'NO_API_KEY' });
});

test('카카오: 음식점 카테고리로 5개 요청하고 응답을 정규화한다', async () => {
  const docs = Array.from({ length: 5 }, (_, i) => ({
    place_name: `식당${i}`,
    category_name: '음식점 > 한식 > 찌개,전골',
    road_address_name: `서울 강남구 테헤란로 ${i}`,
    address_name: '서울 강남구 역삼동',
    phone: '02-000-0000',
    place_url: `http://place.map.kakao.com/${i}`,
  }));
  const calls = stubFetch(() => jsonResponse({ documents: docs }));

  const r = await searchPlaces('서울 강남구 김치찌개', { KAKAO_REST_API_KEY: 'test-key' });

  assert.equal(calls[0].url.hostname, 'dapi.kakao.com');
  assert.equal(calls[0].url.searchParams.get('query'), '서울 강남구 김치찌개');
  assert.equal(calls[0].url.searchParams.get('category_group_code'), 'FD6');
  assert.equal(calls[0].url.searchParams.get('size'), '5');
  assert.equal(calls[0].headers.Authorization, 'KakaoAK test-key');

  assert.equal(r.provider, 'kakao');
  assert.equal(r.places.length, 5);
  assert.deepEqual(r.places[0], {
    name: '식당0',
    category: '한식 > 찌개,전골',
    address: '서울 강남구 테헤란로 0',
    phone: '02-000-0000',
    url: 'http://place.map.kakao.com/0',
  });
});

test('네이버: HTML 태그를 제거하고 지도 링크를 만든다', async () => {
  const calls = stubFetch(() =>
    jsonResponse({
      items: [
        {
          title: '<b>김치찌개</b> 명가 &amp; 식당',
          category: '한식>찌개,전골',
          telephone: '',
          address: '서울특별시 강남구 역삼동 1',
          roadAddress: '서울특별시 강남구 테헤란로 1',
          link: '',
        },
      ],
    }),
  );

  const r = await searchPlaces('서울 강남구 김치찌개', { NAVER_CLIENT_ID: 'id', NAVER_CLIENT_SECRET: 'secret' });

  assert.equal(calls[0].url.hostname, 'openapi.naver.com');
  assert.equal(calls[0].url.searchParams.get('display'), '5');
  assert.equal(calls[0].headers['X-Naver-Client-Id'], 'id');
  assert.equal(calls[0].headers['X-Naver-Client-Secret'], 'secret');

  assert.equal(r.provider, 'naver');
  assert.equal(r.places[0].name, '김치찌개 명가 & 식당');
  assert.equal(r.places[0].address, '서울특별시 강남구 테헤란로 1');
  assert.match(r.places[0].url, /^https:\/\/map\.naver\.com\/p\/search\//);
});

test('API 키 오류와 호출 한도를 구분한다', async () => {
  stubFetch(() => jsonResponse({}, 401));
  await assert.rejects(searchPlaces('a', { KAKAO_REST_API_KEY: 'bad' }), { code: 'INVALID_API_KEY' });
  stubFetch(() => jsonResponse({}, 429));
  await assert.rejects(searchPlaces('b', { KAKAO_REST_API_KEY: 'k' }), { code: 'RATE_LIMITED' });
});

test('카카오맵 서비스가 꺼진 앱은 SERVICE_DISABLED 로 구분한다', async () => {
  stubFetch(() =>
    jsonResponse({ errorType: 'NotAuthorizedError', message: 'App(test) disabled OPEN_MAP_AND_LOCAL service.' }, 403),
  );
  await assert.rejects(searchPlaces('c', { KAKAO_REST_API_KEY: 'k' }), { code: 'SERVICE_DISABLED' });
});

test('같은 검색어는 캐시해서 API를 다시 부르지 않는다', async () => {
  const calls = stubFetch(() => jsonResponse({ documents: [] }));
  const env = { KAKAO_REST_API_KEY: 'k' };
  await searchPlaces('서울 중구 짜장면', env);
  await searchPlaces('서울 중구 짜장면', env);
  assert.equal(calls.length, 1);
});

test('stripHtml', () => {
  assert.equal(stripHtml('<b>a</b> &lt;b&gt; &quot;c&quot;'), 'a <b> "c"');
});
