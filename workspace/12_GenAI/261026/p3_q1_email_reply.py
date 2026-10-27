# 과제 3-1 정답: 고객 이메일 답장 작성기 (ChatPromptTemplate · partial · batch · usage_metadata)
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
llm = ChatOpenAI(model="gpt-6-luna")

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "당신은 {company} 고객지원팀 상담원입니다.\n"
     "- 고객이 쓴 언어와 같은 언어로 답장합니다.\n"
     "- 정중한 어조, 본문 4문장 이내.\n"
     "- 마지막 줄에 서명: {signature}"),
    ("human", "고객 이름: {name}\n문의 내용:\n{email}"),
]).partial(company="SOSIN Shop", signature="SOSIN Shop 고객지원팀 드림")

print("남은 입력 변수:", prompt.input_variables)   # ['email', 'name']

emails = [
    {"name": "김민수", "email": "주문한 운동화 사이즈를 270에서 275로 바꿀 수 있을까요?"},
    {"name": "Emily", "email": "My package arrived damaged. How can I get a replacement?"},
    {"name": "이서연", "email": "적립금은 언제 들어오나요? 구매 확정은 어제 했어요."},
]

chain = prompt | llm                      # AIMessage를 그대로 받아 usage_metadata 확인
replies = chain.batch(emails, config={"max_concurrency": 3})

total_in = total_out = 0
for req, msg in zip(emails, replies):
    u = msg.usage_metadata or {}
    total_in += u.get("input_tokens", 0)
    total_out += u.get("output_tokens", 0)
    print(f"===== {req['name']} (in {u.get('input_tokens')}, out {u.get('output_tokens')}) =====")
    print(msg.content, "\n")

cost = (total_in * 0.10 + total_out * 0.50) / 1_000_000   # gpt-6-luna 단가 (USD / 1M tokens)
print(f"총 토큰: 입력 {total_in} / 출력 {total_out} → ${cost:.6f}")
