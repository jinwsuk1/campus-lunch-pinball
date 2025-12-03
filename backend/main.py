# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Literal
from auth import router as auth_router


app = FastAPI(title="Campus Lunch Roulette API")

app.include_router(auth_router)

# 프론트에서 접근 허용 (개발 단계라 * 허용)
origins = [
    "http://localhost:1234",  # parcel dev server (대부분 1234 포트)
    "http://127.0.0.1:1234",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins + ["*"],  # 개발 편의상 * 도 같이 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 카테고리 타입 (일단 문자열 literal)
Category = Literal["korean", "japanese", "chinese", "snack", "cafe"]

# 임시 하드코딩 식당 목록 (나중에 DB로 교체)
MOCK_RESTAURANTS = [
    {"id": 1, "name": "김밥천국 정문점", "category": "korean"},
    {"id": 2, "name": "한솥도시락 후문점", "category": "korean"},
    {"id": 3, "name": "스시로", "category": "japanese"},
    {"id": 4, "name": "홍콩반점", "category": "chinese"},
    {"id": 5, "name": "엽기떡볶이", "category": "snack"},
    {"id": 6, "name": "이디야커피 정문점", "category": "cafe"},
]

@app.get("/api/restaurants")
def list_restaurants(categories: list[Category] | None = None):
    """
    카테고리로 필터링된 식당 목록 반환.
    categories 파라미터가 없으면 전체 반환.
    예: /api/restaurants?categories=korean&categories=snack
    """
    if not categories:
        return MOCK_RESTAURANTS

    filtered = [r for r in MOCK_RESTAURANTS if r["category"] in categories]
    return filtered

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
