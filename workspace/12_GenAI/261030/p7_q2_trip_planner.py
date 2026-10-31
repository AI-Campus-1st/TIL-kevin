# 과제 7-2 정답: 도시별 병렬 일정 생성 + 예산 조정 루프 여행 플래너
# (Send 동적 병렬 · operator.add Reducer · Command(update + goto) · 조정 루프 · recursion_limit)
import operator
from typing import Annotated, Literal, TypedDict

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, Overwrite, Send

load_dotenv()
llm = ChatOpenAI(model="gpt-6-luna", temperature=0, reasoning={"effort": "none"})

# ---------------------------------------------------------------- 1) 스키마 · State
class Activity(BaseModel):
    city: str = Field(description="도시 이름")
    name: str = Field(description="활동 이름")
    cost: int = Field(description="1인 예상 비용(원)")
    priority: int = Field(description="중요도 1~5, 5가 가장 중요")

class CityPlan(BaseModel):
    activities: list[Activity] = Field(description="활동 4개")

class TripState(TypedDict):
    cities: list[str]
    budget: int
    activities: Annotated[list[dict], operator.add]   # 병렬 결과 누적
    total: int
    trimmed: list[str]
    rounds: int

class CityInput(TypedDict):
    city: str

# ---------------------------------------------------------------- 2) 노드
def fan_out(state: TripState):
    """도시 수만큼 plan_city 작업을 동적으로 생성"""
    return [Send("plan_city", {"city": c}) for c in state["cities"]]

def plan_city(state: CityInput):
    plan = llm.with_structured_output(CityPlan).invoke(
        f"{state['city']} 1일 여행 활동 4개를 제안하세요. 비용은 1인 기준 원화, "
        f"중요도는 대표 명소일수록 높게 매기세요.")
    acts = [a.model_dump() | {"city": state["city"]} for a in plan.activities]
    return {"activities": acts}

def budget_check(state: TripState) -> Command[Literal["trim", "__end__"]]:
    total = sum(a["cost"] for a in state["activities"])
    if total <= state["budget"] or not state["activities"]:
        return Command(update={"total": total}, goto=END)
    return Command(update={"total": total}, goto="trim")

def trim(state: TripState):
    """중요도가 가장 낮고(동률이면 비싼) 활동 1개를 제거 — Reducer가 있는 키를 통째로 바꿀 때는 Overwrite"""
    acts = sorted(state["activities"], key=lambda a: (a["priority"], -a["cost"]))
    removed, rest = acts[0], acts[1:]
    return {
        "activities": Overwrite(rest),
        "trimmed": state.get("trimmed", []) + [f"{removed['city']} · {removed['name']} ({removed['cost']:,}원)"],
        "rounds": state.get("rounds", 0) + 1,
    }

# ---------------------------------------------------------------- 3) 그래프
b = StateGraph(TripState)
b.add_node("plan_city", plan_city)
b.add_node("budget_check", budget_check)     # Command로 이동하므로 나가는 엣지 없음
b.add_node("trim", trim)
b.add_conditional_edges(START, fan_out, ["plan_city"])
b.add_edge("plan_city", "budget_check")      # 모든 Send 작업이 끝난 뒤 실행
b.add_edge("trim", "budget_check")           # 조정 루프
graph = b.compile()

# ---------------------------------------------------------------- 4) 테스트
result = graph.invoke(
    {"cities": ["교토", "오사카", "나라"], "budget": 150_000, "trimmed": [], "rounds": 0},
    {"recursion_limit": 30},                 # 루프 안전장치
)

print(f"예산 {150_000:,}원 / 최종 합계 {result['total']:,}원 / 조정 {result['rounds']}회")
for a in sorted(result["activities"], key=lambda a: a["city"]):
    print(f"  [{a['city']}] {a['name']} · {a['cost']:,}원 · 중요도 {a['priority']}")
print("제외한 활동:", result["trimmed"])
