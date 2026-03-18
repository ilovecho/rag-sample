"""
=== 4단계: 고급 RAG 기법 ===

실무에서 RAG 품질을 높이기 위한 다양한 기법을 보여줍니다:
1. 다양한 검색 전략 (MMR, Similarity Score Threshold)
2. 메타데이터 필터링
3. 멀티 쿼리 리트리버 (질문을 여러 각도로 재작성)
4. 앙상블 리트리버 (키워드 + 시맨틱 검색 결합)
"""

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.retrievers import MultiQueryRetriever
from langchain.schema import Document

load_dotenv()


def prepare_vectorstore():
    """문서를 로드하고 벡터 저장소를 생성합니다."""
    loader = DirectoryLoader(
        "sample_documents/",
        glob="*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300, chunk_overlap=50
    )
    chunks = text_splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings)
    return vectorstore


# ──────────────────────────────────────────────
# 기법 1: 다양한 검색 전략
# ──────────────────────────────────────────────
def demo_search_strategies(vectorstore):
    """
    검색 전략 비교:

    1. similarity: 코사인 유사도 기반 (기본값)
       - 가장 유사한 k개 반환
    2. mmr (Maximal Marginal Relevance): 다양성 고려
       - 유사하지만 서로 다른 내용의 문서를 반환
       - 중복 답변 방지에 유용
    3. similarity_score_threshold: 점수 기준
       - 유사도가 특정 임계값 이상인 문서만 반환
       - 관련 없는 문서 필터링에 유용
    """
    query = "복리후생에 대해 알려주세요"
    print("=" * 60)
    print(f"검색 전략 비교 | 질문: '{query}'")
    print("=" * 60)

    # 1) 기본 유사도 검색
    print("\n[1] Similarity 검색:")
    results = vectorstore.similarity_search(query, k=3)
    for i, doc in enumerate(results):
        print(f"  {i+1}. {doc.page_content[:80]}...")

    # 2) MMR 검색 (다양성 강조)
    print("\n[2] MMR 검색 (다양성↑):")
    results = vectorstore.max_marginal_relevance_search(
        query,
        k=3,
        fetch_k=10,        # 후보 10개 중에서
        lambda_mult=0.5,    # 0=다양성 최대, 1=유사도 최대
    )
    for i, doc in enumerate(results):
        print(f"  {i+1}. {doc.page_content[:80]}...")

    # 3) 유사도 점수 포함 검색
    print("\n[3] 유사도 점수 포함 검색:")
    results = vectorstore.similarity_search_with_score(query, k=3)
    for i, (doc, score) in enumerate(results):
        print(f"  {i+1}. [점수: {score:.4f}] {doc.page_content[:60]}...")


# ──────────────────────────────────────────────
# 기법 2: 메타데이터 활용
# ──────────────────────────────────────────────
def demo_metadata():
    """
    메타데이터를 문서에 태그하여 필터링 검색을 합니다.
    실무에서는 카테고리, 날짜, 부서 등으로 필터링 가능.
    """
    print("\n" + "=" * 60)
    print("메타데이터 필터링 데모")
    print("=" * 60)

    # 메타데이터가 포함된 문서 직접 생성
    docs = [
        Document(
            page_content="연차는 입사 1년 이상부터 15일 부여됩니다.",
            metadata={"category": "HR", "topic": "휴가"},
        ),
        Document(
            page_content="SmartWidget Pro Standard 요금제는 월 49,000원입니다.",
            metadata={"category": "Product", "topic": "요금"},
        ),
        Document(
            page_content="재택근무는 주 2회까지 가능하며 팀장 승인이 필요합니다.",
            metadata={"category": "HR", "topic": "근무"},
        ),
        Document(
            page_content="Enterprise 플랜은 온프레미스 설치를 지원합니다.",
            metadata={"category": "Product", "topic": "요금"},
        ),
    ]

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma.from_documents(documents=docs, embedding=embeddings)

    # HR 카테고리만 필터링 검색
    print("\n[HR 카테고리만 검색]")
    results = vectorstore.similarity_search(
        "회사 정책",
        k=3,
        filter={"category": "HR"},
    )
    for doc in results:
        print(f"  [{doc.metadata['topic']}] {doc.page_content}")

    # Product 카테고리만 필터링 검색
    print("\n[Product 카테고리만 검색]")
    results = vectorstore.similarity_search(
        "가격",
        k=3,
        filter={"category": "Product"},
    )
    for doc in results:
        print(f"  [{doc.metadata['topic']}] {doc.page_content}")


# ──────────────────────────────────────────────
# 기법 3: 멀티 쿼리 리트리버
# ──────────────────────────────────────────────
def demo_multi_query(vectorstore):
    """
    MultiQueryRetriever:
    - 사용자의 질문을 LLM이 여러 각도로 재작성
    - 각 변형 질문으로 검색 후 결과를 합침
    - 단일 질문으로 놓칠 수 있는 관련 문서까지 찾을 수 있음

    예: "복리후생" → ["직원 혜택", "회사 지원금", "welfare benefits"]
    """
    print("\n" + "=" * 60)
    print("멀티 쿼리 리트리버 데모")
    print("=" * 60)

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    multi_retriever = MultiQueryRetriever.from_llm(
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        llm=llm,
    )

    query = "직원들한테 돈으로 지원해주는 것들"
    print(f"\n질문: '{query}'")
    print("(LLM이 이 질문을 여러 형태로 변환하여 검색)")

    results = multi_retriever.invoke(query)
    print(f"\n검색 결과 {len(results)}개:")
    for i, doc in enumerate(results):
        print(f"  {i+1}. {doc.page_content[:80]}...")


if __name__ == "__main__":
    vectorstore = prepare_vectorstore()

    demo_search_strategies(vectorstore)
    demo_metadata()
    demo_multi_query(vectorstore)
