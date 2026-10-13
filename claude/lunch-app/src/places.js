// 지도 장소 검색 (카카오 로컬 API 또는 네이버 지역 검색 API)
// - KAKAO_REST_API_KEY 가 있으면 카카오를 사용 (음식점 카테고리로 한정)
// - 없고 NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 이 있으면 네이버를 사용
// 두 API의 응답을 같은 모양으로 정규화해 반환

const RESULT_LIMIT = 5;
const TIMEOUT_MS = 5000;
const CACHE_TTL_MS = 10 * 60 * 1000;

class PlacesError extends Error {
  constructor(code, message) {
    super(message);
    this.code = code;
  }
}

function getProvider(env = process.env) {
  if (env.KAKAO_REST_API_KEY) return 'kakao';
  if (env.NAVER_CLIENT_ID && env.NAVER_CLIENT_SECRET) return 'naver';
  return null;
}

async function fetchJson(url, headers) {
  let res;
  try {
    res = await fetch(url, { headers, signal: AbortSignal.timeout(TIMEOUT_MS) });
  } catch (err) {
    throw new PlacesError('UPSTREAM_ERROR', `지도 API에 연결하지 못했어요. (${err.name})`);
  }
  if (res.status === 401 || res.status === 403) {
    const body = await res.text().catch(() => '');
    // 키는 유효하지만 카카오 앱에서 카카오맵 서비스를 켜지 않은 경우
    if (body.includes('OPEN_MAP_AND_LOCAL')) {
      throw new PlacesError(
        'SERVICE_DISABLED',
        '카카오 앱에서 카카오맵 사용이 꺼져 있어요. Kakao Developers > 내 애플리케이션 > 제품 설정 > 카카오맵에서 사용 설정을 켜 주세요.',
      );
    }
    throw new PlacesError('INVALID_API_KEY', '지도 API 키가 올바르지 않거나 권한이 없어요.');
  }
  if (res.status === 429) {
    throw new PlacesError('RATE_LIMITED', '지도 API 호출 한도를 넘었어요. 잠시 후 다시 시도해 주세요.');
  }
  if (!res.ok) {
    throw new PlacesError('UPSTREAM_ERROR', `지도 API 오류 (HTTP ${res.status})`);
  }
  return res.json();
}

async function searchKakao(query, env) {
  const url = new URL('https://dapi.kakao.com/v2/local/search/keyword.json');
  url.searchParams.set('query', query);
  url.searchParams.set('category_group_code', 'FD6'); // 음식점
  url.searchParams.set('size', String(RESULT_LIMIT));
  const data = await fetchJson(url, { Authorization: `KakaoAK ${env.KAKAO_REST_API_KEY}` });
  return (data.documents || []).map((d) => ({
    name: d.place_name,
    // "음식점 > 한식 > 찌개,전골" → "한식 > 찌개,전골"
    category: (d.category_name || '').replace(/^음식점\s*>\s*/, ''),
    address: d.road_address_name || d.address_name || '',
    phone: d.phone || '',
    url: d.place_url || '',
  }));
}

const HTML_ENTITIES = { '&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"', '&#39;': "'", '&apos;': "'" };

function stripHtml(s = '') {
  return s.replace(/<[^>]*>/g, '').replace(/&(amp|lt|gt|quot|#39|apos);/g, (m) => HTML_ENTITIES[m]);
}

async function searchNaver(query, env) {
  const url = new URL('https://openapi.naver.com/v1/search/local.json');
  url.searchParams.set('query', query);
  url.searchParams.set('display', String(RESULT_LIMIT));
  url.searchParams.set('sort', 'random'); // 정확도순
  const data = await fetchJson(url, {
    'X-Naver-Client-Id': env.NAVER_CLIENT_ID,
    'X-Naver-Client-Secret': env.NAVER_CLIENT_SECRET,
  });
  return (data.items || []).map((item) => {
    const name = stripHtml(item.title);
    const address = item.roadAddress || item.address || '';
    return {
      name,
      category: item.category || '',
      address,
      phone: item.telephone || '',
      // 네이버 응답의 link는 가게 홈페이지라 비어 있는 경우가 많아, 지도 검색 링크로 통일
      url: `https://map.naver.com/p/search/${encodeURIComponent(`${name} ${address}`.trim())}`,
    };
  });
}

const cache = new Map();

/**
 * 장소를 검색해 최대 5개 반환
 * @returns {Promise<{provider: string, places: object[]}>}
 */
async function searchPlaces(query, env = process.env) {
  const provider = getProvider(env);
  if (!provider) {
    throw new PlacesError(
      'NO_API_KEY',
      '지도 검색 API 키가 설정되지 않았어요. .env 파일에 KAKAO_REST_API_KEY 또는 NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 을 넣어 주세요.',
    );
  }

  const key = `${provider}:${query}`;
  const hit = cache.get(key);
  if (hit && hit.expires > Date.now()) return hit.value;

  const places = provider === 'kakao' ? await searchKakao(query, env) : await searchNaver(query, env);
  const value = { provider, places: places.slice(0, RESULT_LIMIT) };
  cache.set(key, { value, expires: Date.now() + CACHE_TTL_MS });
  return value;
}

function clearCache() {
  cache.clear();
}

module.exports = { searchPlaces, getProvider, stripHtml, clearCache, PlacesError };
