# 과제 3-3 정답: Few-shot 템플릿으로 업무 요청 → 표준 티켓 변환 (JsonOutputParser · batch · stream)
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

load_dotenv()
llm = ChatOpenAI(model="gpt-6-luna")

examples = [
    {"request": "로그인 페이지가 자꾸 흰 화면만 떠요 급해요",
     "ticket": '{"team": "개발", "title": "[개발] 로그인 페이지 빈 화면 오류 수정", "priority": "high"}'},
    {"request": "다음 달 신입 온보딩 자료 좀 업데이트 해주실 수 있나요",
     "ticket": '{"team": "인사", "title": "[인사] 신입 온보딩 자료 업데이트", "priority": "low"}'},
    {"request": "3분기 광고비 정산 내역이 안 맞는 것 같아요 이번 주 안에 확인 부탁",
     "ticket": '{"team": "재무", "title": "[재무] 3분기 광고비 정산 내역 확인", "priority": "medium"}'},
]
example_prompt = ChatPromptTemplate.from_messages([("human", "{request}"), ("ai", "{ticket}")])
few_shot = FewShotChatMessagePromptTemplate(examples=examples, example_prompt=example_prompt)

prompt = ChatPromptTemplate.from_messages([
    ("system", "사내 업무 요청을 표준 티켓 JSON으로 변환합니다. team은 [개발/인사/재무/총무] 중 하나, "
               "title은 '[팀] 명사형 작업명' 형식, priority는 low/medium/high 중 하나. JSON만 출력합니다."),
    few_shot,
    ("human", "{request}"),
])
chain = prompt | llm | JsonOutputParser()

requests = [
    "회의실 프로젝터가 안 켜져요 오후 2시 회의 전에 봐주세요",
    "연말정산 서류 제출 기한이 언제까지예요?",
    "결제 API 응답이 10초 넘게 걸려서 고객 불만이 들어오고 있어요",
    "사무실 커피머신 원두 주문 부탁드립니다",
    "법인카드 한도 상향 신청하고 싶어요",
]

tickets = chain.batch([{"request": r} for r in requests])
valid_teams, valid_pri = {"개발", "인사", "재무", "총무"}, {"low", "medium", "high"}
for r, t in zip(requests, tickets):
    ok = t.get("team") in valid_teams and t.get("priority") in valid_pri and str(t.get("title", "")).startswith("[")
    print(f"{'O' if ok else 'X'} {t}  ← {r}")

# 같은 템플릿을 스트리밍 체인으로 재사용
print("\n[stream]")
for chunk in (prompt | llm | StrOutputParser()).stream({"request": requests[2]}):
    print(chunk, end="", flush=True)
print()
