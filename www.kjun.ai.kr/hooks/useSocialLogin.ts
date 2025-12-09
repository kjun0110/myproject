"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { type AuthProvider } from "@/lib/auth";
import { createSocialLoginHandlers } from "@/service/mainservice";

export function useSocialLogin() {
  const router = useRouter();
  const [loading, setLoading] = useState<Record<AuthProvider, boolean>>({
    kakao: false,
    naver: false,
    google: false,
  });
  const [error, setError] = useState<string | null>(null);

  // 서비스 레이어의 핸들러 생성 함수 사용
  const handlers = createSocialLoginHandlers(router, setLoading, setError);

  const isAnyLoading = Object.values(loading).some((isLoading) => isLoading);

  return {
    loading,
    error,
    setLoading,
    setError,
    isAnyLoading,
    ...handlers,
  };
}

