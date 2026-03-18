"""
===============================================
  실습 2: 문서 분할 & 벡터 검색 체험
===============================================

목표:
  1) 문서를 청크로 분할하는 과정을 눈으로 확인
  2) chunk_size에 따른 차이를 실험
  3) 벡터 검색이 키워드 검색과 어떻게 다른지 비교

실행: python tutorials/practice_02_split_and_search.py
"""

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

load_dotenv()


def part1_text_splitting():
    """Part 1: 텍스트 분할 과정을 눈으로 확인"""
    print("=" * 60)
    print("Part 1: 텍스트 분할 과정")
    print("=" * 60)

    # 문서 로드
    loader = TextLoader("sample_documents/company_policy.txt", encoding="utf-8")
    documents = loader.load()
    doc = documents[0]

    print(f"\n원본 문서 길이: {len(doc.page_content)}자")
    print(f"원본 메타데이터: {doc.metadata}")

    # 다양한 chunk_size로 분할 실험
    print("\n--- chunk_size별 분할 결과 비교 ---")
    for size in [100, 200, 300, 500]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=size,
            chunk_overlap=30,
        )
        chunks = splitter.split_documents(documents)
        print(f"\n  chunk_size={size:>4} → {len(chunks):>2}개 청크")
        # 첫 번째 청크 내용 미리보기
        print(f"    첫 청크: {chunks[0].page_content[:50]}...")

    # chunk_size=200으로 상세 확인
    print("\n\n--- chunk_size=200 상세 결과 ---")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=30,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)

    for i, chunk in enumerate(chunks):
        print(f"\n[청크 {i+1}] ({len(chunk.page_content)}자)")
        print(f"{'─'*40}")
        print(chunk.page_content)

    return chunks


def part2_keyword_vs_semantic():
    """Part 2: 키워드 검색 vs 시맨틱(의미) 검색 비교"""
    print("\n\n" + "=" * 60)
    print("Part 2: 키워드 검색 vs 시맨틱 검색")
    print("=" * 60)

    # 문서 준비
    loader = TextLoader("sample_documents/company_policy.txt", encoding="utf-8")
    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=30)
    chunks = splitter.split_documents(documents)

    # 벡터 저장소 생성
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma.from_documents(chunks, embeddings)

    # 비교할 질문들
    test_queries = [
        # (질문, 설명)
        ("연차", "정확한 키워드"),
        ("쉬는 날이 며칠인가요?", "키워드 '연차' 없이 의미만"),
        ("돈으로 지원해주는 것들", "구어체/비공식 표현"),
        ("집에서 일하는 규정", "'재택근무' 키워드 없이"),
    ]

    for query, desc in test_queries:
        print(f"\n{'─'*50}")
        print(f"질문: '{query}' ({desc})")

        # 키워드 검색 (단순 문자열 포함 여부)
        keyword_results = []
        for chunk in chunks:
            if query in chunk.page_content:
                keyword_results.append(chunk.page_content[:60])

        print(f"\n  [키워드 검색] 결과 {len(keyword_results)}건:")
        if keyword_results:
            for r in keyword_results[:2]:
                print(f"    → {r}...")
        else:
            print(f"    → 결과 없음 ❌ ('{query}'라는 글자가 없으니까)")

        # 시맨틱 검색 (의미 기반)
        semantic_results = vectorstore.similarity_search_with_score(query, k=2)
        print(f"\n  [시맨틱 검색] 결과 {len(semantic_results)}건:")
        for doc, score in semantic_results:
            print(f"    → (거리: {score:.4f}) {doc.page_content[:60]}...")

    return vectorstore


def part3_interactive_search(vectorstore):
    """Part 3: 직접 검색해보기"""
    print("\n\n" + "=" * 60)
    print("Part 3: 직접 검색해보기 (종료: quit)")
    print("=" * 60)
    print("질문을 입력하면 유사한 문서를 검색합니다.\n")

    while True:
        query = input("검색어: ").strip()
        if query.lower() in ("quit", "exit", "q"):
            break
        if not query:
            continue

        results = vectorstore.similarity_search_with_score(query, k=3)
        print(f"\n  검색 결과 (상위 3개):")
        for i, (doc, score) in enumerate(results):
            print(f"  [{i+1}] 거리: {score:.4f}")
            print(f"      {doc.page_content[:100]}...")
        print()


if __name__ == "__main__":
    chunks = part1_text_splitting()
    vectorstore = part2_keyword_vs_semantic()
    part3_interactive_search(vectorstore)
