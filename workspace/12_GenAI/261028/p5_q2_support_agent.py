# 과제 5-3 정답: 고객 전용 주문 상담 에이전트 (ToolRuntime context · checkpointer · 에러 처리 · 호출 제한 미들웨어)
import json
from dataclasses import dataclass

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware, wrap_tool_call
from langchain.messages import ToolMessage
from langchain.tools import ToolRuntime, tool
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()
llm = ChatOpenAI(model="gpt-6-luna")

ORDERS = {
    "A-1001": {"customer_id": "c01", "item": "무선 이어폰", "status": "배송중", "amount": 89000},
    "A-1002": {"customer_id": "c01", "item": "텀블러", "status": "배송완료", "amount": 29000},
    "B-2001": {"customer_id": "c02", "item": "러닝화", "status": "결제완료", "amount": 119000},
}


@dataclass
class Customer:
    customer_id: str
    name: str


@tool
def list_my_orders(runtime: ToolRuntime[Customer]) -> str:
    """현재 로그인한 고객의 주문 목록(주문번호 · 상품 · 상태 · 금액)을 조회합니다."""
    cid = runtime.context.customer_id                       # 모델이 아닌 서버가 넣는 값
    mine = {k: v for k, v in ORDERS.items() if v["customer_id"] == cid}
    return json.dumps(mine, ensure_ascii=False) if mine else "주문 내역이 없습니다."


@tool
def request_refund(order_id: str, reason: str, runtime: ToolRuntime[Customer]) -> str:
    """주문번호로 환불을 요청합니다. 배송완료된 주문만 환불할 수 있습니다."""
    order = ORDERS.get(order_id)
    if order is None or order["customer_id"] != runtime.context.customer_id:
        raise ValueError(f"주문번호 {order_id}를 찾을 수 없습니다")         # 다른 고객 주문도 '없음'으로 처리
    if order["status"] != "배송완료":
        return f"환불 불가: 현재 상태가 '{order['status']}'입니다. 배송완료 후 요청할 수 있습니다."
    order["status"] = "환불요청"
    return f"환불 요청 완료: {order_id} ({order['item']}, {order['amount']:,}원) / 사유: {reason}"


@wrap_tool_call
def tool_error_to_message(request, handler):
    """도구 예외를 모델이 이해할 수 있는 ToolMessage로 변환"""
    try:
        return handler(request)
    except Exception as e:
        return ToolMessage(content=f"도구 오류: {e}. 주문 목록을 조회해 주문번호를 확인하세요.",
                           tool_call_id=request.tool_call["id"])


agent = create_agent(
    model=llm,
    tools=[list_my_orders, request_refund],
    system_prompt="당신은 쇼핑몰 고객상담원입니다. 도구 결과에 근거해 정중한 존댓말로 2~3문장 이내로 답하세요.",
    context_schema=Customer,
    checkpointer=InMemorySaver(),
    middleware=[tool_error_to_message, ModelCallLimitMiddleware(run_limit=6)],
)


def chat(customer: Customer, thread: str, msg: str):
    r = agent.invoke({"messages": [{"role": "user", "content": msg}]},
                     config={"configurable": {"thread_id": thread}}, context=customer)
    print(f"[{customer.name}] {msg}\n  → {r['messages'][-1].content}\n")


kim = Customer("c01", "김소신")
park = Customer("c02", "박고객")

chat(kim, "kim-1", "제 주문 내역 보여주세요")
chat(kim, "kim-1", "그중 텀블러는 환불하고 싶어요. 색상이 마음에 안 들어요")   # 멀티턴: 주문번호 기억
chat(kim, "kim-1", "이어폰도 환불해 주세요")                                   # 배송중 → 환불 불가
chat(kim, "kim-1", "B-2001 주문도 환불해 주세요")                              # 타인 주문 → 도구 오류 처리
chat(park, "park-1", "제 주문 내역 보여주세요")                               # 다른 고객 → 본인 주문만
print({k: v["status"] for k, v in ORDERS.items()})
