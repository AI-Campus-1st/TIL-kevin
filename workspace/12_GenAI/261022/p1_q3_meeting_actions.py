# 과제 1-3 정답: 회의록 액션 아이템 추출기 (Structured Outputs + 에러 처리)
import time
import openai
import pandas as pd
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()
MODEL = "gpt-6-luna"

class ActionItem(BaseModel):
    owner: str      # 담당자
    task: str       # 할 일
    due: str        # 기한 (없으면 "미정")

class MeetingResult(BaseModel):
    summary: str
    action_items: list[ActionItem]

def extract(text, retries=3):
    for i in range(retries):
        try:
            r = client.responses.parse(
                model=MODEL,
                instructions="회의록에서 요약 1문장과 액션 아이템을 추출하라. 기한이 없으면 '미정', 액션 아이템이 없으면 빈 리스트.",
                input=text,
                text_format=MeetingResult,
            )
            return r.output_parsed
        except openai.RateLimitError:
            time.sleep(2 ** i)                  # 지수 백오프 후 재시도
        except openai.APIConnectionError:
            time.sleep(2 ** i)
    return None                                 # 재시도 실패 시 None

meetings = {
    "주간회의_0922": "김대리: 신규 랜딩페이지 시안은 목요일까지 제가 공유할게요. 박과장: 광고 예산안은 다음 주 월요일까지 정리하겠습니다. 이팀장: 고객 인터뷰 일정은 추후 정하죠.",
    "개발회의_0923": "최개발: 로그인 버그는 오늘 중으로 수정합니다. 정QA: 수정되면 회귀 테스트를 수요일까지 진행할게요.",
    "잡담": "오늘 점심 뭐 먹을까요? 비가 와서 국물이 좋겠네요.",
}

rows = []
for name, text in meetings.items():
    result = extract(text)
    if result is None:
        print(f"[{name}] 추출 실패")
        continue
    print(f"[{name}] {result.summary} (액션 {len(result.action_items)}건)")
    for a in result.action_items:
        rows.append({"meeting": name, **a.model_dump()})

df = pd.DataFrame(rows, columns=["meeting", "owner", "task", "due"])
print(df)
df.to_csv("action_items.csv", index=False, encoding="utf-8-sig")
