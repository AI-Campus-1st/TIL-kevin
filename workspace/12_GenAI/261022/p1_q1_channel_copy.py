# 과제 1-1 정답: 채널별 홍보 문구 생성기와 비용 리포트
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()
MODEL = "gpt-6-luna"
PRICE = {"input": 0.10, "output": 0.50}  # USD / 1M tokens (gpt-6-luna, Standard)
USD_KRW = 1350

product = "무선 이어폰 SOSIN Buds — 노이즈 캔슬링, 배터리 30시간, 무게 4.5g, 가격 89,000원"

channels = {
    "인스타그램": ("당신은 SNS 마케터입니다. 이모지와 해시태그 3개를 포함해 2문장으로 작성하세요.", 120),
    "보도자료": ("당신은 홍보팀 기자입니다. 객관적인 문체로 수치를 포함해 4문장 이내로 작성하세요.", 300),
    "사내공지": ("당신은 사내 커뮤니케이션 담당자입니다. 임직원 대상 존댓말로 3문장 이내로 작성하세요.", 200),
}


def cost_usd(usage):
    return (usage.input_tokens * PRICE["input"] + usage.output_tokens * PRICE["output"]) / 1_000_000


rows = []
for name, (instructions, max_tok) in channels.items():
    r = client.responses.create(
        model=MODEL,
        instructions=instructions,
        input=f"다음 제품의 홍보 문구를 작성해줘.\n{product}",
        max_output_tokens=max_tok,
        reasoning={"effort": "none"},
    )
    rows.append({
        "channel": name,
        "status": r.status,  # incomplete면 max_output_tokens에 걸려 잘린 것
        "in_tok": r.usage.input_tokens,
        "out_tok": r.usage.output_tokens,
        "cost_usd": round(cost_usd(r.usage), 6),
        "text": r.output_text,
    })

df = pd.DataFrame(rows)
df["cost_krw"] = (df["cost_usd"] * USD_KRW).round(3)
print(df[["channel", "status", "in_tok", "out_tok", "cost_usd", "cost_krw"]])
print(f"\n총 비용: ${df['cost_usd'].sum():.6f} (약 {df['cost_krw'].sum():.2f}원)")
for _, row in df.iterrows():
    print(f"\n[{row['channel']}]\n{row['text']}")
