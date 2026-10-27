# 과제 2-3 정답: Few-shot으로 다중 필드 JSON 추출 일관성 높이기
import json
import re
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()
MODEL = "gpt-6-luna"

CATEGORIES = ["배송", "결제", "상품", "계정"]

tests = [  # (메시지, 정답 category, 정답 urgency)
    ("결제가 두 번 됐어요. 빨리 취소해주세요!!", "결제", "high"),
    ("비밀번호 변경은 어디서 하나요?", "계정", "low"),
    ("주문한 지 열흘인데 아직도 안 왔어요. 내일 여행 가야 하는데요", "배송", "high"),
    ("이 셔츠 면 100%인가요?", "상품", "low"),
    ("배송지를 회사로 바꿀 수 있을까요? 모레 도착 예정이에요", "배송", "medium"),
    ("카드 할부 결제도 가능한가요?", "결제", "low"),
]

ZERO = """고객 메시지를 분석해서 JSON으로 답해.
category는 {cats} 중 하나, urgency는 low / medium / high 중 하나.
형식: {{"category": "", "urgency": "", "summary": ""}}

메시지: {m}"""

FEW = """고객 메시지를 분석해서 JSON으로만 답해.
category는 {cats} 중 하나, urgency는 low / medium / high 중 하나.
urgency 기준: 금전 피해 · 일정 임박 = high, 처리 요청 = medium, 단순 문의 = low

메시지: 쿠폰이 적용이 안 돼요
{{"category": "결제", "urgency": "medium", "summary": "쿠폰 적용 오류"}}

메시지: 탈퇴하면 적립금은 어떻게 되나요?
{{"category": "계정", "urgency": "low", "summary": "탈퇴 시 적립금 처리 문의"}}

메시지: 택배가 파손돼서 왔는데 오늘 선물해야 해요
{{"category": "배송", "urgency": "high", "summary": "파손 배송, 당일 선물 일정"}}

메시지: {m}"""

def parse_json(text):
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    return json.loads(cleaned)

rows = []
for name, tpl in [("zero", ZERO), ("few", FEW)]:
    for m, cat, urg in tests:
        r = client.responses.create(model=MODEL, input=tpl.format(cats=CATEGORIES, m=m))
        try:
            d = parse_json(r.output_text)
            fmt_ok = set(d) == {"category", "urgency", "summary"} and d["category"] in CATEGORIES \
                and d["urgency"] in ("low", "medium", "high")
        except json.JSONDecodeError:
            d, fmt_ok = {}, False
        rows.append({
            "prompt": name, "message": m, "format_ok": fmt_ok,
            "category_ok": d.get("category") == cat, "urgency_ok": d.get("urgency") == urg,
            "pred": d, "in_tok": r.usage.input_tokens,
        })

df = pd.DataFrame(rows)
print(df.groupby("prompt")[["format_ok", "category_ok", "urgency_ok", "in_tok"]].mean().round(2))
