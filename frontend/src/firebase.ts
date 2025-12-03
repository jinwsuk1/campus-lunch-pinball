// src/firebase.ts
import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

// 🔽 Firebase 콘솔에서 복사한 설정으로 바꿔 넣기
const firebaseConfig = {
  apiKey: "AIzaSyCQtaX9NELWsfWSfVCk82Mz3vkBIoPzPng",
  authDomain: "campus-lunch-pinball.firebaseapp.com",
  projectId: "campus-lunch-pinball",
  storageBucket: "campus-lunch-pinball.firebasestorage.app",
  messagingSenderId: "173018551160",
  appId: "1:173018551160:web:af6f3822046c711e9d2e8d",
  measurementId: "G-7B2ZEVVK20"
};

export const firebaseApp = initializeApp(firebaseConfig);
export const auth = getAuth(firebaseApp);
export const googleProvider = new GoogleAuthProvider();
googleProvider.setCustomParameters({
  prompt: "select_account",
});

