"""
=== 5단계: PDF 문서 RAG ===

실무에서 가장 많이 쓰이는 PDF 문서 기반 RAG입니다.
PDF 로더 사용법과 페이지 단위 메타데이터 활용을 보여줍니다.

사용법:
  sample_documents/ 폴더에 .pdf 파일을 넣고 실행하세요.
"""

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
import os

load_dotenv()

PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""다음 문서 내용을 참고하여 질문에 답변하세요.
답변 시 출처 페이지 번호도 함께 알려주세요.
문서에 없는 내용은 "문서에서 해당 정보를 찾을 수 없습니다"라고 답변하세요.

문서 내용:
{context}

질문: {question}

답변:""",
)


def build_pdf_rag(pdf_directory="sample_documents/"):
    """PDF 파일들로 RAG 파이프라인을 구성합니다."""

    # PDF 파일 확인
    pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith(".pdf")]
    if not pdf_files:
        print(f"'{pdf_directory}' 에 PDF 파일이 없습니다.")
        print("PDF 파일을 넣고 다시 실행해주세요.")
        return None

    # PDF 로드 (페이지별로 자동 분리됨)
    loader = DirectoryLoader(
        pdf_directory,
        glob="*.pdf",
        loader_cls=PyPDFLoader,
    )
    documents = loader.load()
    print(f"[로드 완료] {len(documents)}페이지 로드됨")

    # 각 페이지의 메타데이터 확인
    for doc in documents[:3]:
        print(f"  - {doc.metadata.get('source', '?')} p.{doc.metadata.get('page', '?')}")

    # 텍스트 분할
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"[분할 완료] {len(chunks)}개 청크")

    # 벡터 저장소 & QA 체인
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT},
    )
    return qa_chain


if __name__ == "__main__":
    print("=" * 60)
    print("PDF 문서 RAG")
    print("=" * 60)

    qa_chain = build_pdf_rag()
    if qa_chain is None:
        exit()

    while True:
        question = input("\n질문 (종료: quit): ").strip()
        if question.lower() in ("quit", "exit", "q"):
            break
        if not question:
            continue

        result = qa_chain.invoke({"query": question})
        print(f"\nA: {result['result']}")
        print("\n참조 출처:")
        for doc in result["source_documents"]:
            source = doc.metadata.get("source", "unknown")
            page = doc.metadata.get("page", "?")
            print(f"  - {source} (p.{page})")
