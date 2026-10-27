# 과제 4-2 정답: 언어 감지 라우팅 번역봇 (RunnableLambda · RunnableBranch · with_fallbacks · with_retry)
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnableLambda

load_dotenv()
primary = ChatOpenAI(model="gpt-6-sol", max_retries=0)
backup = ChatOpenAI(model="gpt-6-luna")
llm = primary.with_fallbacks([backup])            # 주 모델 장애 시 대체 모델


def detect(text: str) -> dict:
    """언어 감지는 코드로 — 한글 · 영문 글자 비율"""
    ko = len(re.findall(r"[가-힣]", text))
    en = len(re.findall(r"[A-Za-z]", text))
    lang = "ko" if ko > en else "en" if en > ko else "unknown"
    return {"text": text.strip(), "lang": lang}


ko2en = ChatPromptTemplate.from_template("다음 한국어를 자연스러운 영어로 번역해. 번역문만 출력해.\n{text}") | llm | StrOutputParser()
en2ko = ChatPromptTemplate.from_template("다음 영어를 자연스러운 한국어로 번역해. 번역문만 출력해.\n{text}") | llm | StrOutputParser()
unknown = RunnableLambda(lambda d: f"번역할 수 없는 입력입니다: {d['text']!r} (한국어 또는 영어만 지원)")

router = RunnableBranch(
    (lambda d: d["lang"] == "ko", ko2en),
    (lambda d: d["lang"] == "en", en2ko),
    unknown,
)


def format_result(d: dict) -> str:
    return f"[{d['lang']}] {d['text']}\n → {d['result']}"


chain = (
    RunnableLambda(detect)
    | {"text": lambda d: d["text"], "lang": lambda d: d["lang"], "result": router}
    | RunnableLambda(format_result)
).with_retry(stop_after_attempt=2)

inputs = ["오늘 회의는 3시로 미뤄졌습니다.", "Could you send me the invoice by Friday?", "12345 !!!", "   다음 주 월요일 휴무입니다   "]
for r in chain.batch(inputs):
    print(r, "\n")
