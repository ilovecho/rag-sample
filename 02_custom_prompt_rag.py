"""
=== 2단계: 커스텀 프롬프트 RAG ===

기본 RAG에서 한 단계 더 나아가:
- 프롬프트 템플릿을 커스터마이징하여 답변 품질 향상
- 답변 언어, 톤, 형식을 제어
"""

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv()


# ──────────────────────────────────────────────
# 여러 문서를 한번에 로드
# ──────────────────────────────────────────────
def load_all_documents():
    """디렉토리 내 모든 txt 파일을 로드합니다."""
    loader = DirectoryLoader(
        "sample_documents/",
        glob="*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    documents = loader.load()
    print(f"[로드 완료] {len(documents)}개 문서 로드됨")
    for doc in documents:
        print(f"  - {doc.metadata['source']}")
    return documents


# ──────────────────────────────────────────────
# 커스텀 프롬프트 템플릿
# ──────────────────────────────────────────────

# 한국어 답변 + 친절한 톤
CUSTOM_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""당신은 회사의 친절한 AI 어시스턴트입니다.
아래 참고 자료를 바탕으로 질문에 답변해주세요.

규칙:
1. 반드시 한국어로 답변하세요.
2. 참고 자료에 없는 내용은 "해당 정보를 찾을 수 없습니다"라고 답변하세요.
3. 답변은 간결하고 명확하게 작성하세요.
4. 가능하면 구체적인 수치나 조건을 포함하세요.

참고 자료:
{context}

질문: {question}

답변:""",
)

# 표 형식 답변용 프롬프트
TABLE_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""아래 참고 자료를 기반으로 질문에 답변하세요.
답변은 가능하면 표(마크다운) 형식으로 정리하세요.

참고 자료:
{context}

질문: {question}

답변 (표 형식 선호):""",
)


def build_rag_pipeline(prompt_template):
    """커스텀 프롬프트로 RAG 파이프라인을 구성합니다."""
    # 1. 문서 로드 & 분할
    documents = load_all_documents()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300, chunk_overlap=50
    )
    chunks = text_splitter.split_documents(documents)

    # 2. 벡터 저장소 생성
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
    )

    # 3. 커스텀 프롬프트로 QA 체인 생성
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt_template},  # 커스텀 프롬프트!
    )
    return qa_chain


if __name__ == "__main__":
    # 커스텀 프롬프트 RAG
    print("=" * 60)
    print("커스텀 프롬프트 RAG 테스트")
    print("=" * 60)

    qa_chain = build_rag_pipeline(CUSTOM_PROMPT)

    questions = [
        "회사에서 지원하는 복리후생을 알려주세요",
        "SmartWidget Pro의 요금제를 비교해주세요",
        "재택근무 규정이 어떻게 되나요?",
        "회사 주차장 이용 방법이 궁금합니다",  # 문서에 없는 정보
    ]

    for q in questions:
        result = qa_chain.invoke({"query": q})
        print(f"\nQ: {q}")
        print(f"A: {result['result']}")
        print("-" * 40)
