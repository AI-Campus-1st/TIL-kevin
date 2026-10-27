# 과제 4-1 정답: 채용 공고 분석 + 지원자 매칭 (RunnableParallel · itemgetter · assign · RunnableLambda)
import time
from operator import itemgetter
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough

load_dotenv()
llm = ChatOpenAI(model="gpt-6-luna")

skills_chain = (
    ChatPromptTemplate.from_template(
        "채용 공고에서 필수 기술 스택만 소문자 JSON 배열로 추출해. 다른 말은 쓰지 마.\n"
        '형식: {{"skills": ["python", "..."]}}\n\n{posting}')
    | llm | JsonOutputParser()
)
career_chain = (
    ChatPromptTemplate.from_template("채용 공고에서 요구 경력(년)을 숫자 하나로만 답해. 신입이면 0.\n\n{posting}")
    | llm | StrOutputParser()
)
summary_chain = (
    ChatPromptTemplate.from_template("채용 공고의 담당 업무를 한 문장으로 요약해.\n\n{posting}")
    | llm | StrOutputParser()
)

analysis = RunnableParallel(
    skills=skills_chain | itemgetter("skills"),
    career=career_chain,
    summary=summary_chain,
)


def match(d: dict) -> dict:
    """지원자와 공고를 코드로 비교 — 계산은 LLM에 맡기지 않음"""
    required = {s.lower() for s in d["analysis"]["skills"]}
    have = {s.lower() for s in d["candidate"]["skills"]}
    hit = required & have
    try:
        need_years = int("".join(ch for ch in d["analysis"]["career"] if ch.isdigit()) or 0)
    except ValueError:
        need_years = 0
    score = round(100 * len(hit) / max(len(required), 1))
    return {
        "summary": d["analysis"]["summary"],
        "match_score": score,
        "matched": sorted(hit),
        "missing": sorted(required - have),
        "career_ok": d["candidate"]["years"] >= need_years,
    }


pipeline = (
    RunnablePassthrough.assign(analysis=analysis)   # {posting, candidate} + analysis
    | RunnableLambda(match)
)

posting = """[백엔드 개발자] 결제 서비스 API 설계 및 운영. 경력 3년 이상.
필수: Python, FastAPI, PostgreSQL, Docker / 우대: Kubernetes, AWS"""
candidate = {"name": "지원자A", "years": 4, "skills": ["Python", "Django", "PostgreSQL", "Docker", "AWS"]}

t0 = time.time()
print(pipeline.invoke({"posting": posting, "candidate": candidate}))
print(f"병렬 실행 시간: {time.time() - t0:.2f}s")

# 비교: 같은 세 체인을 순차 실행
t0 = time.time()
for c in [skills_chain, career_chain, summary_chain]:
    c.invoke({"posting": posting})
print(f"순차 실행 시간: {time.time() - t0:.2f}s")
