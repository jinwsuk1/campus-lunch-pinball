# main.py
from typing import Literal, List

from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from db import Base, engine, SessionLocal, get_db
from models import Restaurant
from auth import router as auth_router

app = FastAPI(title="Campus Lunch Roulette API")

origins = [
    "http://localhost:1234",
    "http://127.0.0.1:1234",
    "http://localhost:1235",
    "http://127.0.0.1:1235",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins + ["*"],  # 개발 편의상 * 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Category = Literal["korean", "japanese", "chinese", "snack", "cafe"]


@app.on_event("startup")
def on_startup():
    # DB 테이블 생성
    Base.metadata.create_all(bind=engine)

    # 기본 식당 데이터가 없으면 넣어두기
    db = SessionLocal()
    try:
        count = db.query(Restaurant).count()
        if count == 0:
            SEED_RESTAURANTS = [
                Restaurant(name="한뚝배기", category="korean", description="제육, 닭갈비, 김치찌개, 순두부찌개"),
                Restaurant(name="이모네", category="korean", description="육회비빔밥, 김치찌개, 뚝배기불고기"),
                Restaurant(name="이것이국밥이다", category="korean", description="돼지국밥, 순대국밥, 냉면"),
                Restaurant(name="메밀막국수", category="korean", description="메밀막국수, 비빔막국수, 소머리국밥"),
                Restaurant(name="감동까스", category="japanese", description="등심돈까스, 치즈돈까스, 카레"),
                Restaurant(name="잇또라멘", category="japanese", description="돈코츠라멘, 닌니쿠라멘, 쇼유라멘"),
                Restaurant(name="선착장", category="japanese", description="모듬초밥, 회덮밥, 회"),
                Restaurant(name="영춘원", category="chinese", description="마라탕, 꿔바로우, 우육탕면"),
                Restaurant(name="학사반점", category="chinese", description="짜장면, 짬뽕, 탕수육"),
                Restaurant(name="호랑", category="chinese", description="마파두부, 마라탕, 깐풍기"),
                Restaurant(name="마라순코우마라탕", category="chinese", description="마라탕 마라샹궈, 꿔바로우"),
                Restaurant(name="맘스터치", category="snack", description="싸이버거, 치킨, 떡강정"),
                Restaurant(name="동대문엽기떡볶이", category="snack", description="엽기떡볶이, 로제떡볶이, 튀김"),
                Restaurant(name="빠사시떡볶이&닭강정", category="snack", description="닭강정, 떡볶이, 꼬마김밥"),
                Restaurant(name="메가커피", category="cafe", description="아메리카노, 라떼, 스무디"),
                Restaurant(name="봉주르대곡리", category="cafe", description="아메리카노, 크로플, 토스트"),
                Restaurant(name="공차", category="cafe", description="밀크티, 스무디"),
                Restaurant(name="카페드림", category="cafe", description="아메리카노, 라떼, 디저트"),
            ]
            db.add_all(SEED_RESTAURANTS)
            db.commit()
            print("Seeded initial restaurants.")
    finally:
        db.close()


@app.get("/api/restaurants")
def list_restaurants(
    categories: List[Category] | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """
    카테고리로 필터링된 식당 목록 반환.
    categories 파라미터가 없으면 전체 반환.
    예: /api/restaurants?categories=korean&categories=snack
    """
    query = db.query(Restaurant).filter(Restaurant.is_active == True)  # noqa: E712

    if categories:
        query = query.filter(Restaurant.category.in_(categories))

    results = query.all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "category": r.category,
            "address": r.address,
            "description": r.description,
        }
        for r in results
    ]


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


# JWT/Firebase 관련 라우터
app.include_router(auth_router)
