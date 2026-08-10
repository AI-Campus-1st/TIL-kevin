### 1. 쇼핑몰 서비스 database 및 회원, 상품 테이블 생성과 구조 변경

#### 정답
```sql
CREATE DATABASE IF NOT EXISTS shopping_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE shopping_db;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    price INT NOT NULL DEFAULT 0,
    stock_quantity INT NOT NULL DEFAULT 0
);

ALTER TABLE users ADD COLUMN phone VARCHAR(20);
```

#### 해설

- `CREATE DATABASE`문으로 DB를 생성하고 `USE`로 활성화합니다. 
- CREATE TABLE 구문에서 `PRIMARY KEY`,` AUTO_INCREMENT`, `NOT NULL`, `UNIQUE`, `DEFAULT` 제약조건을 지정하여 데이터 무결성을 보장합니다. 
- 기존 테이블에 새 컬럼을 추가할 때에는 `ALTER TABLE [테이블명] ADD COLUMN [컬럼명] [데이터타입];` 구문을 사용합니다.

### 2. 쇼핑몰 초기 테스트 데이터 등록, 수정 및 삭제

#### 정답
```sql
USE shopping_db;

INSERT INTO users (username, email, phone) VALUES
    ('김철수', 'chulsoo@test.com', NULL),
    ('이영희', 'younghee@test.com', '010-9876-5432'),
    ('박민수', 'minsu@test.com', '010-5555-4444');

INSERT INTO products (product_name, price, stock_quantity) VALUES
    ('무선 마우스', 25000, 50),
    ('기계식 키보드', 89000, 30),
    ('4K 모니터', 350000, 10),
    ('USB 허브', 15000, 100);

UPDATE users 
SET phone = '010-1234-5678' 
WHERE email = 'chulsoo@test.com';

DELETE FROM products 
WHERE product_name = 'USB 허브';
```

#### 해설

- `INSERT INTO`문에서 다중 레코드 다변량 콤마(`,`) 구문을 사용해 한 번에 여러 행을 삽입할 수 있습니다. 
- `UPDATE`와 `DELETE` 구문 실행 시 타겟 행만 정확히 변경/삭제되도록 WHERE 절 조건을 명확하게 기술하는 것이 매우 중요합니다.

### 3. DISTINCT, ORDER BY, LIMIT을 활용한 기초 SELECT 쿼리 작성

#### 정답

```sql
USE shopping_db;

-- 1. 중복 제거하여 고유 재고 수량 조회
SELECT DISTINCT stock_quantity 
FROM products;

-- 2. 상품 가격 내림차순 정렬 조회
SELECT product_name, price 
FROM products 
ORDER BY price DESC;

-- 3. 회원 번호 내림차순 정렬 후 상위 2명 회원 조회
SELECT * 
FROM users 
ORDER BY user_id DESC 
LIMIT 2;
```

#### 해설

- `DISTINCT` 키워드를 사용하면 조회 결과에서 중복 데이터를 제거하고 고유한 값만 추출할 수 있습니다. 
- `ORDER BY 컬럼명 DESC` 구문은 지정한 컬럼 기준 내림차순 정렬을 수행하며, `LIMIT N` 구문을 조합하여 정렬 결과 중 상위 N개의 행만 선별하여 출력할 수 있습니다.