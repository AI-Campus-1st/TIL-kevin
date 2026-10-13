const test = require('node:test');
const assert = require('node:assert/strict');
const { REGIONS, resolveRegion } = require('../src/regions');

test('시/도는 16개이고 각 시/도 안에 중복된 시/군/구가 없다', () => {
  assert.equal(REGIONS.length, 16);
  for (const r of REGIONS) {
    assert.ok(r.districts.length > 0, r.name);
    assert.equal(new Set(r.districts).size, r.districts.length, `${r.name}에 중복 있음`);
  }
});

test('2026년 개편이 반영돼 있다', () => {
  const incheon = REGIONS.find((r) => r.name === '인천광역시').districts;
  for (const d of ['제물포구', '영종구', '서해구', '검단구']) assert.ok(incheon.includes(d), d);
  for (const d of ['중구', '동구', '서구']) assert.ok(!incheon.includes(d), d);

  assert.ok(REGIONS.some((r) => r.name === '전남광주통합특별시'));
  assert.ok(!REGIONS.some((r) => r.name === '광주광역시' || r.name === '전라남도'));
  assert.ok(REGIONS.find((r) => r.name === '대구광역시').districts.includes('군위군'));
});

test('resolveRegion은 동명 지역을 시/도 약칭으로 구분한다', () => {
  assert.equal(resolveRegion('서울특별시', '중구').query, '서울 중구');
  assert.equal(resolveRegion('부산광역시', '중구').query, '부산 중구');
  assert.equal(resolveRegion('전남광주통합특별시', '광주 동구').query, '광주 동구');
  assert.equal(resolveRegion('세종특별자치시', '세종시').query, '세종시');
});

test('resolveRegion은 목록에 없는 조합을 거부한다', () => {
  assert.equal(resolveRegion('서울특별시', '해운대구'), null);
  assert.equal(resolveRegion('없는도', '중구'), null);
  assert.equal(resolveRegion(null, null), null);
});
