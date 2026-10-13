const test = require('node:test');
const assert = require('node:assert/strict');
const { recommend, filterMenus, MENUS } = require('../src/recommend');

// 재현 가능한 테스트를 위한 시드 랜덤 (mulberry32)
function seededRng(seed = 1) {
  let s = seed >>> 0;
  return () => {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

test('필터 없이 추천하면 메뉴 1개와 대안 2개를 돌려준다', () => {
  const r = recommend({}, seededRng());
  assert.ok(r.pick);
  assert.equal(r.alternatives.length, 2);
  assert.equal(r.candidateCount, MENUS.length);
  const ids = [r.pick.id, ...r.alternatives.map((m) => m.id)];
  assert.equal(new Set(ids).size, ids.length, '중복 없이 뽑아야 한다');
});

test('카테고리 필터를 지킨다', () => {
  for (let seed = 1; seed < 50; seed++) {
    const r = recommend({ categories: ['japanese', 'chinese'] }, seededRng(seed));
    for (const m of [r.pick, ...r.alternatives]) {
      assert.ok(['japanese', 'chinese'].includes(m.category));
    }
  }
});

test('태그는 모두 만족해야 한다', () => {
  const list = filterMenus(MENUS, { tags: ['soup', 'noodle'] });
  assert.ok(list.length > 0);
  for (const m of list) {
    assert.ok(m.tags.includes('soup') && m.tags.includes('noodle'));
  }
});

test('예산과 매운맛 상한을 지킨다', () => {
  const list = filterMenus(MENUS, { maxPrice: 9000, maxSpicy: 0 });
  assert.ok(list.length > 0);
  for (const m of list) {
    assert.ok(m.price <= 9000);
    assert.equal(m.spicy, 0);
  }
});

test('최근 먹은 3개 메뉴는 추천하지 않는다', () => {
  const recent = ['kimchi-jjigae', 'jjajangmyeon', 'donkatsu'];
  for (let seed = 1; seed < 100; seed++) {
    const r = recommend({ recent }, seededRng(seed));
    for (const m of [r.pick, ...r.alternatives]) {
      assert.ok(!recent.includes(m.id));
    }
  }
});

test('후보가 최근 메뉴뿐이면 제외를 풀고 relaxed 표시', () => {
  const menus = MENUS.filter((m) => ['gimbap', 'ramyeon'].includes(m.id));
  const r = recommend({ recent: ['gimbap', 'ramyeon'] }, seededRng(), menus);
  assert.ok(r.pick);
  assert.equal(r.relaxed, true);
});

test('조건에 맞는 메뉴가 없으면 pick이 null', () => {
  const r = recommend({ maxPrice: 1000 });
  assert.equal(r.pick, null);
  assert.equal(r.candidateCount, 0);
});

test('직전에 먹은 카테고리는 덜 나온다', () => {
  let same = 0;
  let total = 0;
  for (let seed = 1; seed < 2000; seed++) {
    const r = recommend({ recent: ['kimchi-jjigae'], count: 0 }, seededRng(seed));
    total++;
    if (r.pick.category === 'korean') same++;
  }
  const koreanShare = MENUS.filter((m) => m.category === 'korean').length / MENUS.length;
  assert.ok(same / total < koreanShare, `한식 비율 ${same / total} < 기본 비율 ${koreanShare}`);
});
