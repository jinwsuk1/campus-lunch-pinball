# backend/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.oauth2 import id_token
from google.auth.transport import requests

router = APIRouter(prefix="/api", tags=["auth"])

auth_scheme = HTTPBearer()

# 🔽 Firebase 프로젝트 ID (firebaseConfig 의 projectId 값)
FIREBASE_PROJECT_ID = "campus-lunch-pinball"


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
):
    token = creds.credentials
    user = verify_firebase_id_token(token)
    return user


@router.get("/me")
async def read_me(user: dict = Depends(get_current_user)):
    """
    로그인된 사용자 정보 확인용 엔드포인트.
    """
    return {
        "uid": user.get("uid") or user.get("user_id"),
        "email": user.get("email"),
        "name": user.get("name"),
        "picture": user.get("picture"),
    }
