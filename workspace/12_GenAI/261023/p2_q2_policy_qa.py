# 과제 2-2 정답: USER 템플릿 + 대체 경로로 정책 문서 Q&A (JSON 응답)
import json
import re
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()
MODEL = "gpt-6-luna"

POLICY = """[배송] 평일 오후 2시 이전 주문은 당일 출고, 이후 주문은 다음 영업일 출고. 제주 · 도서산간은 3,000원 추가.
[교환/반품] 수령 후 7일 이내 가능. 단순 변심은 왕복 배송비 6,000원 고객 부담, 제품 불량은 무료.
[환불] 반품 확인 후 카드 결제는 3~5영업일, 계좌이체는 1~2영업일 내 환불.
[적립금] 구매 확정 시 결제 금액의 1% 적립, 유효기간 1년."""

SYSTEM = """당신은 온라인 쇼핑몰 고객센터 상담원입니다.
- 반드시 # Context의 정책 내용만 근거로 답합니다.
- 정책에 근거가 없으면 추측하지 말고 answer에 "정책에서 확인할 수 없습니다"라고 쓰고 need_human을 true로 합니다.
- 정중한 존댓말, answer는 2문장 이내."""

USER_TEMPLATE = """다음 정보를 참고하여 고객 질문에 답하세요.
반드시 아래 JSON 형식으로만 답하세요.
{{"answer": "", "evidence": "근거가 된 정책 항목명 또는 null", "need_human": true/false}}

# Context
{context}

# Input Data
{question}"""

tests = [  # (질문, 정책으로 답변 가능 여부)
    ("오후 3시에 주문하면 언제 출고되나요?", True),
    ("단순 변심으로 반품하면 배송비는 얼마예요?", True),
    ("계좌이체로 결제했는데 환불 얼마나 걸려요?", True),
    ("해외 배송도 되나요?", False),
    ("적립금을 현금으로 바꿀 수 있나요?", False),
    ("회원 등급별 할인율이 궁금해요", False),
]

def parse_json(text):
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    return json.loads(cleaned)

rows = []
for q, answerable in tests:
    r = client.responses.create(
        model=MODEL, instructions=SYSTEM,
        input=USER_TEMPLATE.format(context=POLICY, question=q),
    )
    try:
        d = parse_json(r.output_text)
        correct = (d["need_human"] is False) if answerable else (d["need_human"] is True)
    except (json.JSONDecodeError, KeyError):
        d, correct = {"answer": r.output_text, "evidence": None, "need_human": None}, False
    rows.append({"question": q, "answerable": answerable, **d, "correct_routing": correct})

df = pd.DataFrame(rows)
print(df[["question", "answerable", "need_human", "evidence", "correct_routing"]])
print(f"\n라우팅 정확도: {df['correct_routing'].mean():.0%}")
hallucinated = df[(~df["answerable"]) & (df["need_human"] != True)]
print(f"정책에 없는 질문에 답을 지어낸 건수: {len(hallucinated)}")
