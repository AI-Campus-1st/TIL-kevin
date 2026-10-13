// 점심 메뉴 데이터
// price: 1인 기준 대략적인 가격(원), spicy: 0(안 매움) ~ 3(아주 매움)
// keyword: 지도 검색에 쓸 단어 (없으면 name 사용)
// tags: soup(국물), hearty(든든), light(가벼움), quick(빨리 먹기), rice(밥), noodle(면)

const CATEGORIES = {
  korean: '한식',
  chinese: '중식',
  japanese: '일식',
  western: '양식',
  snack: '분식',
  asian: '아시안',
};

const TAGS = {
  soup: '국물',
  hearty: '든든하게',
  light: '가볍게',
  quick: '빨리',
  rice: '밥',
  noodle: '면',
};

const MENUS = [
  // 한식
  { id: 'kimchi-jjigae', name: '김치찌개', emoji: '🍲', category: 'korean', price: 9000, spicy: 2, tags: ['soup', 'rice', 'hearty'] },
  { id: 'doenjang-jjigae', name: '된장찌개', emoji: '🥘', category: 'korean', price: 9000, spicy: 0, tags: ['soup', 'rice'] },
  { id: 'sundubu', name: '순두부찌개', emoji: '🍲', category: 'korean', price: 9500, spicy: 2, tags: ['soup', 'rice'] },
  { id: 'bibimbap', name: '비빔밥', emoji: '🥗', category: 'korean', price: 9500, spicy: 1, tags: ['rice', 'light'] },
  { id: 'jeyuk', name: '제육볶음', emoji: '🍖', category: 'korean', price: 10000, spicy: 2, tags: ['rice', 'hearty'] },
  { id: 'bulgogi', name: '불고기 백반', keyword: '불고기', emoji: '🥩', category: 'korean', price: 11000, spicy: 0, tags: ['rice', 'hearty'] },
  { id: 'gukbap', name: '돼지국밥', emoji: '🍜', category: 'korean', price: 10000, spicy: 0, tags: ['soup', 'rice', 'hearty'] },
  { id: 'galbitang', name: '갈비탕', emoji: '🍖', category: 'korean', price: 14000, spicy: 0, tags: ['soup', 'rice', 'hearty'] },
  { id: 'naengmyeon', name: '냉면', emoji: '🍜', category: 'korean', price: 11000, spicy: 1, tags: ['noodle', 'light'] },
  { id: 'kalguksu', name: '칼국수', emoji: '🍜', category: 'korean', price: 9000, spicy: 0, tags: ['noodle', 'soup'] },
  { id: 'dakgalbi', name: '닭갈비', emoji: '🍗', category: 'korean', price: 13000, spicy: 2, tags: ['rice', 'hearty'] },
  { id: 'samgyetang', name: '삼계탕', emoji: '🐔', category: 'korean', price: 16000, spicy: 0, tags: ['soup', 'hearty'] },
  { id: 'yukgaejang', name: '육개장', emoji: '🌶️', category: 'korean', price: 10000, spicy: 2, tags: ['soup', 'rice', 'hearty'] },
  { id: 'godeungeo', name: '고등어구이 정식', keyword: '고등어구이', emoji: '🐟', category: 'korean', price: 11000, spicy: 0, tags: ['rice'] },

  // 중식
  { id: 'jjajangmyeon', name: '짜장면', emoji: '🍝', category: 'chinese', price: 7000, spicy: 0, tags: ['noodle', 'quick'] },
  { id: 'jjamppong', name: '짬뽕', emoji: '🌶️', category: 'chinese', price: 9000, spicy: 2, tags: ['noodle', 'soup'] },
  { id: 'bokkeumbap', name: '볶음밥', emoji: '🍛', category: 'chinese', price: 8000, spicy: 0, tags: ['rice', 'quick'] },
  { id: 'tangsuyuk', name: '탕수육 세트', keyword: '탕수육', emoji: '🍤', category: 'chinese', price: 12000, spicy: 0, tags: ['hearty'] },
  { id: 'mapa-dubu', name: '마파두부밥', keyword: '마파두부', emoji: '🫕', category: 'chinese', price: 9000, spicy: 2, tags: ['rice'] },
  { id: 'mala-tang', name: '마라탕', emoji: '🔥', category: 'chinese', price: 12000, spicy: 3, tags: ['soup', 'noodle'] },

  // 일식
  { id: 'donkatsu', name: '돈카츠', emoji: '🍱', category: 'japanese', price: 11000, spicy: 0, tags: ['rice', 'hearty'] },
  { id: 'ramen', name: '라멘', emoji: '🍜', category: 'japanese', price: 10000, spicy: 0, tags: ['noodle', 'soup', 'hearty'] },
  { id: 'udon', name: '우동', emoji: '🍜', category: 'japanese', price: 8000, spicy: 0, tags: ['noodle', 'soup', 'light'] },
  { id: 'sushi', name: '초밥', emoji: '🍣', category: 'japanese', price: 15000, spicy: 0, tags: ['rice', 'light'] },
  { id: 'gyudon', name: '규동', emoji: '🍚', category: 'japanese', price: 9000, spicy: 0, tags: ['rice', 'quick'] },
  { id: 'soba', name: '메밀소바', emoji: '🥢', category: 'japanese', price: 9000, spicy: 0, tags: ['noodle', 'light'] },
  { id: 'kaisendon', name: '사케동', emoji: '🐟', category: 'japanese', price: 14000, spicy: 0, tags: ['rice', 'light'] },

  // 양식
  { id: 'pasta', name: '파스타', emoji: '🍝', category: 'western', price: 14000, spicy: 0, tags: ['noodle'] },
  { id: 'burger', name: '수제버거', emoji: '🍔', category: 'western', price: 12000, spicy: 0, tags: ['hearty', 'quick'] },
  { id: 'pizza', name: '피자', emoji: '🍕', category: 'western', price: 13000, spicy: 0, tags: ['hearty'] },
  { id: 'salad', name: '샐러드', emoji: '🥗', category: 'western', price: 11000, spicy: 0, tags: ['light', 'quick'] },
  { id: 'sandwich', name: '샌드위치', emoji: '🥪', category: 'western', price: 8000, spicy: 0, tags: ['light', 'quick'] },
  { id: 'risotto', name: '리조또', emoji: '🍚', category: 'western', price: 14000, spicy: 0, tags: ['rice'] },
  { id: 'steak-bowl', name: '스테이크 덮밥', keyword: '스테이크덮밥', emoji: '🥩', category: 'western', price: 13000, spicy: 0, tags: ['rice', 'hearty'] },

  // 분식
  { id: 'tteokbokki', name: '떡볶이', emoji: '🍢', category: 'snack', price: 6000, spicy: 2, tags: ['quick'] },
  { id: 'gimbap', name: '김밥', emoji: '🍙', category: 'snack', price: 4500, spicy: 0, tags: ['rice', 'quick', 'light'] },
  { id: 'ramyeon', name: '라면', emoji: '🍜', category: 'snack', price: 5000, spicy: 1, tags: ['noodle', 'soup', 'quick'] },
  { id: 'rabokki', name: '라볶이', emoji: '🌶️', category: 'snack', price: 7000, spicy: 2, tags: ['noodle', 'quick'] },
  { id: 'omurice', name: '오므라이스', emoji: '🍳', category: 'snack', price: 8000, spicy: 0, tags: ['rice'] },
  { id: 'jjolmyeon', name: '쫄면', emoji: '🥢', category: 'snack', price: 7000, spicy: 2, tags: ['noodle', 'light'] },

  // 아시안
  { id: 'pho', name: '쌀국수', emoji: '🍜', category: 'asian', price: 10000, spicy: 0, tags: ['noodle', 'soup', 'light'] },
  { id: 'pad-thai', name: '팟타이', emoji: '🍤', category: 'asian', price: 11000, spicy: 1, tags: ['noodle'] },
  { id: 'curry', name: '카레', emoji: '🍛', category: 'asian', price: 9000, spicy: 1, tags: ['rice', 'hearty'] },
  { id: 'nasi-goreng', name: '나시고렝', emoji: '🍳', category: 'asian', price: 11000, spicy: 1, tags: ['rice'] },
  { id: 'bun-cha', name: '분짜', emoji: '🥢', category: 'asian', price: 12000, spicy: 0, tags: ['noodle', 'light'] },
  { id: 'tom-yum', name: '똠얌꿍', emoji: '🦐', category: 'asian', price: 13000, spicy: 3, tags: ['soup'] },
];

module.exports = { CATEGORIES, TAGS, MENUS };
