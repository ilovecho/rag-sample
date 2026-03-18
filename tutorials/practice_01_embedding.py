"""
===============================================
  실습 1: 임베딩 체험하기
===============================================

목표: 텍스트가 어떻게 숫자(벡터)로 변환되는지 직접 확인합니다.

실행: python tutorials/practice_01_embedding.py
사전 조건: .env 파일에 OPENAI_API_KEY 설정
"""

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
import numpy as np

load_dotenv()


def cosine_similarity(a, b):
    """두 벡터의 코사인 유사도를 계산합니다 (0~1)."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def main():
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Part 1: 텍스트 → 벡터 변환
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("=" * 60)
    print("Part 1: 텍스트를 벡터로 변환하기")
    print("=" * 60)

    # 임베딩 모델 생성
    # text-embedding-3-small: 저렴하고 성능 좋은 모델 (1536차원)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # 하나의 텍스트를 벡터로 변환
    text = "고양이는 귀여운 동물이다"
    vector = embeddings.embed_query(text)

    print(f"\n원본 텍스트: {text}")
    print(f"벡터 차원 수: {len(vector)}")
    print(f"벡터 타입:    {type(vector)}")
    print(f"벡터 앞 5개:  {[round(v, 4) for v in vector[:5]]}")
    print(f"벡터 뒤 5개:  {[round(v, 4) for v in vector[-5:]]}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Part 2: 의미 유사도 비교
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n\n" + "=" * 60)
    print("Part 2: 의미가 비슷한 문장일수록 유사도가 높은지 확인")
    print("=" * 60)

    # 비교할 문장들
    sentences = [
        "고양이는 귀여운 동물이다",          # 원본
        "냥이는 사랑스러운 반려동물이다",     # 같은 의미, 다른 표현
        "강아지도 귀여운 동물이다",           # 부분적으로 유사
        "파이썬은 프로그래밍 언어이다",       # 관련 없음
        "오늘 주식이 폭락했다",              # 완전히 다른 주제
    ]

    # 모든 문장을 한 번에 임베딩
    # embed_query: 검색 질문용 (1개)
    # embed_documents: 문서 저장용 (여러 개)
    vectors = embeddings.embed_documents(sentences)

    print(f"\n기준 문장: '{sentences[0]}'")
    print("-" * 50)

    for i in range(1, len(sentences)):
        sim = cosine_similarity(vectors[0], vectors[i])
        # 시각적 막대 그래프
        bar_length = int(sim * 30)
        bar = "█" * bar_length + "░" * (30 - bar_length)
        print(f"  {sim:.4f} |{bar}| {sentences[i]}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Part 3: 직접 실험해보기
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n\n" + "=" * 60)
    print("Part 3: 직접 실험해보기 (종료: quit)")
    print("=" * 60)
    print("두 문장을 입력하면 유사도를 계산합니다.\n")

    while True:
        text1 = input("문장 1: ").strip()
        if text1.lower() in ("quit", "exit", "q"):
            break
        text2 = input("문장 2: ").strip()
        if text2.lower() in ("quit", "exit", "q"):
            break

        v1 = embeddings.embed_query(text1)
        v2 = embeddings.embed_query(text2)
        sim = cosine_similarity(v1, v2)

        bar_length = int(sim * 30)
        bar = "█" * bar_length + "░" * (30 - bar_length)
        print(f"\n  유사도: {sim:.4f} |{bar}|")

        if sim > 0.8:
            print("  → 매우 유사한 의미!")
        elif sim > 0.5:
            print("  → 어느 정도 관련 있음")
        else:
            print("  → 관련성 낮음")
        print()


if __name__ == "__main__":
    main()
