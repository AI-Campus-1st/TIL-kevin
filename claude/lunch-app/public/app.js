(() => {
  const HISTORY_KEY = 'lunch-history';
  const REGION_KEY = 'lunch-region';
  const HISTORY_MAX = 10;
  const SPIN_MS = 900;
  const CATEGORY_ICONS = { '': '🍽️', korean: '🍚', chinese: '🥟', japanese: '🍣', western: '🍝', snack: '🍢', asian: '🍜' };
  const SPICY_LABELS = ['안 매움', '살짝 매움', '매움', '아주 매움'];

  const $ = (id) => document.getElementById(id);
  const els = {
    form: $('search-form'),
    sido: $('sido'),
    district: $('district'),
    price: $('price'),
    spicy: $('spicy'),
    recommendBtn: $('recommend-btn'),
    categoryStrip: $('category-strip'),
    tagPills: $('tag-pills'),
    head: $('detail-head'),
    badge: $('photo-badge'),
    emoji: $('result-emoji'),
    name: $('result-name'),
    meta: $('result-meta'),
    reason: $('result-reason'),
    note: $('result-note'),
    error: $('error'),
    railPrice: $('rail-price'),
    railRegion: $('rail-region'),
    railMenu: $('rail-menu'),
    eatBtn: $('eat-btn'),
    rerollBtn: $('reroll-btn'),
    mapLink: $('map-link'),
    body: $('detail-body'),
    altList: $('alt-list'),
    placesTitle: $('places-title'),
    placesStatus: $('places-status'),
    placesList: $('places-list'),
    placesSource: $('places-source'),
    historyList: $('history-list'),
    clearHistory: $('clear-history'),
  };

  const state = {
    category: '',
    tags: new Set(),
    allMenus: [],
    regions: [],
    current: null,
    placesRequest: 0,
    busy: false,
  };

  // localStorage 접근 불가 환경(시크릿 모드 등) 대비
  function readStore(key, fallback) {
    try {
      const raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : fallback;
    } catch {
      return fallback;
    }
  }

  function writeStore(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch {
      /* 저장 불가 시 무시 */
    }
  }

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text != null) node.textContent = text;
    return node;
  }

  function won(n) {
    return `${n.toLocaleString('ko-KR')}원`;
  }

  // ---------- 최근 먹은 메뉴 ----------
  function loadHistory() {
    const list = readStore(HISTORY_KEY, []);
    return Array.isArray(list) ? list : [];
  }

  function formatDate(iso) {
    const d = new Date(iso);
    const diffDays = Math.round((new Date(new Date().toDateString()) - new Date(d.toDateString())) / 86400000);
    if (diffDays === 0) return '오늘';
    if (diffDays === 1) return '어제';
    return `${d.getMonth() + 1}월 ${d.getDate()}일`;
  }

  function renderHistory() {
    const history = loadHistory();
    els.historyList.innerHTML = '';
    els.clearHistory.classList.toggle('hidden', !history.length);
    if (!history.length) {
      els.historyList.append(el('li', 'empty', '아직 기록이 없어요. 추천받은 메뉴를 먹었다면 "이걸로 먹을래요"를 눌러 주세요.'));
      return;
    }
    for (const item of history) {
      const li = el('li');
      li.append(el('span', 'h-emoji', item.emoji), el('span', 'h-name', item.name), el('span', 'h-date', formatDate(item.date)));
      els.historyList.append(li);
    }
  }

  // ---------- 지역 선택 ----------
  function fillDistricts(sidoName, selected = '') {
    const sido = state.regions.find((r) => r.name === sidoName);
    els.district.innerHTML = '<option value="">시/군/구 선택</option>';
    els.district.disabled = !sido;
    if (!sido) return;
    for (const d of sido.districts) els.district.add(new Option(d, d, false, d === selected));
  }

  function initRegions(regions) {
    state.regions = regions;
    for (const r of regions) els.sido.add(new Option(r.name, r.name));
    const saved = readStore(REGION_KEY, null);
    if (saved && regions.some((r) => r.name === saved.sido)) {
      els.sido.value = saved.sido;
      fillDistricts(saved.sido, saved.district);
    }
  }

  /** 선택된 지역 정보, 미선택 시 null */
  function currentRegion() {
    const sido = state.regions.find((r) => r.name === els.sido.value);
    const district = els.district.value;
    if (!sido || !district) return null;
    return { sido: sido.name, district, label: sido.short ? `${sido.short} ${district}` : district };
  }

  function onRegionChange() {
    writeStore(REGION_KEY, { sido: els.sido.value, district: els.district.value });
    const region = currentRegion();
    els.railRegion.textContent = region ? region.label : '선택 안 함';
    if (state.current) {
      els.mapLink.href = mapSearchUrl(state.current);
      loadPlaces(state.current);
    }
  }

  els.sido.addEventListener('change', () => {
    fillDistricts(els.sido.value);
    onRegionChange();
  });
  els.district.addEventListener('change', onRegionChange);

  // ---------- 카테고리 · 기분 ----------
  function renderCategories(categories) {
    const entries = [['', '전체'], ...Object.entries(categories)];
    for (const [key, label] of entries) {
      const btn = el('button', 'category-tab');
      btn.type = 'button';
      btn.dataset.key = key;
      btn.setAttribute('aria-pressed', String(key === state.category));
      btn.classList.toggle('active', key === state.category);
      btn.append(el('span', 'icon', CATEGORY_ICONS[key] || '🍴'), el('span', null, label));
      els.categoryStrip.append(btn);
    }
  }

  els.categoryStrip.addEventListener('click', (e) => {
    const btn = e.target.closest('.category-tab');
    if (!btn) return;
    state.category = btn.dataset.key;
    for (const b of els.categoryStrip.children) {
      const on = b === btn;
      b.classList.toggle('active', on);
      b.setAttribute('aria-pressed', String(on));
    }
  });

  function renderTags(tags) {
    for (const [key, label] of Object.entries(tags)) {
      const btn = el('button', 'pill', label);
      btn.type = 'button';
      btn.setAttribute('aria-pressed', 'false');
      btn.addEventListener('click', () => {
        if (state.tags.has(key)) state.tags.delete(key);
        else state.tags.add(key);
        const on = state.tags.has(key);
        btn.classList.toggle('active', on);
        btn.setAttribute('aria-pressed', String(on));
      });
      els.tagPills.append(btn);
    }
  }

  // ---------- 근처 식당 ----------
  function mapSearchUrl(menu) {
    const region = currentRegion();
    const q = [region && region.label, menu.keyword || menu.name].filter(Boolean).join(' ');
    return `https://map.naver.com/p/search/${encodeURIComponent(q)}`;
  }

  function setPlacesStatus(text, isError = false) {
    els.placesStatus.textContent = text;
    els.placesStatus.classList.toggle('error', isError);
  }

  function arrowIcon() {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('class', 'place-arrow');
    svg.setAttribute('aria-hidden', 'true');
    const use = document.createElementNS('http://www.w3.org/2000/svg', 'use');
    use.setAttribute('href', '#i-arrow');
    svg.append(use);
    return svg;
  }

  function renderPlaces(places) {
    els.placesList.innerHTML = '';
    for (const p of places) {
      const li = el('li', 'place');
      const link = el(p.url ? 'a' : 'div', 'place-link');
      if (p.url) {
        link.href = p.url;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
      }
      const info = el('div', 'place-info');
      info.append(el('span', 'place-name', p.name));
      if (p.category) info.append(el('span', 'place-category', p.category));
      info.append(el('span', 'place-address', p.address || '주소 정보 없음'));
      if (p.phone) info.append(el('span', 'place-phone', p.phone));
      link.append(info);
      if (p.url) link.append(arrowIcon());
      li.append(link);
      els.placesList.append(li);
    }
  }

  async function loadPlaces(menu) {
    const requestId = ++state.placesRequest;
    const region = currentRegion();
    const keyword = menu.keyword || menu.name;
    els.placesSource.classList.add('hidden');
    els.placesList.innerHTML = '';

    if (!region) {
      els.placesTitle.textContent = '근처 식당';
      setPlacesStatus('검색 바에서 지역과 시/군/구를 고르면 근처 식당 5곳을 찾아 드려요.');
      return;
    }

    els.placesTitle.textContent = `${region.district} ${keyword} 맛집`;
    setPlacesStatus('');
    for (let i = 0; i < 5; i++) els.placesList.append(el('li', 'place skeleton'));

    const params = new URLSearchParams({ sido: region.sido, district: region.district, menu: menu.id });
    try {
      const res = await fetch(`/api/places?${params}`);
      const data = await res.json();
      if (requestId !== state.placesRequest) return; // 더 최근 요청이 있으면 무시

      els.placesList.innerHTML = '';
      if (!res.ok) {
        setPlacesStatus(data.error || '식당을 찾지 못했어요.', true);
        return;
      }
      if (!data.places.length) {
        setPlacesStatus(`"${data.query}" 검색 결과가 없어요. 다른 메뉴나 지역을 골라 보세요.`);
        return;
      }
      renderPlaces(data.places);
      els.placesSource.textContent = `"${data.query}" 검색 결과 · ${data.provider === 'kakao' ? '카카오맵' : '네이버 지도'}`;
      els.placesSource.classList.remove('hidden');
    } catch {
      if (requestId !== state.placesRequest) return;
      els.placesList.innerHTML = '';
      setPlacesStatus('식당 정보를 불러오지 못했어요. 잠시 후 다시 시도해 주세요.', true);
    }
  }

  // ---------- 추천 결과 ----------
  function showMenu(menu) {
    state.current = menu;
    els.emoji.textContent = menu.emoji;
    els.name.textContent = menu.name;

    els.meta.innerHTML = '';
    [menu.categoryLabel, `약 ${won(menu.price)}`, SPICY_LABELS[menu.spicy]].forEach((text, i) => {
      if (i) els.meta.append(el('span', 'dot', '·'));
      els.meta.append(el('span', null, text));
    });
    els.reason.textContent = menu.reason || '';
    els.reason.classList.toggle('hidden', !menu.reason);
    els.badge.classList.remove('hidden');

    els.railPrice.innerHTML = '';
    els.railPrice.append(el('span', 'rail-price-value', `약 ${won(menu.price)}`), el('span', 'rail-price-unit', '/ 1인'));
    els.railMenu.textContent = menu.name;
    els.eatBtn.disabled = false;
    els.eatBtn.textContent = '이걸로 먹을래요';
    els.rerollBtn.classList.remove('hidden');
    els.mapLink.classList.remove('hidden');
    els.mapLink.href = mapSearchUrl(menu);
    els.body.classList.remove('hidden');

    loadPlaces(menu);
  }

  function showAlternatives(list) {
    els.altList.innerHTML = '';
    $('alternatives').classList.toggle('hidden', !list.length);
    for (const menu of list) {
      const btn = el('button', 'alt-card');
      btn.type = 'button';
      btn.append(
        el('span', 'alt-photo', menu.emoji),
        el('span', 'alt-title', menu.name),
        el('span', 'alt-meta', `${menu.categoryLabel} · 약 ${won(menu.price)}`),
      );
      btn.addEventListener('click', () => {
        // 대안을 고르면 현재 메뉴와 자리 교체
        const prev = state.current;
        showMenu({ ...menu, reason: '이것도 좋은 선택이에요.' });
        showAlternatives(list.map((m) => (m.id === menu.id ? prev : m)));
        replayReveal();
        els.head.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
      els.altList.append(btn);
    }
  }

  function replayReveal() {
    els.head.classList.remove('revealed');
    void els.head.offsetWidth; // 애니메이션 재시작용 리플로우
    els.head.classList.add('revealed');
  }

  function startSpin() {
    els.head.classList.remove('revealed');
    els.head.classList.add('spinning');
    const pool = state.allMenus;
    if (!pool.length) return () => {};
    const timer = setInterval(() => {
      const m = pool[Math.floor(Math.random() * pool.length)];
      els.emoji.textContent = m.emoji;
      els.name.textContent = m.name;
    }, 70);
    return () => {
      clearInterval(timer);
      els.head.classList.remove('spinning');
    };
  }

  function buildQuery() {
    const params = new URLSearchParams();
    if (state.category) params.set('categories', state.category);
    if (state.tags.size) params.set('tags', [...state.tags].join(','));
    if (els.price.value) params.set('maxPrice', els.price.value);
    if (els.spicy.value) params.set('maxSpicy', els.spicy.value);
    const recent = loadHistory().map((h) => h.id);
    if (recent.length) params.set('recent', recent.join(','));
    return params.toString();
  }

  function setBusy(busy) {
    state.busy = busy;
    els.recommendBtn.disabled = busy;
    els.rerollBtn.disabled = busy;
    if (!state.current) els.eatBtn.disabled = busy;
  }

  async function doRecommend() {
    if (state.busy) return;
    els.error.classList.add('hidden');
    setBusy(true);
    const stopSpin = startSpin();

    try {
      const [res] = await Promise.all([fetch(`/api/recommend?${buildQuery()}`), new Promise((r) => setTimeout(r, SPIN_MS))]);
      const data = await res.json();
      stopSpin();

      if (!res.ok) {
        restoreHead();
        showError(data.error || '추천에 실패했어요.');
        return;
      }
      showMenu(data.pick);
      showAlternatives(data.alternatives);
      els.note.textContent = data.relaxed
        ? '조건에 맞는 메뉴를 최근에 다 드셔서, 최근 메뉴도 포함해 골랐어요.'
        : `조건에 맞는 메뉴 ${data.candidateCount}개 중에서 골랐어요.`;
      els.note.classList.remove('hidden');
      replayReveal();
    } catch {
      stopSpin();
      restoreHead();
      showError('서버에 연결할 수 없어요. 잠시 후 다시 시도해 주세요.');
    } finally {
      setBusy(false);
    }
  }

  // 추천 실패 시 이전 결과(또는 빈 상태)로 복원
  function restoreHead() {
    const m = state.current;
    els.emoji.textContent = m ? m.emoji : '🍽️';
    els.name.textContent = m ? m.name : '아직 고른 메뉴가 없어요';
  }

  function showError(message) {
    els.error.textContent = message;
    els.error.classList.remove('hidden');
  }

  els.form.addEventListener('submit', (e) => {
    e.preventDefault();
    doRecommend();
  });
  els.rerollBtn.addEventListener('click', doRecommend);

  els.eatBtn.addEventListener('click', () => {
    const m = state.current;
    // 추천 전에는 추천 버튼 역할
    if (!m) return doRecommend();
    const history = loadHistory();
    history.unshift({ id: m.id, name: m.name, emoji: m.emoji, date: new Date().toISOString() });
    writeStore(HISTORY_KEY, history.slice(0, HISTORY_MAX));
    renderHistory();
    els.eatBtn.disabled = true;
    els.eatBtn.textContent = '맛있게 드세요!';
  });

  els.clearHistory.addEventListener('click', () => {
    if (!confirm('최근 먹은 메뉴 기록을 모두 지울까요?')) return;
    writeStore(HISTORY_KEY, []);
    renderHistory();
  });

  // ---------- 초기화 ----------
  async function init() {
    renderHistory();
    try {
      const [optRes, menuRes] = await Promise.all([fetch('/api/options'), fetch('/api/menus')]);
      const { categories, tags, regions } = await optRes.json();
      state.allMenus = (await menuRes.json()).menus;
      initRegions(regions);
      renderCategories(categories);
      renderTags(tags);
      const region = currentRegion();
      els.railRegion.textContent = region ? region.label : '선택 안 함';
    } catch {
      showError('메뉴 정보를 불러오지 못했어요. 서버가 실행 중인지 확인해 주세요.');
    }
  }

  init();
})();
