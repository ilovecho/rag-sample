# RAG 학습 샘플 프로젝트

> **RAG(Retrieval-Augmented Generation)** 를 처음부터 단계별로 학습할 수 있는 프로젝트입니다.
> 개념 이해부터 실전 구현까지, 한국어 예제와 실습 코드를 포함하고 있습니다.

---

## 프로젝트 구조

```
rag-sample/
├── .env.example                # API 키 설정 템플릿
├── requirements.txt            # 의존성 패키지
├── README.md                   # 이 파일
├── GUIDE.md                    # 간략 가이드
├── RAG_학습_가이드.docx          # 전체 학습 내용 (Word 문서)
│
├── sample_documents/           # 샘플 문서 (RAG 데이터 소스)
│   ├── company_policy.txt      #   회사 정책 문서
│   └── product_guide.txt       #   제품 가이드 문서
│
├── 01_basic_rag.py             # 기본 RAG 파이프라인
├── 02_custom_prompt_rag.py     # 커스텀 프롬프트 RAG
├── 03_conversational_rag.py    # 대화형 RAG (챗봇)
├── 04_advanced_rag.py          # 고급 검색 기법
├── 05_pdf_rag.py               # PDF 문서 RAG
│
└── tutorials/                  # 초보자용 학습 자료
    ├── 01_RAG란_무엇인가.md
    ├── 02_임베딩과_벡터DB_이해하기.md
    ├── 03_단계별_실습_튜토리얼.md
    ├── 04_용어사전.md
    ├── 05_자주하는_실수와_트러블슈팅.md
    ├── 06_학습_로드맵.md
    ├── practice_01_embedding.py
    ├── practice_02_split_and_search.py
    └── practice_03_full_rag.py
```

---

## 패키지 설명

| 패키지 | 버전 | 역할 |
|--------|------|------|
| `langchain` | 0.3.25 | RAG 파이프라인의 핵심 프레임워크. 문서 로드, 텍스트 분할, 체인 구성, 리트리버 등 RAG의 모든 구성 요소를 조립하는 데 사용됩니다. |
| `langchain-openai` | 0.3.12 | LangChain에서 OpenAI의 LLM(GPT-4o-mini 등)과 임베딩 모델(text-embedding-3-small)을 사용하기 위한 연동 패키지입니다. |
| `langchain-community` | 0.3.24 | 커뮤니티에서 제공하는 다양한 통합 도구 모음. ChromaDB, FAISS 벡터 저장소 연동과 TextLoader, DirectoryLoader 등 문서 로더를 포함합니다. |
| `chromadb` | 1.0.7 | 오픈소스 벡터 데이터베이스. 임베딩 벡터를 로컬에 저장하고 유사도 기반 검색을 수행합니다. 설치가 간단하여 학습/프로토타입에 적합합니다. |
| `tiktoken` | 0.9.0 | OpenAI 모델의 토크나이저. 텍스트를 토큰 단위로 분할하거나 토큰 수를 계산할 때 사용됩니다. LangChain 내부에서 자동으로 활용됩니다. |
| `pypdf` | 5.6.0 | PDF 파일에서 텍스트를 추출하는 라이브러리. `05_pdf_rag.py`에서 PyPDFLoader가 내부적으로 사용합니다. |
| `python-dotenv` | 1.1.0 | `.env` 파일에서 환경 변수(API 키 등)를 읽어오는 라이브러리. `load_dotenv()`를 호출하면 `.env`의 값이 자동으로 환경 변수에 로드됩니다. |
| `faiss-cpu` | 1.13.2 | Meta(Facebook)에서 개발한 고속 벡터 유사도 검색 라이브러리. ChromaDB의 대안으로, 대규모 데이터에서 더 빠른 검색 성능을 제공합니다. |

---

## 실행 방법

### 1. 사전 요구 사항

- **Python 3.10 이상** 설치 필요
- **OpenAI API 키** 필요 ([발급 페이지](https://platform.openai.com/api-keys))

### 2. 환경 설정

```bash
# 프로젝트 폴더로 이동
cd rag-sample

# 가상환경 생성 (권장)
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 3. API 키 설정

```bash
# .env.example을 복사하여 .env 파일 생성
copy .env.example .env        # Windows
# cp .env.example .env        # Mac/Linux
```

`.env` 파일을 열고 실제 API 키를 입력합니다:
```
OPENAI_API_KEY=sk-여기에-실제-API-키를-입력하세요
```

> **주의**: `.env` 파일에 따옴표나 공백을 넣지 마세요.
> - ✅ `OPENAI_API_KEY=sk-abc123...`
> - ❌ `OPENAI_API_KEY="sk-abc123..."`
> - ❌ `OPENAI_API_KEY = sk-abc123...`

### 4. 샘플 코드 실행

각 파일을 순서대로 실행하며 학습합니다:

```bash
# 1단계: 기본 RAG 파이프라인 (가장 먼저 실행!)
python 01_basic_rag.py

# 2단계: 커스텀 프롬프트로 답변 품질 제어
python 02_custom_prompt_rag.py

# 3단계: 대화형 RAG 챗봇 (대화 맥락 유지)
python 03_conversational_rag.py

# 4단계: 고급 검색 기법 (MMR, 메타데이터, 멀티쿼리)
python 04_advanced_rag.py

# 5단계: PDF 문서 RAG (sample_documents/에 PDF 파일 필요)
python 05_pdf_rag.py
```

### 5. 초보자 실습 코드 실행

`tutorials/` 폴더의 실습 코드는 개념을 체험할 수 있도록 설계되었습니다:

```bash
# 임베딩 체험 (텍스트 → 벡터 변환, 유사도 비교)
python tutorials/practice_01_embedding.py

# 문서 분할 & 키워드 vs 시맨틱 검색 비교
python tutorials/practice_02_split_and_search.py

# RAG 전체 파이프라인 조립 (파라미터 수정 실험 가능)
python tutorials/practice_03_full_rag.py
```

---

## 학습 순서

### 개념 학습 (tutorials/ 문서)

| 순서 | 파일 | 내용 |
|------|------|------|
| 1 | `tutorials/01_RAG란_무엇인가.md` | RAG 개념, 필요성, 전체 흐름, 비유 |
| 2 | `tutorials/02_임베딩과_벡터DB_이해하기.md` | 임베딩, 코사인 유사도, 텍스트 분할, 벡터DB |
| 3 | `tutorials/03_단계별_실습_튜토리얼.md` | 코드 따라치며 배우는 5개 실습 |
| 4 | `tutorials/04_용어사전.md` | 모르는 용어 찾아보기 |
| 5 | `tutorials/05_자주하는_실수와_트러블슈팅.md` | 8가지 흔한 실수 + 디버깅 체크리스트 |
| 6 | `tutorials/06_학습_로드맵.md` | 다음 단계 학습 가이드 |

### 코드 실습

| 단계 | 파일 | 핵심 개념 |
|------|------|-----------|
| 1 | `01_basic_rag.py` | 로드 → 분할 → 임베딩 → 검색 → 생성 기본 흐름 |
| 2 | `02_custom_prompt_rag.py` | 프롬프트 템플릿으로 답변 품질 제어 |
| 3 | `03_conversational_rag.py` | 대화 히스토리 + RAG 결합 (챗봇) |
| 4 | `04_advanced_rag.py` | MMR, 메타데이터 필터링, 멀티쿼리 검색 |
| 5 | `05_pdf_rag.py` | PDF 문서 처리 실전 예제 |

### 추천 학습 흐름

```
개념 문서 01~02 읽기
      ↓
practice_01_embedding.py 실행 (임베딩 체험)
      ↓
개념 문서 03 따라하기
      ↓
practice_02, practice_03 실험
      ↓
01~05 샘플 코드 분석 & 실행
      ↓
자신의 문서로 RAG 시스템 구축!
```

---

## RAG 파이프라인 핵심 흐름

```
[문서] → Load → Split → Embed → Store(VectorDB)
                                      ↓
[질문] → Embed → Search(유사도) → [관련 청크들]
                                      ↓
                              [질문 + 청크들] → LLM → [답변]
```

---

## 주요 파라미터 튜닝 가이드

| 파라미터 | 작게 | 크게 | 추천 시작값 |
|---------|------|------|------------|
| `chunk_size` | 정밀 검색, 문맥 부족 | 맥락 보존, 노이즈 증가 | 300~500 |
| `chunk_overlap` | 문맥 끊김 위험 | 중복 증가 | chunk_size의 10~20% |
| `k` (검색 개수) | 정확하지만 정보 부족 | 풍부하지만 노이즈 | 2~4 |
| `temperature` | 일관된 답변 | 창의적 답변 | 0 (사실 기반 추천) |

---

## 트러블슈팅

| 문제 | 해결 |
|------|------|
| API 키 에러 | `.env` 파일 확인, 따옴표/공백 없이 키 입력, `load_dotenv()` 호출 확인 |
| 인코딩 에러 | `TextLoader("파일.txt", encoding="utf-8")` 지정 |
| 검색 결과가 엉뚱함 | `k` 줄이기, `chunk_size` 조정, 유사도 점수 확인 |
| 답변이 문서를 무시 | 프롬프트에 "문서만 근거로 답변" 명시 |
| 패키지 설치 오류 | Python 3.10+ 확인, 가상환경 활성화 확인 |

자세한 트러블슈팅은 `tutorials/05_자주하는_실수와_트러블슈팅.md`를 참고하세요.
