# 과제 2-1 정답: 기초 방법론으로 상품 설명 프롬프트 개선 + JSON 파싱 검증
import json
import re
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()
MODEL = "gpt-6-luna"

products = [
    "텀블러 | 스테인리스 이중 진공, 500ml, 보온 12시간 | 29,000원",
    "러닝화 | 무게 220g, 쿠셔닝 폼, 통기성 메쉬 | 119,000원",
    "탁상용 가습기 | 초음파 방식, 300ml, 무드등, USB 전원 | 25,000원",
]

BASELINE = "이 제품 설명 써줘: {p}"

IMPROVED_SYSTEM = "당신은 10년 차 이커머스 상품 기획자입니다. 과장 없이 사실 기반으로 작성하고, 주어진 정보에 없는 내용은 만들지 않습니다."
IMPROVED_USER = """<product> 태그 안의 정보로 상품 상세페이지 문구를 작성해줘.
- title: 20자 이내
- summary: 1문장
- features: 핵심 특징 정확히 3개 (각 15자 이내)
- target: 추천 대상 1문장
반드시 아래 JSON 형식으로만 답해. 코드블록이나 다른 설명은 쓰지 마.
{{"title": "", "summary": "", "features": ["", "", ""], "target": ""}}

<product>{p}</product>"""

REQUIRED = {"title", "summary", "features", "target"}

def parse_json(text):
    """```json 코드블록이 섞여 와도 파싱되도록 정리 후 json.loads"""
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    return json.loads(cleaned)

def validate(data):
    """형식 검증: 필수 키 · features 3개 · title 20자 이내"""
    errors = []
    if set(data) != REQUIRED:
        errors.append(f"keys={sorted(data)}")
    if not isinstance(data.get("features"), list) or len(data["features"]) != 3:
        errors.append("features != 3")
    if len(str(data.get("title", ""))) > 20:
        errors.append("title > 20자")
    return errors

rows = []
for p in products:
    base = client.responses.create(model=MODEL, input=BASELINE.format(p=p))
    imp = client.responses.create(model=MODEL, instructions=IMPROVED_SYSTEM, input=IMPROVED_USER.format(p=p))
    try:
        data = parse_json(imp.output_text)
        errors = validate(data)
    except json.JSONDecodeError:
        data, errors = None, ["JSON 파싱 실패"]
    rows.append({
        "product": p.split(" | ")[0],
        "base_out_tok": base.usage.output_tokens,
        "imp_out_tok": imp.usage.output_tokens,
        "parsed": data is not None,
        "valid": data is not None and not errors,
        "errors": ", ".join(errors),
        "title": data["title"] if data else None,
    })

df = pd.DataFrame(rows)
print(df)
print(f"\n형식 준수율: {df['valid'].mean():.0%}")
