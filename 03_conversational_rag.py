"""
=== 3단계: 대화형 RAG (Conversational RAG) ===

이전 대화를 기억하면서 문서 기반 답변을 하는 챗봇입니다.

핵심 개념:
- ConversationBufferMemory: 대화 히스토리 저장
- ConversationalRetrievalChain: 대화 맥락 + 문서 검색을 결합
"""

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

load_dotenv()


def build_conversational_rag():
    """대화형 RAG 체인을 구성합니다."""
    # 문서 로드 & 분할
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

    # 벡터 저장소
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings)

    # 대화 메모리
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,   # Message 객체로 반환
        output_key="answer",    # 답변 키 지정
    )

    # 대화형 RAG 체인
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        memory=memory,
        return_source_documents=True,
    )
    return chain


def chat(chain, question):
    """대화형으로 질문합니다."""
    result = chain.invoke({"question": question})
    print(f"\n사용자: {question}")
    print(f"AI: {result['answer']}")
    return result


if __name__ == "__main__":
    print("=" * 60)
    print("대화형 RAG 챗봇 (종료: 'quit' 입력)")
    print("=" * 60)

    chain = build_conversational_rag()

    # 데모: 연속 대화 (이전 맥락을 기억함)
    print("\n--- 데모 대화 ---")
    chat(chain, "SmartWidget Pro의 요금제 종류를 알려주세요")
    chat(chain, "그 중에서 AI 분석이 포함된 건 어떤 건가요?")  # '그 중에서' → 이전 맥락 참조
    chat(chain, "그 플랜의 가격은 얼마인가요?")  # '그 플랜' → 이전 답변 참조

    # 인터랙티브 모드
    print("\n\n--- 자유 대화 모드 ---")
    while True:
        user_input = input("\n질문: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            print("종료합니다.")
            break
        if not user_input:
            continue
        chat(chain, user_input)
