# auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.oauth2 import id_token
from google.auth.transport import requests
from sqlalchemy.orm import Session
from pydantic import BaseModel

from db import get_db
from models import User, UserPreference

router = APIRouter(prefix="/api", tags=["auth"])

auth_scheme = HTTPBearer()

# Firebase 프로젝트 ID (firebaseConfig 의 projectId 값과 동일해야 함)
FIREBASE_PROJECT_ID = "campus-lunch-pinball"  # 여기를 네 값으로 맞춰줘


def verify_firebase_id_token(token: str) -> dict:
    """
    Firebase ID 토큰 검증 후 payload 반환.
    검증 실패 시 HTTPException 발생.
    """
    try:
        decoded = id_token.verify_firebase_token(
            token,
            requests.Request(),
            audience=FIREBASE_PROJECT_ID,
        )
        return decoded
    except Exception as e:
        print("Firebase token verify error:", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase ID token",
        )


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(auth_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = creds.credentials
    payload = verify_firebase_id_token(token)

    uid = payload.get("uid") or payload.get("user_id")
    if not uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload (no uid).",
        )

    user = db.query(User).filter(User.firebase_uid == uid).first()
    if not user:
        # 없으면 새로 생성
        user = User(
            firebase_uid=uid,
            email=payload.get("email"),
            display_name=payload.get("name"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user


@router.get("/me")
async def read_me(current_user: User = Depends(get_current_user)):
    """
    DB에 저장된 현재 로그인 사용자 정보 반환
    """
    return {
        "id": current_user.id,
        "uid": current_user.firebase_uid,
        "email": current_user.email,
        "name": current_user.display_name,
    }


# ===== 선호 카테고리 관련 =====
class PreferenceUpdate(BaseModel):
    default_categories: list[str]  # 예: ["korean", "snack"]


@router.get("/me/preferences")
async def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pref = (
        db.query(UserPreference)
        .filter(UserPreference.user_id == current_user.id)
        .first()
    )

    if not pref or not pref.default_categories:
        return {"default_categories": []}

    categories = [c for c in pref.default_categories.split(",") if c]
    return {"default_categories": categories}


@router.put("/me/preferences")
async def update_preferences(
    payload: PreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cat_str = ",".join(payload.default_categories)

    pref = (
        db.query(UserPreference)
        .filter(UserPreference.user_id == current_user.id)
        .first()
    )

    if pref is None:
        pref = UserPreference(
            user_id=current_user.id,
            default_categories=cat_str,
        )
        db.add(pref)
    else:
        pref.default_categories = cat_str

    db.commit()
    return {"default_categories": payload.default_categories}
