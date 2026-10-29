# 과제 6-1 정답: 부서 · 연도 필터를 자동으로 적용하는 사내 공지 검색기
# (CSVLoader · metadata · InMemoryVectorStore · 구조화 출력으로 필터 추출 · 필터 검색)
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from typing import Literal, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_community.document_loaders import CSVLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()
llm = ChatOpenAI(model="gpt-6-luna", temperature=0, reasoning={"effort": "none"})
emb = OpenAIEmbeddings(model="text-embedding-3-small")

# ---------------------------------------------------------------- 1) 로드 — 필터에 쓸 열은 metadata로
loader = CSVLoader(
    file_path='notices.csv', encoding="utf-8",
    content_columns=["title", "body"],               # 임베딩할 본문
    metadata_columns=["id", "year", "department"],   # 필터 · 출처용
)
docs = loader.load()
print(docs[0].page_content.replace("\n", " | "), docs[0].metadata)

vs = InMemoryVectorStore.from_documents(docs, embedding=emb)

# ---------------------------------------------------------------- 2) 질문에서 필터 추출 (Self-Query 방식)
DEPTS = ["인사", "IT", "총무"]
YEARS = ["2025", "2026"]

class SearchPlan(BaseModel):
    query: str = Field(description="필터 조건을 뺀 검색 문장")
    department: Optional[Literal["인사", "IT", "총무"]] = Field(default=None, description="질문에 부서가 명시된 경우만")
    year: Optional[Literal["2025", "2026"]] = Field(default=None, description="질문에 연도가 명시된 경우만")

plan_chain = ChatPromptTemplate.from_messages([
    ("system", "사내 공지 검색 질문을 분석해 검색 문장과 필터를 추출하세요. "
               "부서 · 연도가 질문에 없으면 null로 두세요. 올해는 2026년입니다."),
    ("human", "{question}"),
]) | llm.with_structured_output(SearchPlan)

def search_notices(question: str, k: int = 3):
    plan = plan_chain.invoke({"question": question})
    cond = {}
    if plan.department in DEPTS:          # 모델 출력도 허용값인지 코드로 한 번 더 확인
        cond["department"] = plan.department
    if plan.year in YEARS:
        cond["year"] = plan.year

    def match(doc):                       # InMemoryVectorStore의 filter는 Document를 받는 함수
        return all(doc.metadata.get(key) == val for key, val in cond.items())

    hits = vs.similarity_search(plan.query or question, k=k, filter=match if cond else None)
    if not hits and cond:                 # 필터 결과가 없으면 필터 없이 다시 검색
        hits = vs.similarity_search(plan.query or question, k=k)
        cond = {"(필터 해제)": True}
    return plan, cond, hits

# ---------------------------------------------------------------- 3) 테스트
for q in [
    "IT 부서 공지 중에 접속 관련 내용 있어?",
    "올해 인사팀 휴직 관련 공지 알려줘",
    "2025년 공지 중 공사나 점검 일정",
    "점심 시간 바뀌었어?",
]:
    plan, cond, hits = search_notices(q)
    print(f"\nQ: {q}")
    print(f"  검색어={plan.query!r} 필터={cond}")
    for d in hits:
        m = d.metadata
        title = d.page_content.splitlines()[0].replace("title: ", "")
        print(f"  - [{m['id']} · {m['year']} · {m['department']}] {title}")
