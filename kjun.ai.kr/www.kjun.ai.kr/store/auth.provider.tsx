"use client";

import { useEffect, type ReactNode } from "react";
import { useAuthStore } from "./auth.store";

interface AuthProviderProps {
    children: ReactNode;
}

/**
 * Auth Provider
 * - Zustand Store 초기화 및 전역 상태 관리
 * - Next.js 16 App Router와 호환
 * - 클라이언트 컴포넌트로 동작
 */
export function AuthProvider({ children }: AuthProviderProps) {
    const refreshAccessToken = useAuthStore((state) => state.refreshAccessToken);
    const isLoggedIn = useAuthStore((state) => state.isLoggedIn);
    const accessToken = useAuthStore((state) => state.accessToken);
    const userInfo = useAuthStore((state) => state.userInfo);
    const loginProvider = useAuthStore((state) => state.loginProvider);

    // 초기화 시 현재 Zustand 상태 확인
    useEffect(() => {
        console.log("🚀 [Zustand] AuthProvider 초기화");
        console.log("📊 [Zustand] 현재 상태:", {
            hasAccessToken: !!accessToken,
            accessTokenLength: accessToken?.length || 0,
            accessTokenPreview: accessToken 
                ? (accessToken.length > 50 
                    ? `${accessToken.substring(0, 20)}...${accessToken.substring(accessToken.length - 10)}` 
                    : accessToken)
                : null,
            isLoggedIn,
            provider: loginProvider,
            hasUserInfo: !!userInfo,
        });
    }, []); // 마운트 시 한 번만 실행

    useEffect(() => {
        // 로그인 상태이지만 Access Token이 없는 경우 (새로고침 등)
        // HttpOnly 쿠키의 Refresh Token으로 Access Token 갱신 시도
        if (isLoggedIn && !accessToken) {
            console.log("🔄 [Zustand] Access Token이 없습니다. 갱신을 시도합니다...");
            refreshAccessToken();
        }
    }, [isLoggedIn, accessToken, refreshAccessToken]);

    useEffect(() => {
        // Access Token 자동 갱신 (선택적)
        // Access Token이 만료되기 전에 자동으로 갱신
        // 예: 5분마다 갱신 시도
        if (!isLoggedIn) return;

        const interval = setInterval(
            () => {
                console.log("🔄 [Zustand] Access Token 자동 갱신 시도...");
                refreshAccessToken();
            },
            5 * 60 * 1000 // 5분
        );

        return () => clearInterval(interval);
    }, [isLoggedIn, refreshAccessToken]);

    return <>{children}</>;
}

