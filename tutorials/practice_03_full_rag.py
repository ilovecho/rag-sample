"""
===============================================
  실습 3: 완전한 RAG 파이프라인 직접 만들기
===============================================

목표: 모든 과정을 하나씩 조립하면서 RAG 전체 흐름을 체험합니다.

각 단계를 순서대로 실행하면서 중간 결과를 확인할 수 있습니다.
코드의 각 부분을 수정해보면서 결과가 어떻게 달라지는지 실험해보세요!

실행: python tutorials/practice_03_full_rag.py
"""

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: 문서 로드
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def step1_load():
    """
    문서를 읽어서 Document 객체로 변환합니다.

    📝 실험해보세요:
    - sample_documents에 자신만의 txt 파일을 추가해보세요
    - 다른 주제의 문서를 넣으면 어떤 답변이 나올까요?
    """
    print("\n📌 STEP 1: 문서 로드")
    print("-" * 40)

    loader = DirectoryLoader(
        "sample_documents/",
        glob="*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    documents = loader.load()

    for doc in documents:
        print(f"  ✓ {doc.metadata['source']} ({len(doc.page_content)}자)")

    print(f"  총 {len(documents)}개 문서 로드 완료")
    return documents


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: 텍스트 분할
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def step2_split(documents):
    """
    문서를 적절한 크기의 청크로 분할합니다.

    📝 실험해보세요:
    - chunk_size를 100, 200, 500으로 바꿔보세요
    - chunk_overlap을 0으로 하면 어떻게 달라질까요?
    """
    print("\n📌 STEP 2: 텍스트 분할")
    print("-" * 40)

    # ┌──────────────────────────────────┐
    # │  🔧 여기를 수정해서 실험해보세요!  │
    # └──────────────────────────────────┘
    CHUNK_SIZE = 300          # 👈 이 값을 바꿔보세요 (100, 200, 300, 500)
    CHUNK_OVERLAP = 50        # 👈 이 값을 바꿔보세요 (0, 30, 50, 100)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)

    print(f"  설정: chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}")
    print(f"  결과: {len(chunks)}개 청크 생성")
    print(f"\n  처음 3개 청크 미리보기:")
    for i, chunk in enumerate(chunks[:3]):
        print(f"    [청크 {i+1}] ({len(chunk.page_content)}자)")
        print(f"    {chunk.page_content[:80]}...")

    return chunks


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3: 벡터 저장소 생성
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def step3_vectorstore(chunks):
    """
    청크를 임베딩하고 벡터DB에 저장합니다.

    이 단계에서:
    1. 각 청크의 텍스트를 OpenAI API로 보내서 벡터(1536차원)로 변환
    2. 변환된 벡터를 ChromaDB에 저장
    3. 검색 테스트로 동작 확인
    """
    print("\n📌 STEP 3: 벡터 저장소 생성")
    print("-" * 40)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
    )

    print(f"  ✓ {len(chunks)}개 청크를 벡터로 변환 & 저장 완료")

    # 검색 테스트
    print(f"\n  검색 테스트:")
    test_queries = ["연차 휴가", "제품 가격"]
    for query in test_queries:
        results = vectorstore.similarity_search(query, k=1)
        print(f"    '{query}' → {results[0].page_content[:50]}...")

    return vectorstore


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 4: 프롬프트 설계
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def step4_prompt():
    """
    LLM에 보낼 프롬프트를 설계합니다.

    프롬프트에서 제어할 수 있는 것:
    - 답변 언어 (한국어/영어)
    - 답변 톤 (격식체/비격식체)
    - 답변 형식 (자유 텍스트/불릿포인트/표)
    - 문서 외 정보에 대한 행동 (모른다고 답변/추측)

    📝 실험해보세요:
    - template 내용을 바꿔서 답변 스타일을 변경해보세요!
    """
    print("\n📌 STEP 4: 프롬프트 설계")
    print("-" * 40)

    # ┌──────────────────────────────────┐
    # │  🔧 프롬프트를 수정해서 실험!      │
    # └──────────────────────────────────┘
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""당신은 친절한 회사 AI 어시스턴트입니다.

아래 [참고 문서]를 근거로 질문에 답변하세요.

규칙:
1. 반드시 한국어로 답변하세요.
2. 참고 문서에 없는 내용은 "해당 정보를 찾을 수 없습니다"라고 답하세요.
3. 가능하면 구체적인 수치를 포함하세요.
4. 답변은 2~3문장으로 간결하게 작성하세요.

[참고 문서]
{context}

[질문]
{question}

[답변]""",
    )

    print("  ✓ 커스텀 프롬프트 생성 완료")
    print(f"  프롬프트 변수: {prompt.input_variables}")
    return prompt


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 5: RAG 체인 조립 & 실행
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def step5_qa(vectorstore, prompt):
    """
    모든 구성 요소를 조립하여 RAG 체인을 완성합니다.

    📝 실험해보세요:
    - temperature를 0.7로 바꿔보세요 (답변이 달라짐)
    - k를 1, 2, 5로 바꿔보세요 (검색 문서 수)
    - model을 "gpt-4o"로 바꿔보세요 (더 정확하지만 비용 ↑)
    """
    print("\n📌 STEP 5: RAG 체인 조립 & 질의응답")
    print("-" * 40)

    # ┌──────────────────────────────────┐
    # │  🔧 이 설정들을 바꿔서 실험!       │
    # └──────────────────────────────────┘
    MODEL = "gpt-4o-mini"    # 👈 "gpt-4o"로 바꿔보세요
    TEMPERATURE = 0          # 👈 0.7로 바꿔보세요
    K = 3                    # 👈 1, 2, 5로 바꿔보세요

    llm = ChatOpenAI(model=MODEL, temperature=TEMPERATURE)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": K}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )

    print(f"  설정: model={MODEL}, temperature={TEMPERATURE}, k={K}")

    # 테스트 질문들
    questions = [
        "신입사원은 연차가 며칠인가요?",
        "재택근무는 어떻게 신청하나요?",
        "SmartWidget Pro의 Professional 요금은?",
        "회사 주차장은 어디에 있나요?",  # 문서에 없는 정보!
    ]

    for q in questions:
        result = qa_chain.invoke({"query": q})
        print(f"\n  Q: {q}")
        print(f"  A: {result['result']}")

        # 참조한 문서 확인
        sources = set()
        for doc in result["source_documents"]:
            src = doc.metadata.get("source", "?")
            sources.add(src.split("/")[-1])
        print(f"  📄 참조: {', '.join(sources)}")

    return qa_chain


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 메인 실행
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if __name__ == "__main__":
    print("╔══════════════════════════════════════════╗")
    print("║   RAG 파이프라인 조립 실습                 ║")
    print("║   5단계를 순서대로 실행합니다               ║")
    print("╚══════════════════════════════════════════╝")

    # 각 단계를 순서대로 실행
    documents = step1_load()
    chunks = step2_split(documents)
    vectorstore = step3_vectorstore(chunks)
    prompt = step4_prompt()
    qa_chain = step5_qa(vectorstore, prompt)

    # 자유 질문 모드
    print("\n\n" + "=" * 60)
    print("자유 질문 모드 (종료: quit)")
    print("=" * 60)

    while True:
        question = input("\n질문: ").strip()
        if question.lower() in ("quit", "exit", "q"):
            print("실습을 종료합니다!")
            break
        if not question:
            continue

        result = qa_chain.invoke({"query": question})
        print(f"\nA: {result['result']}")
