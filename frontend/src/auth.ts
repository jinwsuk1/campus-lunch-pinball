// src/auth.ts
import { auth, googleProvider } from "./firebase";
import {
  signInWithPopup,
  signOut,
  onAuthStateChanged,
  User,
} from "firebase/auth";

let currentUser: User | null = null;
let currentIdToken: string | null = null;

// 다른 스크립트에서 토큰을 쓸 수 있게 window 에 저장
// eslint-disable-next-line
(window as any).currentIdToken = null;

async function loginWithGoogle() {
  try {
    const result = await signInWithPopup(auth, googleProvider);
    const user = result.user;
    currentUser = user;
    currentIdToken = await user.getIdToken();
    (window as any).currentIdToken = currentIdToken;
    updateAuthUI();
    console.log("Firebase ID token:", currentIdToken);
  } catch (e) {
    console.error(e);
    alert("로그인 중 오류가 발생했습니다.");
  }
}

async function logout() {
  await signOut(auth);
  currentUser = null;
  currentIdToken = null;
  (window as any).currentIdToken = null;
  updateAuthUI();
}

function updateAuthUI() {
  const userInfo = document.getElementById("user-info");
  const loginBtn = document.getElementById("login-btn") as
    | HTMLButtonElement
    | null;
  const logoutBtn = document.getElementById("logout-btn") as
    | HTMLButtonElement
    | null;

  if (!userInfo || !loginBtn || !logoutBtn) return;

  if (currentUser) {
    userInfo.textContent = `${currentUser.displayName || ""} (${
      currentUser.email || ""
    })`;
    loginBtn.style.display = "none";
    logoutBtn.style.display = "inline-block";
  } else {
    userInfo.textContent = "로그인하지 않음";
    loginBtn.style.display = "inline-block";
    logoutBtn.style.display = "none";
  }
}

function initAuthUI() {
  const loginBtn = document.getElementById("login-btn");
  const logoutBtn = document.getElementById("logout-btn");

  if (loginBtn) {
    loginBtn.addEventListener("click", () => {
      loginWithGoogle();
    });
  }

  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      logout();
    });
  }

  // 새로고침 후 상태 반영
  onAuthStateChanged(auth, async (user) => {
    currentUser = user;
    if (user) {
      currentIdToken = await user.getIdToken();
      (window as any).currentIdToken = currentIdToken;
    } else {
      currentIdToken = null;
      (window as any).currentIdToken = null;
    }
    updateAuthUI();
  });
}

// /api/me 호출해서 토큰이 실제로 동작하는지 테스트
async function callBackendMe() {
  const token = (window as any).currentIdToken as string | null;
  if (!token) {
    alert("먼저 Google 로그인을 해 주세요.");
    return;
  }

  try {
    const res = await fetch("http://127.0.0.1:8000/api/me", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!res.ok) {
      const text = await res.text();
      console.error("Backend error:", res.status, text);
      alert("서버에서 인증 실패: " + res.status);
      return;
    }

    const data = await res.json();
    console.log("Backend /api/me:", data);
    alert(`서버에서 받은 유저 정보:\n${data.email}\n${data.name}`);
  } catch (e) {
    console.error(e);
    alert("백엔드 호출 중 오류가 발생했습니다.");
  }
}

function initBackendTestButton() {
  const btnTest = document.getElementById("btnTestMe");
  if (btnTest) {
    btnTest.addEventListener("click", () => {
      callBackendMe();
    });
  }
}

/**
 * 여기서 바로 초기화 함수를 호출한다.
 * index.html 의 script 가 body 끝에 있기 때문에
 * 이 시점에는 DOM 이 이미 만들어져 있어서 DOMContentLoaded 를 기다릴 필요가 없다.
 */
function initAuth() {
  initAuthUI();
  initBackendTestButton();
}

// 모듈 로드 시 바로 실행
initAuth();
