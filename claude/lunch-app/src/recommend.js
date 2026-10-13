const { CATEGORIES, TAGS, MENUS } = require('./menus');

// 최근 먹은 메뉴 중 이 개수만큼은 추천 후보에서 제외
const RECENT_EXCLUDE_COUNT = 3;
// 직전에 먹은 메뉴와 같은 카테고리는 가중치를 낮춤
const SAME_CATEGORY_WEIGHT = 0.4;

/**
 * 조건에 맞는 메뉴만 필터링
 * - categories: 하나라도 일치하면 통과 (비어 있으면 전체)
 * - tags: 선택한 태그를 모두 가진 메뉴만 통과
 * - maxPrice / maxSpicy: 상한
 */
function filterMenus(menus, { categories = [], tags = [], maxPrice, maxSpicy } = {}) {
  return menus.filter((m) => {
    if (categories.length && !categories.includes(m.category)) return false;
    if (tags.some((t) => !m.tags.includes(t))) return false;
    if (Number.isFinite(maxPrice) && m.price > maxPrice) return false;
    if (Number.isFinite(maxSpicy) && m.spicy > maxSpicy) return false;
    return true;
  });
}

function weightedPick(items, weights, rng) {
  const total = weights.reduce((a, b) => a + b, 0);
  let r = rng() * total;
  for (let i = 0; i < items.length; i++) {
    r -= weights[i];
    if (r < 0) return i;
  }
  return items.length - 1;
}

function buildReason(menu, recentMenu) {
  const parts = [];
  if (menu.tags.includes('soup')) parts.push('따끈한 국물');
  if (menu.tags.includes('hearty')) parts.push('든든한 한 끼');
  if (menu.tags.includes('light')) parts.push('부담 없이 가볍게');
  if (menu.tags.includes('quick')) parts.push('빠르게 먹고 쉬기');
  if (menu.spicy >= 2) parts.push('스트레스 날리는 매운맛');
  if (recentMenu && recentMenu.category !== menu.category) {
    parts.push(`어제 ${CATEGORIES[recentMenu.category]}이었으니 오늘은 ${CATEGORIES[menu.category]}`);
  }
  if (!parts.length) parts.push('오늘 같은 날 딱 좋은 메뉴');
  return parts.slice(0, 2).join(' · ');
}

/**
 * 점심 메뉴 추천
 * @param {object} options
 * @param {string[]} [options.categories]
 * @param {string[]} [options.tags]
 * @param {number}   [options.maxPrice]
 * @param {number}   [options.maxSpicy]
 * @param {string[]} [options.recent]  최근 먹은 메뉴 id (최근 순)
 * @param {number}   [options.count]   함께 돌려줄 대안 개수
 * @param {() => number} [rng]
 */
function recommend(options = {}, rng = Math.random, menus = MENUS) {
  const { recent = [], count = 2 } = options;
  const candidates = filterMenus(menus, options);

  if (!candidates.length) {
    return { pick: null, alternatives: [], candidateCount: 0, relaxed: false };
  }

  // 최근 먹은 메뉴는 제외하되, 그러면 후보가 없을 때는 제외 해제
  const recentSet = new Set(recent.slice(0, RECENT_EXCLUDE_COUNT));
  let pool = candidates.filter((m) => !recentSet.has(m.id));
  let relaxed = false;
  if (!pool.length) {
    pool = candidates;
    relaxed = true;
  }

  const recentMenu = recent.length ? menus.find((m) => m.id === recent[0]) : null;
  const weights = pool.map((m) =>
    recentMenu && m.category === recentMenu.category ? SAME_CATEGORY_WEIGHT : 1,
  );

  // 가중치 랜덤으로 1 + count 개를 중복 없이 추첨
  const picked = [];
  const remaining = [...pool];
  const remainingWeights = [...weights];
  while (picked.length < 1 + count && remaining.length) {
    const i = weightedPick(remaining, remainingWeights, rng);
    picked.push(remaining[i]);
    remaining.splice(i, 1);
    remainingWeights.splice(i, 1);
  }

  const [pick, ...alternatives] = picked;
  return {
    pick: { ...pick, categoryLabel: CATEGORIES[pick.category], reason: buildReason(pick, recentMenu) },
    alternatives: alternatives.map((m) => ({ ...m, categoryLabel: CATEGORIES[m.category] })),
    candidateCount: candidates.length,
    relaxed,
  };
}

module.exports = { recommend, filterMenus, CATEGORIES, TAGS, MENUS };
