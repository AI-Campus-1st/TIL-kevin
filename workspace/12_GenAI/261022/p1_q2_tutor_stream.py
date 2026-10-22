# 과제 1-2 정답: 스트리밍 영어 회화 튜터 (멀티턴 + 누적 토큰 추적)
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()
MODEL = "gpt-6-luna"

TUTOR = """You are a friendly English conversation tutor for Korean beginners.
- Reply in simple English within 2 sentences, then ask one follow-up question.
- If the user's sentence has a grammar mistake, add one line: '교정: <corrected sentence>'."""

prev_id = None
total_in = total_out = 0

while True:
    user = input("\n나: ").strip()
    if user.lower() in ("quit", "exit", "종료"):
        break
    stream = client.responses.create(
        model=MODEL,
        instructions=TUTOR,              # previous_response_id로 이어가도 instructions는 매번 전달
        input=user,
        previous_response_id=prev_id,
        stream=True,
    )
    print("튜터: ", end="")
    for event in stream:
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)
        elif event.type == "response.completed":  # 완료 이벤트에서 id · usage 획득
            prev_id = event.response.id
            total_in += event.response.usage.input_tokens
            total_out += event.response.usage.output_tokens
    print(f"\n(누적 토큰 — 입력 {total_in}, 출력 {total_out})")

print(f"\n대화 종료. 총 입력 {total_in} / 출력 {total_out} 토큰")
