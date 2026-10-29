# 과제 6-2 정답: 섹션 출처를 JSON으로 돌려주는 제품 매뉴얼 Q&A
# (MarkdownHeaderTextSplitter + RecursiveCharacterTextSplitter 2단계 분할 · FAISS · MMR · 구조화 출력)
import json
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

load_dotenv()
llm = ChatOpenAI(model="gpt-6-luna", temperature=0, reasoning={"effort": "none"})
emb = OpenAIEmbeddings(model="text-embedding-3-small")

# ---------------------------------------------------------------- 1) 샘플 매뉴얼 (마크다운 2개)
MANUALS = {
    "robot_cleaner.md": """# 로봇청소기 RC-9 사용 설명서
## 설치
### 충전 스테이션 위치
충전 스테이션은 벽에 붙이고 좌우 0.5m, 앞쪽 1.5m 이내에 장애물이 없는 곳에 둔다.
### 첫 충전
처음 사용할 때는 4시간 이상 완전히 충전한 뒤 청소를 시작한다.
## 청소 모드
### 자동 모드
전체 공간을 지도로 만든 뒤 구역 순서대로 청소한다. 한 번 충전으로 최대 150분 동작한다.
### 집중 모드
지정한 1m x 1m 구역을 두 번 반복해 청소한다.
## 문제 해결
### 충전이 되지 않을 때
충전 단자를 마른 천으로 닦고, 스테이션 전원 어댑터가 연결되어 있는지 확인한다.
### 오류 코드 E3
바퀴에 머리카락이나 이물질이 감긴 상태다. 전원을 끄고 바퀴를 분리해 청소한다.
""",
    "air_fryer.md": """# 에어프라이어 AF-5 사용 설명서
## 사용 방법
### 예열
조리 전 180도에서 3분간 예열하면 조리 시간이 짧아지고 결과가 고르게 나온다.
### 조리 용량
바스켓에는 최대 1.2kg까지 넣을 수 있으며, 재료가 겹치지 않게 펼쳐 담는다.
## 관리
### 세척
바스켓과 트레이는 식기세척기 사용이 가능하다. 본체는 전원을 뽑고 젖은 천으로 닦는다.
## 문제 해결
### 흰 연기가 날 때
기름이 많은 재료에서 기름이 떨어져 타는 경우다. 트레이의 기름을 버리고 다시 조리한다.
""",
}

# ---------------------------------------------------------------- 2) 2단계 분할 — 헤더 → 길이
header_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")]
)
size_splitter = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=20)

chunks = []
for file, text in MANUALS.items():
    sections = header_splitter.split_text(text)             # 헤더가 metadata(h1/h2/h3)로
    for c in size_splitter.split_documents(sections):       # 긴 섹션은 한 번 더 분할 (metadata 유지)
        c.metadata["file"] = file
        c.metadata["section"] = " > ".join(c.metadata[h] for h in ("h2", "h3") if h in c.metadata)
        chunks.append(c)

print("청크 수:", len(chunks))
for c in chunks[:3]:
    print(" ", c.metadata["file"], "|", c.metadata["section"], "|", c.page_content[:30])

vs = FAISS.from_documents(chunks, emb)
retriever = vs.as_retriever(search_type="mmr", search_kwargs={"k": 3, "fetch_k": 8, "lambda_mult": 0.6})

# ---------------------------------------------------------------- 3) 구조화 답변
class Source(BaseModel):
    file: str = Field(description="참고한 파일명")
    section: str = Field(description="참고한 섹션 경로 (예: 문제 해결 > 오류 코드 E3)")

class ManualAnswer(BaseModel):
    found: bool = Field(description="문서에서 답을 찾았으면 true")
    answer: str = Field(description="문서 근거 답변. 찾지 못했으면 빈 문자열")
    sources: list[Source] = Field(default_factory=list, description="실제로 참고한 문서 섹션")

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "당신은 가전 제품 매뉴얼 상담원입니다. 아래 [문서]에 있는 내용만 근거로 답하세요.\n"
     "문서에 답이 없으면 found=false로 두고 추측하지 마세요.\n"
     "sources에는 답변에 실제로 사용한 문서의 파일명과 섹션만 넣으세요.\n\n[문서]\n{context}"),
    ("human", "{question}"),
])

def format_docs(docs):
    return "\n\n".join(
        f"<doc file='{d.metadata['file']}' section='{d.metadata['section']}'>\n{d.page_content}\n</doc>"
        for d in docs)

def finalize(x):
    ans: ManualAnswer = x["answer"]
    retrieved = {(d.metadata["file"], d.metadata["section"]) for d in x["docs"]}
    # 모델이 검색되지 않은 출처를 만들어 넣었는지 코드로 확인
    ans.sources = [s for s in ans.sources if (s.file, s.section) in retrieved]
    if not ans.found:
        ans.answer = "매뉴얼에서 찾을 수 없습니다. 고객센터(1588-0000)로 문의해 주세요."
        ans.sources = []
    return ans

qa_chain = (
    RunnableParallel(docs=retriever, question=RunnablePassthrough())
    .assign(answer=RunnablePassthrough.assign(context=lambda x: format_docs(x["docs"]))
            | prompt | llm.with_structured_output(ManualAnswer))
    | RunnableLambda(finalize)
)

# ---------------------------------------------------------------- 4) 테스트
for q in ["로봇청소기에 E3가 떠요", "에어프라이어 바스켓 식기세척기 돼?",
          "처음 쓸 때 충전은 얼마나 해야 해?", "에어프라이어 보증 기간은?"]:
    res = qa_chain.invoke(q)
    print(f"\nQ: {q}")
    print(json.dumps(res.model_dump(), ensure_ascii=False, indent=2))
