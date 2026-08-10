### 1. SELECT문 연습

#### 정답
```sql

-- A1.
SELECT customer_name, grade FROM tb_customer WHERE city = '서울';
-- A2.
SELECT * FROM tb_customer WHERE customer_name LIKE '이%';
-- A3.
SELECT * FROM tb_product WHERE unit_price BETWEEN 5000 AND 50000 ORDER BY unit_price;
-- A4.
SELECT COUNT(*) FROM tb_order WHERE order_dt >= '2024-04-01' AND order_dt < '2024-07-01';
-- A5.
SELECT * FROM tb_customer WHERE grade IS NULL;

-- A6.  
SELECT cat.category_name, COUNT(*) AS cnt, ROUND(AVG(p.unit_price)) AS avg_price
FROM tb_product p 
    JOIN tb_category cat ON p.category_id = cat.category_id
GROUP BY cat.category_name 
ORDER BY avg_price DESC;

-- A7.  
SELECT IFNULL(grade,'미지정') AS grade, COUNT(*) AS cnt,
    ROUND(COUNT(*)/(SELECT COUNT(*) FROM tb_customer)*100,1) AS pct
FROM tb_customer 
GROUP BY IFNULL(grade,'미지정') 
ORDER BY cnt DESC;

-- A8.  
SELECT DATE_FORMAT(order_dt,'%Y-%m') AS ym, COUNT(*) AS cnt
FROM tb_order 
WHERE status <> 'CANCELED'
GROUP BY DATE_FORMAT(order_dt,'%Y-%m') 
ORDER BY ym;

-- A9.  
SELECT cat.category_name, SUM(p.stock_qty) AS stock
FROM tb_product p 
    JOIN tb_category cat ON p.category_id = cat.category_id
GROUP BY cat.category_name 
HAVING SUM(p.stock_qty) < 100;

-- A10. 
SELECT MAX(unit_price) - MIN(unit_price) AS gap FROM tb_product;

-- A11. 
SELECT o.order_id, c.customer_name, o.order_dt, SUM(i.qty*i.unit_price) AS amount
FROM tb_order o 
    JOIN tb_customer c ON o.customer_id=c.customer_id
    JOIN tb_order_item i ON o.order_id=i.order_id
GROUP BY o.order_id, c.customer_name, o.order_dt 
ORDER BY o.order_id;

-- A12. 
SELECT c.* 
FROM tb_customer c 
    LEFT JOIN tb_order o ON c.customer_id=o.customer_id
WHERE o.order_id IS NULL;

-- A13. 
SELECT p.* 
FROM tb_product p 
    LEFT JOIN tb_order_item i ON p.product_id=i.product_id
WHERE i.order_item_id IS NULL;

-- A14. 
SELECT c.customer_name, SUM(i.qty*i.unit_price) AS amount
FROM tb_customer c 
    JOIN tb_order o ON c.customer_id=o.customer_id
    JOIN tb_order_item i ON o.order_id=i.order_id
WHERE o.status <> 'CANCELED'
GROUP BY c.customer_id, c.customer_name 
ORDER BY amount DESC 
LIMIT 5;

-- A15. 
SELECT c.country, cat.category_name, SUM(i.qty*i.unit_price) AS amount
FROM tb_customer c 
    JOIN tb_order o ON c.customer_id=o.customer_id
    JOIN tb_order_item i ON o.order_id=i.order_id
    JOIN tb_product p ON p.poroduct_id = i.product_id
    JOIN tb_category cat ON p.category_id=cat.category_id
-- WHERE o.status <> 'CANCELED'
GROUP BY c.country, cat.category_id
ORDER BY amount DESC;

-- A16. 
SELECT cat.category_name, COUNT(*) AS cnt,
    CASE WHEN COUNT(*) > 3 THEN '많음' ELSE '적음' END AS lvl
FROM tb_product p 
    JOIN tb_category cat ON p.category_id=cat.category_id
GROUP BY cat.category_name 
ORDER BY cnt DESC;

-- A17. 
SELECT 
    CASE 
        WHEN cnt = 0 THEN '0건' 
        WHEN cnt <= 2 THEN '1~2건'
        ELSE '3건 이상' 
    END AS bucket, COUNT(*) AS customers
FROM (
    SELECT c.customer_id, COUNT(o.order_id) AS cnt
    FROM tb_customer c 
        LEFT JOIN tb_order o ON c.customer_id=o.customer_id
    GROUP BY c.customer_id
    ) t
GROUP BY bucket;

-- A18.
SELECT YEAR(o.order_dt) AS yr,
    SUM(CASE WHEN MONTH(o.order_dt)=1 THEN i.qty*i.unit_price ELSE 0 END) AS m01,
    SUM(CASE WHEN MONTH(o.order_dt)=2 THEN i.qty*i.unit_price ELSE 0 END) AS m02,
    SUM(CASE WHEN MONTH(o.order_dt)=3 THEN i.qty*i.unit_price ELSE 0 END) AS m03,
    SUM(CASE WHEN MONTH(o.order_dt)=4 THEN i.qty*i.unit_price ELSE 0 END) AS m04,
    SUM(CASE WHEN MONTH(o.order_dt)=5 THEN i.qty*i.unit_price ELSE 0 END) AS m05,
    SUM(CASE WHEN MONTH(o.order_dt)=6 THEN i.qty*i.unit_price ELSE 0 END) AS m06,
    SUM(CASE WHEN MONTH(o.order_dt)=7 THEN i.qty*i.unit_price ELSE 0 END) AS m07,
    SUM(CASE WHEN MONTH(o.order_dt)=8 THEN i.qty*i.unit_price ELSE 0 END) AS m08,
    SUM(CASE WHEN MONTH(o.order_dt)=9 THEN i.qty*i.unit_price ELSE 0 END) AS m09,
    SUM(CASE WHEN MONTH(o.order_dt)=10 THEN i.qty*i.unit_price ELSE 0 END) AS m10,
    SUM(CASE WHEN MONTH(o.order_dt)=11 THEN i.qty*i.unit_price ELSE 0 END) AS m11,
    SUM(CASE WHEN MONTH(o.order_dt)=12 THEN i.qty*i.unit_price ELSE 0 END) AS m12
FROM tb_order o 
    JOIN tb_order_item i ON o.order_id=i.order_id
WHERE o.status <> 'CANCELED' 
GROUP BY YEAR(o.order_dt);
```

```sql
-- =====================================================================
-- A19. 상품별 재고 소진율
-- =====================================================================
SELECT cat.category_name AS 카테고리,
    p.product_name AS 상품명,
    IFNULL(SUM(i.qty), 0) AS 판매수량,
    p.stock_qty AS 남은재고,
    ROUND(IFNULL(SUM(i.qty), 0)
        / (IFNULL(SUM(i.qty), 0) + p.stock_qty) * 100, 1) AS 소진율
FROM tb_product p
    JOIN tb_category cat ON p.category_id = cat.category_id
    LEFT JOIN tb_order_item i ON p.product_id = i.product_id
    LEFT JOIN tb_order o ON i.order_id = o.order_id AND o.status <> 'CANCELED'
GROUP BY p.product_id, cat.category_name, p.product_name, p.stock_qty
ORDER BY 소진율 DESC;
```

#### 해설

- 안 팔린 상품까지 나와야 합니다 → tb_product 를 왼쪽에 두고 LEFT JOIN
- 취소 조건은 ON 절에 작성합니다. WHERE 로 옮기면 주문 없는 상품이 사라집니다
- SUM 결과가 NULL 인 상품은 IFNULL 로 0 처리

```sql
-- =====================================================================
-- A20. 취소로 놓친 매출
-- =====================================================================
SELECT c.customer_name AS 고객명,
    c.country AS 국가,
    DATE(o.order_dt) AS 주문일,
    SUM(i.qty * i.unit_price) AS 취소금액,
    COUNT(*) AS 담긴상품수
FROM tb_order o
    JOIN tb_customer c ON o.customer_id = c.customer_id
    JOIN tb_order_item i ON o.order_id = i.order_id
WHERE o.status = 'CANCELED'
GROUP BY o.order_id, c.customer_name, c.country, DATE(o.order_dt)
ORDER BY 취소금액 DESC;

-- 취소 총액
SELECT COUNT(DISTINCT o.order_id) AS 취소건수,
       SUM(i.qty * i.unit_price) AS 취소총액
FROM tb_order o
    JOIN tb_order_item i ON o.order_id = i.order_id
WHERE o.status = 'CANCELED';
```

#### 해설
- "담긴 상품 개수"는 COUNT(*) — 상세 줄 수로

```sql
-- =====================================================================
-- A21. 등급별 1인당 구매액
-- =====================================================================
SELECT IFNULL(c.grade, '미지정') AS 등급,
    COUNT(DISTINCT c.customer_id) AS 인원수,
    COUNT(DISTINCT o.customer_id) AS 주문한인원,
    IFNULL(SUM(i.qty * i.unit_price), 0) AS 총매출,
    ROUND(IFNULL(SUM(i.qty * i.unit_price), 0)
            / COUNT(DISTINCT c.customer_id)) AS 일인당평균
FROM tb_customer c
    LEFT JOIN tb_order o ON c.customer_id = o.customer_id 
        AND o.status <> 'CANCELED'
    LEFT JOIN tb_order_item i ON o.order_id = i.order_id
GROUP BY IFNULL(c.grade, '미지정')
ORDER BY 일인당평균 DESC;
```

#### 해설

- 주문이 없는 고객도 분모에 넣어야 하므로 tb_customer 를 왼쪽에 두고 LEFT JOIN
- 취소 조건은 ON 절에 작성합니다. WHERE 로 옮기면 주문 없는 고객이 사라집니다
- COUNT(DISTINCT c.customer_id) = 등급 전체 인원
    - COUNT(DISTINCT o.customer_id) = 그중 실제로 산 사람 (LEFT JOIN 이라 NULL 은 안 세어짐)
    - 이 두 값의 차이가 곧 '아직 안 산 사람' 입니다
