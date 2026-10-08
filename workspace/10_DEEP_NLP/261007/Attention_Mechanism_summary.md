# Attention Mechanism

## 요약

- 출력의 각 위치에서 입력 전체 중 관련성이 높은 위치의 정보를 선택적으로 반영하는 연산
- Query와 Key의 유사도로 Attention Score 계산
- Softmax로 Score를 정규화해 Attention 가중치 산출
- 가중치로 Value를 가중합해 최종 출력 생성
- Self-Attention은 Query, Key, Value를 모두 같은 시퀀스에서 생성해 시퀀스 내부 관계를 학습하는 형태

## 1. Self-Attention

### 정의

- 하나의 시퀀스 안에서 각 토큰이 같은 시퀀스의 모든 토큰과의 관련성을 계산하는 Attention
- Query, Key, Value가 모두 동일한 입력 시퀀스에서 생성
- 각 토큰의 출력 표현에 시퀀스 전체의 문맥 정보 반영

### 인코더-디코더 Attention과의 차이

- 인코더-디코더 Attention: Query는 디코더, Key와 Value는 인코더에서 생성
- 인코더-디코더 Attention의 목적: 출력 시퀀스와 입력 시퀀스 사이의 대응 관계 학습
- Self-Attention의 목적: 같은 시퀀스 내부 토큰 간의 의존 관계 학습

### RNN 대비 특징

- 순환 구조 없이 모든 위치를 동시에 계산해 병렬 처리 가능
- 임의의 두 위치가 한 번의 연산으로 직접 연결
- 거리가 먼 토큰 간 의존 관계도 정보 손실 없이 학습 가능
- 순서 정보가 연산 자체에 포함되지 않아 위치 인코딩(Positional Encoding) 별도 필요

### 변형

- Masked Self-Attention: 디코더에서 현재 위치 이후의 토큰을 참조하지 못하도록 차단
- Multi-Head Attention: Query, Key, Value를 여러 개의 부분 공간으로 나누어 병렬로 Attention 수행 후 결합
- Multi-Head 구조로 서로 다른 유형의 관계를 동시에 학습

## 2. Attention Scores

### 정의

- 특정 Query가 각 Key와 얼마나 관련 있는지 나타내는 값
- Query 하나당 Key 개수만큼의 Score 산출
- Score가 클수록 해당 위치의 Value가 출력에 크게 반영

### 계산 방식

- Additive Attention (Bahdanau): Query와 Key를 각각 선형 변환 후 더하고 tanh와 선형 층을 거쳐 Score 산출
- Dot-Product Attention (Luong): Query와 Key의 내적을 Score로 사용
- Scaled Dot-Product Attention (Transformer): 내적 결과를 Key 차원의 제곱근으로 나눈 값을 Score로 사용

### 스케일링이 필요한 이유

- Query와 Key의 차원이 커질수록 내적 값의 분산 증가
- 큰 Score가 Softmax에 입력되면 출력이 한 위치에 극단적으로 집중
- Softmax 포화 구간에서 기울기가 매우 작아져 학습 불안정
- Key 차원의 제곱근으로 나누어 Score 분산을 일정 수준으로 유지

### Softmax 정규화

- Score를 Softmax에 통과시켜 Attention 가중치로 변환
- 모든 가중치는 0 이상, 가중치 합은 1
- 가중치를 Query 기준의 확률 분포로 해석 가능

### 마스킹(Masking)

- Softmax 이전에 참조하지 않을 위치의 Score를 음의 무한대로 설정
- 해당 위치의 가중치가 0이 되어 출력에서 제외
- Padding Mask: 길이를 맞추기 위해 추가한 패딩 토큰 제외
- Look-Ahead Mask: 디코더에서 미래 시점 토큰 제외

## 3. Query, Key, Value

### 각 요소의 역할

- Query: Score 계산의 기준이 되는 벡터, 현재 출력을 계산하는 위치의 표현
- Key: Query와 비교되는 벡터, 각 위치가 Query와 얼마나 관련 있는지 판단하는 데 사용
- Value: 가중합에 실제로 사용되는 정보 벡터, 출력에 전달되는 내용

### 생성 방식

- 입력 벡터에 서로 다른 학습 가능한 가중치 행렬을 곱해 Query, Key, Value 생성
- 세 가중치 행렬은 학습을 통해 함께 갱신
- 동일한 입력에서 비교용 표현과 전달용 표현을 분리해 학습
- Query와 Key는 내적을 위해 같은 차원 필요, Value 차원은 독립적으로 설정 가능

### 역할 분리의 의미

- 관련성 판단에 필요한 특징과 실제로 전달할 정보의 특징을 서로 다르게 학습 가능
- 같은 토큰이라도 Query로 쓰일 때와 Key로 쓰일 때 다른 표현 사용
- 단일 표현으로 비교와 전달을 모두 수행하는 방식보다 표현력 향상

### Bahdanau Attention과의 대응

- Query: 디코더의 직전 은닉 상태
- Key: 인코더의 annotation
- Value: 인코더의 annotation
- Bahdanau 구조는 Key와 Value가 동일한 특수한 형태

## 4. Weighted Sum

### 정의

- 각 Value에 해당 위치의 Attention 가중치를 곱한 뒤 모두 더하는 연산
- 결과 벡터가 Attention의 최종 출력
- 인코더-디코더 Attention에서는 이 결과를 Context Vector로 사용

### 행렬 형태의 전체 연산

- Attention(Q, K, V) = softmax(QKᵀ / √d_k) V
- QKᵀ: 모든 Query와 모든 Key 사이의 Score 행렬
- √d_k로 나누기: Score 스케일링
- softmax: 행 단위 가중치 정규화
- V와의 곱: 모든 Query에 대한 가중합을 한 번에 계산

### 특징

- 가장 관련 있는 위치 하나만 선택하는 방식이 아닌 모든 위치를 비율에 따라 반영하는 soft selection
- 연산 전체가 미분 가능해 역전파로 Query, Key, Value 가중치 학습 가능
- 출력 개수는 Query 개수와 동일
- 입력 길이와 관계없이 출력 벡터 차원은 Value 차원으로 고정

### 계산량

- 모든 Query와 모든 Key 쌍에 대해 Score 계산
- 시퀀스 길이의 제곱에 비례하는 계산량과 메모리 사용량
- 긴 시퀀스 처리 시 주요 제약 요인

## 전체 연산 흐름

- 입력 벡터를 선형 변환해 Query, Key, Value 생성
- Query와 Key로 Attention Score 계산
- Score 스케일링과 마스킹 적용
- Softmax로 Attention 가중치 산출
- 가중치로 Value를 가중합해 출력 생성

## 의의

- 고정 길이 벡터 하나에 입력을 압축하던 인코더-디코더 구조의 정보 병목 해소
- Query-Key-Value 구조로 Attention을 범용 연산으로 일반화
- Self-Attention으로 순환 구조 없이 시퀀스를 처리하는 Transformer 등장
- 이후 BERT, GPT 등 사전학습 언어 모델의 핵심 연산
- Attention 가중치 시각화를 통해 모델이 참조한 위치 해석 가능
