# 과제 3-2 정답: 레시피 구조화 추출 — PydanticOutputParser vs with_structured_output
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException

load_dotenv()
llm = ChatOpenAI(model="gpt-6-luna")

class Ingredient(BaseModel):
    name: str = Field(description="재료 이름")
    amount: str = Field(description="분량 (예: 200g, 2큰술). 없으면 '적당량'")

class Recipe(BaseModel):
    dish: str = Field(description="요리 이름")
    servings: int = Field(description="몇 인분")
    minutes: int = Field(description="총 조리 시간(분)")
    ingredients: list[Ingredient]
    steps: list[str] = Field(description="조리 순서, 한 단계당 한 문장")

texts = [
    "김치볶음밥 2인분이에요. 밥 두 공기, 김치 한 컵, 스팸 반 캔, 계란 2개 준비하세요. "
    "팬에 스팸과 김치를 볶다가 밥을 넣고 5분 더 볶고, 계란 프라이를 올리면 끝. 15분이면 충분해요.",
    "된장찌개(3인분, 약 25분): 물 600ml에 된장 2큰술을 풀고 감자, 호박, 두부를 넣어 끓입니다. 마지막에 대파를 넣어요.",
    "토스트 1인분. 식빵 2장에 버터를 바르고 구운 뒤 설탕을 뿌립니다. 5분 걸려요.",
]

# 방법 1: PydanticOutputParser — 프롬프트에 형식 지시 삽입
parser = PydanticOutputParser(pydantic_object=Recipe)
prompt = ChatPromptTemplate.from_messages([
    ("system", "요리 설명에서 레시피 정보를 추출합니다.\n{format_instructions}"),
    ("human", "{text}"),
]).partial(format_instructions=parser.get_format_instructions())
parser_chain = prompt | llm | parser

# 방법 2: with_structured_output — 모델의 구조화 출력 사용
structured_chain = (
    ChatPromptTemplate.from_messages([("system", "요리 설명에서 레시피 정보를 추출합니다."), ("human", "{text}")])
    | llm.with_structured_output(Recipe)
)

for name, chain in [("PydanticOutputParser", parser_chain), ("with_structured_output", structured_chain)]:
    ok = 0
    print(f"\n######## {name} ########")
    for t in texts:
        try:
            r = chain.invoke({"text": t})
            ok += 1
            print(f"- {r.dish}: {r.servings}인분 · {r.minutes}분 · 재료 {len(r.ingredients)}개 · 단계 {len(r.steps)}개")
        except OutputParserException as e:
            print("- 파싱 실패:", str(e)[:80])
    print(f"성공 {ok}/{len(texts)}")
