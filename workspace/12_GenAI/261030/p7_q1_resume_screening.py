# 과제 7-1 정답: 이력서 스크리닝 워크플로
# (사용자 정의 State · 구조화 출력 노드 · 고정 엣지 병렬 실행(fan-out / fan-in) · 조건부 엣지 · stream)
from typing import Literal, TypedDict

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

load_dotenv()
llm = ChatOpenAI(model="gpt-6-luna", temperature=0, reasoning={"effort": "none"})

REQUIRED_SKILLS = {"python", "sql", "docker"}
MIN_YEARS = 3

# ---------------------------------------------------------------- 1) State
class Profile(BaseModel):
    name: str = Field(description="지원자 이름")
    years: int = Field(description="총 경력 연수 (정수)")
    skills: list[str] = Field(description="보유 기술 (소문자 영어 단어)")

class ScreenState(TypedDict):
    resume: str
    profile: dict
    skill_score: int        # 병렬 노드 1이 채움
    strengths: str          # 병렬 노드 2가 채움
    total: int
    decision: str
    message: str

# ---------------------------------------------------------------- 2) 노드
def extract(state: ScreenState):
    p = llm.with_structured_output(Profile).invoke(
        f"다음 이력서에서 이름, 총 경력 연수, 보유 기술을 추출하세요.\n\n{state['resume']}")
    return {"profile": p.model_dump()}

def check_skills(state: ScreenState):
    """코드로 채점 — 필수 기술 일치율 70점 + 경력 30점"""
    p = state["profile"]
    have = {s.lower().strip() for s in p["skills"]}
    skill = round(len(have & REQUIRED_SKILLS) / len(REQUIRED_SKILLS) * 70)
    career = 30 if p["years"] >= MIN_YEARS else round(p["years"] / MIN_YEARS * 30)
    return {"skill_score": skill + career}

def summarize_strengths(state: ScreenState):
    s = llm.invoke(f"다음 이력서에서 지원자의 강점을 한 문장으로 요약하세요.\n\n{state['resume']}").content
    return {"strengths": s}

def decide(state: ScreenState):               # fan-in: 두 병렬 노드가 끝난 뒤 실행
    total = state["skill_score"]
    return {"total": total, "decision": "interview" if total >= 70 else "reject"}

def route(state: ScreenState) -> Literal["invite", "reject"]:
    return "invite" if state["decision"] == "interview" else "reject"

def invite(state: ScreenState):
    msg = llm.invoke(
        f"{state['profile']['name']}님께 1차 면접을 안내하는 3문장 이메일을 작성하세요. "
        f"강점({state['strengths']})을 한 번 언급하세요.").content
    return {"message": msg}

def reject(state: ScreenState):
    missing = REQUIRED_SKILLS - {s.lower() for s in state["profile"]["skills"]}
    return {"message": f"{state['profile']['name']}님, 지원해 주셔서 감사합니다. "
                       f"이번 포지션은 {', '.join(sorted(missing)) or '경력 요건'} 역량이 필요해 함께하기 어렵습니다."}

# ---------------------------------------------------------------- 3) 그래프
b = StateGraph(ScreenState)
b.add_node("extract", extract)
b.add_node("check_skills", check_skills)
b.add_node("summarize_strengths", summarize_strengths)
b.add_node("decide", decide)
b.add_node("invite", invite)
b.add_node("reject", reject)

b.add_edge(START, "extract")
b.add_edge("extract", "check_skills")              # fan-out: 같은 단계에서 병렬 실행
b.add_edge("extract", "summarize_strengths")
b.add_edge(["check_skills", "summarize_strengths"], "decide")   # 두 노드가 모두 끝나야 실행
b.add_conditional_edges("decide", route)
b.add_edge("invite", END)
b.add_edge("reject", END)
graph = b.compile()

print(graph.get_graph().draw_mermaid())

# ---------------------------------------------------------------- 4) 테스트
RESUMES = [
    "김하늘 / 백엔드 개발 5년. Python(FastAPI), PostgreSQL SQL 튜닝, Docker와 Kubernetes로 배포 자동화. "
    "결제 API 응답 속도 40% 개선.",
    "이도윤 / 프론트엔드 개발 1년. React, TypeScript 사용. 사내 디자인 시스템 컴포넌트 20종 개발.",
]
for r in RESUMES:
    print("\n" + "=" * 60)
    for step in graph.stream({"resume": r}, stream_mode="updates"):
        for node, upd in step.items():
            print(f"[{node}] {upd}")
