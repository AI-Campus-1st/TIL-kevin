const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const { recommend, CATEGORIES, TAGS, MENUS } = require('./src/recommend');
const { REGIONS, resolveRegion } = require('./src/regions');
const { searchPlaces, getProvider, PlacesError } = require('./src/places');

// .env 파일이 있으면 API 키 등을 환경변수로 로드
try {
  process.loadEnvFile(path.join(__dirname, '.env'));
} catch {
  /* .env 없음 */
}

const PORT = Number(process.env.PORT) || 3000;
const PUBLIC_DIR = path.join(__dirname, 'public');

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
};

function sendJson(res, status, data) {
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(data));
}

// "a,b,c" 형태의 쿼리를 허용된 값만 남긴 배열로 변환
function parseList(value, allowed) {
  if (!value) return [];
  return value.split(',').map((s) => s.trim()).filter((s) => allowed.includes(s));
}

function parseNumber(value) {
  if (value == null || value === '') return undefined;
  const n = Number(value);
  return Number.isFinite(n) ? n : undefined;
}

const PLACES_ERROR_STATUS = {
  NO_API_KEY: 503,
  INVALID_API_KEY: 502,
  SERVICE_DISABLED: 502,
  RATE_LIMITED: 429,
  UPSTREAM_ERROR: 502,
};

async function handlePlaces(res, q) {
  const region = resolveRegion(q.get('sido'), q.get('district'));
  if (!region) return sendJson(res, 400, { error: '지역을 다시 선택해 주세요.' });
  const menu = MENUS.find((m) => m.id === q.get('menu'));
  if (!menu) return sendJson(res, 400, { error: '알 수 없는 메뉴예요.' });

  const query = `${region.query} ${menu.keyword || menu.name}`;
  try {
    const { provider, places } = await searchPlaces(query);
    return sendJson(res, 200, { query, provider, places });
  } catch (err) {
    if (err instanceof PlacesError) {
      return sendJson(res, PLACES_ERROR_STATUS[err.code] || 502, { query, code: err.code, error: err.message });
    }
    console.error(err);
    return sendJson(res, 500, { query, error: '장소 검색 중 오류가 발생했어요.' });
  }
}

function handleApi(req, res, url) {
  if (url.pathname === '/api/options') {
    return sendJson(res, 200, { categories: CATEGORIES, tags: TAGS, regions: REGIONS });
  }

  if (url.pathname === '/api/places') {
    return handlePlaces(res, url.searchParams);
  }

  if (url.pathname === '/api/menus') {
    return sendJson(res, 200, { menus: MENUS });
  }

  if (url.pathname === '/api/recommend') {
    const q = url.searchParams;
    const menuIds = MENUS.map((m) => m.id);
    const result = recommend({
      categories: parseList(q.get('categories'), Object.keys(CATEGORIES)),
      tags: parseList(q.get('tags'), Object.keys(TAGS)),
      maxPrice: parseNumber(q.get('maxPrice')),
      maxSpicy: parseNumber(q.get('maxSpicy')),
      recent: parseList(q.get('recent'), menuIds),
    });
    if (!result.pick) {
      return sendJson(res, 404, { error: '조건에 맞는 메뉴가 없어요. 필터를 조금 풀어보세요.' });
    }
    return sendJson(res, 200, result);
  }

  return sendJson(res, 404, { error: 'Not found' });
}

function serveStatic(req, res, url) {
  const rel = url.pathname === '/' ? 'index.html' : decodeURIComponent(url.pathname).replace(/^\/+/, '');
  const filePath = path.join(PUBLIC_DIR, rel);
  // public 폴더 밖으로 나가는 경로 차단
  if (!filePath.startsWith(PUBLIC_DIR + path.sep)) {
    res.writeHead(403).end('Forbidden');
    return;
  }
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' }).end('Not found');
      return;
    }
    res.writeHead(200, { 'Content-Type': MIME[path.extname(filePath)] || 'application/octet-stream' });
    res.end(data);
  });
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  if (req.method !== 'GET') {
    res.writeHead(405).end('Method Not Allowed');
    return;
  }
  if (url.pathname.startsWith('/api/')) return handleApi(req, res, url);
  return serveStatic(req, res, url);
});

if (require.main === module) {
  server.listen(PORT, () => {
    console.log(`🍱 점심 메뉴 추천 서버: http://localhost:${PORT}`);
    const provider = getProvider();
    console.log(provider ? `📍 지도 검색: ${provider}` : '📍 지도 검색 API 키 없음 (.env.example 참고)');
  });
}

module.exports = server;
