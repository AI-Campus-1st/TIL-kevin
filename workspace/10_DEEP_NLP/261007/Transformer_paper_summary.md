# Attention Is All You Need (Transformer)

## 논문 정보

- 저자: Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, Illia Polosukhin (Google Brain, Google Research, University of Toronto)
- 발표: NIPS 2017
- 제안 모델: Transformer

## 요약

- 순환 구조(RNN)와 합성곱(CNN)을 완전히 제거하고 Attention만으로 구성한 시퀀스 변환 모델 제안
- 인코더와 디코더 모두 Self-Attention과 위치별 피드포워드 신경망을 쌓은 구조
- 순서 정보는 Positional Encoding으로 입력 임베딩에 직접 추가
- 시퀀스 위치를 순차적으로 계산하지 않아 학습 병렬화가 크게 향상
- 영어-독일어, 영어-프랑스어 번역에서 기존 최고 성능을 갱신하면서 학습 비용은 대폭 감소

## 1. Attention is All You Need

### 기존 시퀀스 모델의 한계

- RNN 계열 모델은 이전 시점의 은닉 상태를 받아 다음 시점을 계산하는 순차 구조
- 시퀀스 길이가 길어질수록 학습 시 병렬 처리가 어렵고 메모리 제약으로 배치 크기 제한
- 기존 Attention은 대부분 RNN과 결합된 보조 장치로 사용
- CNN 기반 모델(ByteNet, ConvS2S)은 병렬화가 가능하지만 먼 위치 간 관계를 학습하려면 여러 층이 필요

### 제안 방향

- 입력과 출력 사이의 전역적 의존 관계를 Attention만으로 학습
- 순환과 합성곱 없이 시퀀스 변환이 가능함을 최초로 입증
- 논문 제목은 Attention 하나만으로 충분하다는 핵심 주장

### 전체 구조

- 인코더-디코더 구조 유지
- 인코더: 동일한 층을 여러 개 쌓은 구조, 각 층은 Multi-Head Self-Attention과 위치별 피드포워드 신경망으로 구성
- 디코더: 인코더 층 구성에 인코더 출력을 참조하는 인코더-디코더 Attention을 추가한 구조
- 모든 하위 층에 잔차 연결(residual connection)과 층 정규화(layer normalization) 적용
- 위치별 피드포워드 신경망: 각 위치에 동일한 두 개의 선형 변환과 ReLU를 독립적으로 적용
- 입력 임베딩, 출력 임베딩, Softmax 이전 선형 변환이 가중치 행렬 공유

### Transformer 내 Attention의 세 가지 사용 방식

- 인코더 Self-Attention: 입력 문장 내 모든 위치가 서로를 참조
- 디코더 Masked Self-Attention: 출력 문장에서 현재 위치까지만 참조, 이후 위치는 마스킹
- 인코더-디코더 Attention: Query는 디코더, Key와 Value는 인코더 출력에서 생성

## 2. Self-Attention

### Scaled Dot-Product Attention

- Query와 Key의 내적으로 관련도 점수 계산
- 내적 결과를 Key 차원의 제곱근으로 나누어 스케일링
- Softmax로 가중치를 구한 뒤 Value를 가중합
- 내적 기반 연산이어서 행렬 곱으로 효율적 구현 가능
- 스케일링 이유: 차원이 클 때 내적 값이 커져 Softmax 기울기가 매우 작아지는 문제 방지

### Multi-Head Attention

- Query, Key, Value를 서로 다른 학습 가능한 선형 변환으로 여러 번 투영
- 투영된 각 부분 공간에서 Attention을 병렬로 수행
- 각 head의 출력을 연결(concatenate)한 뒤 다시 선형 변환
- 서로 다른 위치와 서로 다른 표현 부분 공간의 정보를 동시에 반영
- head마다 차원을 줄여 전체 계산량은 단일 head Attention과 비슷한 수준 유지
- 단일 head는 가중 평균 과정에서 정보가 평탄화되는 문제가 있으며 Multi-Head 구조로 이를 완화

### Self-Attention을 선택한 이유

- 층당 계산 복잡도: 시퀀스 길이가 표현 차원보다 작은 일반적인 번역 과제에서 RNN보다 효율적
- 순차 연산 수: 시퀀스 길이와 관계없이 상수, RNN은 시퀀스 길이에 비례
- 최대 경로 길이: 임의의 두 위치가 한 번의 연산으로 직접 연결되어 장거리 의존 관계 학습에 유리
- 부가 효과: Attention 가중치 분포를 통해 모델의 동작 해석 가능, 일부 head는 문장의 구문·의미 구조와 관련된 패턴 학습

## 3. Positional Encoding

### 필요성

- Self-Attention은 입력 순서를 바꿔도 연산 결과가 위치만 바뀌는 순서 무관(permutation invariant) 연산
- 순환과 합성곱이 없으므로 토큰의 순서 정보를 별도로 주입해야 함

### 적용 방식

- 입력 임베딩과 같은 차원의 위치 벡터를 생성해 임베딩에 더함
- 인코더와 디코더 스택의 가장 아래쪽 입력에 적용

### Sinusoidal Positional Encoding

- 위치와 차원 인덱스를 입력으로 하는 사인, 코사인 함수로 위치 벡터 생성
- 짝수 차원은 사인, 홀수 차원은 코사인 사용
- 차원마다 주파수가 다르며 낮은 차원은 빠르게, 높은 차원은 느리게 변하는 파형
- 고정된 함수로 계산하므로 학습 파라미터가 없음

### Sinusoidal 방식을 선택한 이유

- 일정 거리만큼 떨어진 위치의 인코딩을 현재 위치 인코딩의 선형 변환으로 표현 가능
- 모델이 상대적 위치 관계를 쉽게 학습할 수 있는 구조
- 학습 중 보지 못한 더 긴 시퀀스에도 적용 가능성 존재
- 학습 가능한 위치 임베딩과 비교 실험 결과 성능은 거의 동일

## 4. Parallel Processing

### RNN의 순차 계산 문제

- 현재 시점 계산에 이전 시점의 은닉 상태가 필요해 시점 단위 병렬화 불가
- 시퀀스 길이에 비례하는 순차 연산 필요
- 긴 시퀀스일수록 학습 시간 증가

### Transformer의 병렬 처리

- Self-Attention은 시퀀스의 모든 위치를 행렬 연산 한 번으로 동시에 계산
- 위치별 피드포워드 신경망도 위치 간 의존 없이 독립적으로 계산
- 학습 시 디코더도 Masked Self-Attention과 Teacher Forcing으로 모든 출력 위치를 동시에 계산
- GPU의 대규모 행렬 연산에 적합한 구조

### 추론 시 특성

- 디코더는 추론 시 이전에 생성한 토큰을 입력으로 받아 한 토큰씩 생성하는 자기회귀(auto-regressive) 방식 유지
- 병렬화 이점은 주로 학습 과정과 인코더 연산에서 발생

### 한계와 제안

- 모든 위치 쌍의 관계를 계산하므로 시퀀스 길이의 제곱에 비례하는 계산량
- 매우 긴 시퀀스에서는 각 위치 주변의 제한된 범위만 참조하는 restricted Self-Attention을 향후 연구 방향으로 제시

## 결과

- 영어-독일어 번역에서 앙상블 모델을 포함한 기존 최고 성능 갱신
- 영어-프랑스어 번역에서 단일 모델 기준 최고 성능 달성
- 기존 최고 성능 모델 대비 일부 수준의 학습 비용으로 더 높은 성능 확보
- 영어 구문 분석(constituency parsing)에도 적용해 과제 특화 조정 없이 우수한 성능 확인
- 구성 요소 변형 실험 결과
  - head 수가 너무 적거나 너무 많으면 성능 저하
  - Key 차원 축소 시 성능 저하
  - 모델 크기 증가 시 성능 향상
  - dropout이 과적합 방지에 효과적
  - Sinusoidal 위치 인코딩과 학습 가능한 위치 임베딩의 성능 차이 거의 없음

## 의의

- 순환 구조 없이 Attention만으로 시퀀스를 처리하는 Transformer 구조 제안
- 학습 병렬화로 대규모 데이터와 대규모 모델 학습 가능
- BERT(인코더 기반), GPT(디코더 기반) 등 사전학습 언어 모델의 기반 구조
- 이후 이미지, 음성 등 텍스트 이외 분야로 Transformer 확산
- Seq2Seq, Bahdanau Attention으로 이어진 연구 흐름에서 RNN을 완전히 대체하는 전환점
