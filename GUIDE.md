# RAG 학습 샘플 프로젝트

## 프로젝트 구조

```
rag-sample/
├── .env.example          # API 키 설정 (복사해서 .env 생성)
├── requirements.txt      # 의존성 패키지
├── sample_documents/     # 샘플 문서
│   ├── company_policy.txt
│   └── product_guide.txt
├── 01_basic_rag.py       # 기본 RAG 파이프라인
├── 02_custom_prompt_rag.py   # 커스텀 프롬프트 RAG
├── 03_conversational_rag.py  # 대화형 RAG (채팅)
├── 04_advanced_rag.py    # 고급 검색 기법
└── 05_pdf_rag.py         # PDF 문서 RAG
```

## 시작하기

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 환경변수 설정
cp .env.example .env
# .env 파일에 OpenAI API 키 입력

# 3. 단계별 실행
python 01_basic_rag.py
python 02_custom_prompt_rag.py
python 03_conversational_rag.py
python 04_advanced_rag.py
python 05_pdf_rag.py  # PDF 파일 필요
```

## 학습 순서

| 단계 | 파일 | 핵심 개념 |
|------|------|-----------|
| 1 | `01_basic_rag.py` | 로드→분할→임베딩→검색→생성 기본 흐름 |
| 2 | `02_custom_prompt_rag.py` | 프롬프트 템플릿으로 답변 품질 제어 |
| 3 | `03_conversational_rag.py` | 대화 히스토리 + RAG 결합 |
| 4 | `04_advanced_rag.py` | MMR, 메타데이터, 멀티쿼리 검색 |
| 5 | `05_pdf_rag.py` | PDF 문서 처리 실전 예제 |

## RAG 파이프라인 핵심 흐름

```
[문서] → Load → Split → Embed → Store(VectorDB)
                                      ↓
[질문] → Embed → Search(유사도) → [관련 청크들]
                                      ↓
                              [질문 + 청크들] → LLM → [답변]
```

## 주요 파라미터 튜닝 가이드

- **chunk_size**: 작게(200) → 정밀 검색, 크게(1000) → 맥락 보존
- **chunk_overlap**: 청크 간 겹침. 맥락 끊김 방지 (보통 chunk_size의 10~20%)
- **k (검색 개수)**: 많이 → 정보 풍부하지만 노이즈 증가
- **temperature**: 0 → 일관된 답변, 높게 → 창의적 답변
