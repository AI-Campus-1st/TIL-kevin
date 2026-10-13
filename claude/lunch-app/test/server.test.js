const test = require('node:test');
const assert = require('node:assert/strict');

// 테스트 중에는 .env 의 실제 키를 쓰지 않도록 비워 둠
for (const k of ['KAKAO_REST_API_KEY', 'NAVER_CLIENT_ID', 'NAVER_CLIENT_SECRET']) process.env[k] = '';

const server = require('../server');

let base;
test.before(async () => {
  await new Promise((resolve) => server.listen(0, resolve));
  base = `http://127.0.0.1:${server.address().port}`;
});
test.after(() => server.close());

test('/api/options 에 지역 목록이 포함된다', async () => {
  const data = await (await fetch(`${base}/api/options`)).json();
  assert.ok(Array.isArray(data.regions));
  assert.ok(data.regions.some((r) => r.name === '서울특별시'));
});

test('/api/places 는 잘못된 지역·메뉴를 400으로 거부한다', async () => {
  let res = await fetch(`${base}/api/places?sido=서울특별시&district=해운대구&menu=bibimbap`);
  assert.equal(res.status, 400);
  res = await fetch(`${base}/api/places?sido=서울특별시&district=강남구&menu=nope`);
  assert.equal(res.status, 400);
});

test('/api/places 는 키가 없으면 503과 검색어를 돌려준다', async () => {
  const res = await fetch(`${base}/api/places?sido=서울특별시&district=강남구&menu=tangsuyuk`);
  assert.equal(res.status, 503);
  const data = await res.json();
  assert.equal(data.code, 'NO_API_KEY');
  assert.equal(data.query, '서울 강남구 탕수육');
});
