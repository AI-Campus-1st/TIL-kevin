# 과제 5-2 정답: 해외 여행 준비 리서치 에이전트 (웹 검색 · 날씨 예보 API · 환율 API · response_format · stream)
import requests
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain.agents import create_agent
from langchain.tools import tool

load_dotenv()
llm = ChatOpenAI(model="gpt-6-luna")

search = TavilySearch(max_results=3, topic="general")


@tool
def get_forecast(city: str, days: int = 3) -> dict:
    """도시의 향후 며칠간 날씨 예보(최고 · 최저 기온, 강수 확률)를 조회합니다. city는 영문 도시 이름(예: Tokyo)."""
    days = max(1, min(days, 7))
    try:
        geo = requests.get("https://geocoding-api.open-meteo.com/v1/search",
                           params={"name": city, "count": 1}, timeout=10).json()
        if not geo.get("results"):
            return {"error": f"'{city}' 위치를 찾을 수 없습니다. 영문 도시 이름으로 다시 시도하세요."}
        loc = geo["results"][0]
        daily = requests.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude": loc["latitude"], "longitude": loc["longitude"], "timezone": "auto", "forecast_days": days,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        }, timeout=10).json()["daily"]
    except requests.RequestException as e:
        return {"error": f"날씨 API 호출 실패: {e}"}
    return {"city": loc["name"], "forecast": [
        {"date": d, "max_c": mx, "min_c": mn, "rain_prob": p}
        for d, mx, mn, p in zip(daily["time"], daily["temperature_2m_max"],
                                daily["temperature_2m_min"], daily["precipitation_probability_max"])]}


@tool
def get_exchange_rate(currency: str) -> dict:
    """외화 1단위가 원화(KRW)로 얼마인지 최신 환율을 조회합니다. currency는 통화 코드(예: JPY, USD, EUR)."""
    try:
        data = requests.get(f"https://open.er-api.com/v6/latest/{currency.upper()}", timeout=10).json()
    except requests.RequestException as e:
        return {"error": f"환율 API 호출 실패: {e}"}
    if data.get("result") != "success":
        return {"error": f"'{currency}' 통화 코드를 확인하세요."}
    return {"currency": currency.upper(), "krw": round(data["rates"]["KRW"], 4), "updated": data.get("time_last_update_utc")}


class TripBrief(BaseModel):
    city: str
    weather_summary: str = Field(description="예보 기간의 날씨 요약 한 문장")
    packing: list[str] = Field(description="챙길 준비물 3~5개")
    krw_per_unit: float = Field(description="현지 통화 1단위당 원화")
    budget_tip: str = Field(description="환율을 반영한 예산 팁 한 문장")
    local_news: str = Field(description="웹 검색으로 찾은 여행 관련 최신 정보 한 문장")
    sources: list[str] = Field(description="참고한 URL 목록")


agent = create_agent(
    model=llm,
    tools=[search, get_forecast, get_exchange_rate],
    system_prompt="당신은 해외여행 준비 도우미입니다. 날씨는 get_forecast, 환율은 get_exchange_rate, 최신 행사 · 주의사항은 웹 검색으로 확인하고, 도구 결과에 없는 내용은 지어내지 마세요.",
    response_format=TripBrief,
)

inputs = {"messages": [{"role": "user", "content": "다음 주에 도쿄로 3일 여행 가. 준비할 것 정리해줘"}]}

# 진행 상황을 스트리밍하면서, 마지막에 나오는 구조화 결과를 함께 받기
brief = None
for chunk in agent.stream(inputs, stream_mode="updates"):
    for node, update in chunk.items():
        if not update:
            continue
        if update.get("structured_response") is not None:
            brief = update["structured_response"]
        if "messages" not in update:
            continue
        last = update["messages"][-1]
        if getattr(last, "tool_calls", None):
            print(f"[{node}] 호출 → {[(c['name'], c['args']) for c in last.tool_calls]}")
        elif node == "tools":
            print(f"[{node}] 결과 수신 ({len(str(last.content))}자)")

print("\n", brief.model_dump_json(indent=2) if brief else "구조화 결과 없음")
