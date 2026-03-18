"""
=== 1단계: 기본 RAG 파이프라인 ===

RAG의 핵심 흐름:
  문서 로드 → 텍스트 분할 → 임베딩 → 벡터 저장 → 검색 → LLM 응답

이 파일은 가장 기본적인 RAG 파이프라인을 단계별로 보여줍니다.
"""

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_classic.chains import RetrievalQA

load_dotenv()


# ──────────────────────────────────────────────
# Step 1: 문서 로드 (Load)
# ──────────────────────────────────────────────
def load_documents():
    """텍스트 파일을 Document 객체로 로드합니다."""
    loader = TextLoader("sample_documents/company_policy.txt", encoding="utf-8")
    documents = loader.load()
    print(f"[로드 완료] 문서 {len(documents)}개 로드됨")
    print(f"  - 첫 100자: {documents[0].page_content[:100]}...")
    return documents


# ──────────────────────────────────────────────
# Step 2: 텍스트 분할 (Split)
# ──────────────────────────────────────────────
def split_documents(documents):
    """
    긴 문서를 작은 청크로 분할합니다.

    왜 분할하는가?
    - LLM의 컨텍스트 윈도우에는 제한이 있음
    - 작은 청크일수록 관련 내용만 정확히 검색 가능
    - 임베딩 품질도 짧은 텍스트에서 더 좋음

    주요 파라미터:
    - chunk_size: 각 청크의 최대 문자 수
    - chunk_overlap: 청크 간 겹치는 문자 수 (문맥 유지용)
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,       # 각 청크 최대 300자
        chunk_overlap=50,     # 인접 청크와 50자 겹침
        separators=["\n\n", "\n", ". ", " ", ""],  # 분할 우선순위
    )
    chunks = text_splitter.split_documents(documents)
    print(f"\n[분할 완료] {len(chunks)}개 청크 생성됨")
    for i, chunk in enumerate(chunks):
        print(f"  청크 {i}: {chunk.page_content[:60]}...")
    return chunks


# ──────────────────────────────────────────────
# Step 3: 임베딩 & 벡터 저장 (Embed & Store)
# ──────────────────────────────────────────────
def create_vectorstore(chunks):
    """
    텍스트를 벡터로 변환하고 벡터 DB에 저장합니다.

    임베딩이란?
    - 텍스트를 고차원 숫자 벡터로 변환하는 것
    - 의미가 비슷한 텍스트는 벡터 공간에서 가까이 위치
    - 이를 통해 "의미 기반 검색"이 가능해짐
    """
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db",  # 디스크에 저장
    )
    print(f"\n[벡터 저장 완료] ChromaDB에 {len(chunks)}개 벡터 저장됨")
    return vectorstore


# ──────────────────────────────────────────────
# Step 4: 검색 (Retrieve)
# ──────────────────────────────────────────────
def test_retrieval(vectorstore):
    """
    질문과 유사한 문서 청크를 검색합니다.

    retriever의 search_kwargs:
    - k: 반환할 문서 수 (기본 4)
    """
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    query = "연차는 며칠인가요?"
    results = retriever.invoke(query)

    print(f"\n[검색 테스트] 질문: '{query}'")
    print(f"  검색된 문서 {len(results)}개:")
    for i, doc in enumerate(results):
        print(f"  --- 결과 {i+1} ---")
        print(f"  {doc.page_content[:100]}...")
    return retriever


# ──────────────────────────────────────────────
# Step 5: QA 체인 (Generate)
# ──────────────────────────────────────────────
def create_qa_chain(vectorstore):
    """
    검색 결과를 바탕으로 LLM이 답변을 생성합니다.

    RetrievalQA 체인의 동작:
    1. 사용자 질문을 임베딩
    2. 벡터 DB에서 유사 문서 검색
    3. 검색된 문서 + 질문을 LLM에 전달
    4. LLM이 문서 기반으로 답변 생성
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",  # 검색 결과를 모두 하나의 프롬프트에 넣는 방식
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=True,  # 참조 문서도 함께 반환
    )
    return qa_chain


def ask_question(qa_chain, question):
    """질문하고 답변을 출력합니다."""
    result = qa_chain.invoke({"query": question})
    print(f"\n{'='*50}")
    print(f"Q: {question}")
    print(f"A: {result['result']}")
    print(f"\n참조 문서 {len(result['source_documents'])}개:")
    for i, doc in enumerate(result["source_documents"]):
        print(f"  [{i+1}] {doc.page_content[:80]}...")
    return result


# ──────────────────────────────────────────────
# 실행
# ──────────────────────────────────────────────
if __name__ == "__main__":
    # 전체 파이프라인 실행
    documents = load_documents()
    chunks = split_documents(documents)
    vectorstore = create_vectorstore(chunks)
    test_retrieval(vectorstore)

    # QA 체인으로 질문하기
    qa_chain = create_qa_chain(vectorstore)

    questions = [
        "연차는 며칠인가요?",
        "재택근무는 주 몇 회까지 가능한가요?",
        "점심 식대는 얼마를 지원하나요?",
        "성과 평가 S등급의 성과급은 몇 퍼센트인가요?",
    ]

    for q in questions:
        ask_question(qa_chain, q)
