"use client";

import { useRouter } from "next/navigation";
import { useState, useCallback } from "react";
import { handleSocialLogin } from "@/services/page/pageService";
import type { OAuthProvider } from "@/types";

/**
 * 소셜 로그인 Hook (메인 페이지용)
 * 각 provider별 로딩 상태와 에러 관리
 */
export function useSocialLogin() {
  const router = useRouter();
  const [loading, setLoading] = useState<Record<OAuthProvider, boolean>>({
    kakao: false,
    naver: false,
    google: false,
  });
  const [error, setError] = useState<string | null>(null);

  // 소셜 로그인 핸들러 (무상태 함수 사용)
  const login = useCallback(
    async (provider: OAuthProvider) => {
      setLoading((prev) => ({ ...prev, [provider]: true }));
      setError(null);

      try {
        await handleSocialLogin(
          provider,
          // 성공 콜백
          () => {
            router.push("/dashboard");
          },
          // 에러 콜백
          (err) => {
            setError(err.message);
          }
        );
      } finally {
        setLoading((prev) => ({ ...prev, [provider]: false }));
      }
    },
    [router]
  );

  // Provider별 편의 함수
  const loginWithKakao = useCallback(() => login("kakao"), [login]);
  const loginWithNaver = useCallback(() => login("naver"), [login]);
  const loginWithGoogle = useCallback(() => login("google"), [login]);

  const isAnyLoading = Object.values(loading).some((isLoading) => isLoading);

  return {
    // 상태
    loading,
    error,
    isAnyLoading,

    // 액션 (새 함수명)
    login,
    loginWithKakao,
    loginWithNaver,
    loginWithGoogle,

    // 액션 (기존 함수명 - 하위 호환성)
    handleKakaoLogin: loginWithKakao,
    handleNaverLogin: loginWithNaver,
    handleGoogleLogin: loginWithGoogle,
    handleSocialLogin: login,

    clearError: () => setError(null),
  };
}

