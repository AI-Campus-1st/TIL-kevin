# 과제 4-3 정답: 세션별 학습 도우미 챗봇 + 대화 기록 자르기 (RunnableWithMessageHistory · trim_messages · stream)
from operator import itemgetter
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import trim_messages
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory

load_dotenv()
llm = ChatOpenAI(model="gpt-6-luna")

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 {subject} 학습 도우미입니다. 개념을 2문장으로 설명하고 확인 질문 1개를 합니다."),
    MessagesPlaceholder("history"),
    ("human", "{question}"),
])

# 최근 메시지 6개만 남기기 (token_counter=len → 메시지 개수 기준)
trimmer = trim_messages(max_tokens=6, token_counter=len, strategy="last", start_on="human")

chain = (
    RunnablePassthrough.assign(history=itemgetter("history") | trimmer)
    | prompt | llm | StrOutputParser()
)

store: dict[str, InMemoryChatMessageHistory] = {}


def get_history(session_id: str) -> InMemoryChatMessageHistory:
    return store.setdefault(session_id, InMemoryChatMessageHistory())


tutor = RunnableWithMessageHistory(
    chain, get_history, input_messages_key="question", history_messages_key="history",
).with_config(run_name="study_tutor", tags=["assignment"])


def ask(session, subject, question):
    cfg = {"configurable": {"session_id": session}}
    print(f"\n[{session}] Q: {question}\nA: ", end="")
    for chunk in tutor.stream({"subject": subject, "question": question}, config=cfg):
        print(chunk, end="", flush=True)
    print(f"\n  (저장된 메시지 {len(store[session].messages)}개)")


ask("kim", "파이썬", "제 이름은 김소신이고 리스트를 배우고 있어요.")
ask("lee", "통계", "평균과 중앙값의 차이가 뭐예요?")
for q in ["리스트 슬라이싱은 뭐예요?", "딕셔너리는요?", "튜플은 왜 써요?", "제 이름이 뭐였죠?"]:
    ask("kim", "파이썬", q)

# 저장소에는 전체 기록이 남고, 모델에는 최근 6개만 전달됨
print({k: len(v.messages) for k, v in store.items()})
