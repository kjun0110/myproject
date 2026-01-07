/**
 * 인증 상태 관리 Hook (대시보드 페이지용)
 * Zustand 스토어를 React Hook으로 감싸서 사용
 */

"use client";

import { useAuthStore } from "@/store/auth.store";
import { handleLogout } from "@/services/dashboard/dashboardService";
import type { OAuthProvider, UserInfo } from "@/store/auth.index";

/**
 * 인증 상태 관리 Hook
 */
export function useAuth() {
    // Zustand 스토어에서 상태 구독
    const accessToken = useAuthStore((state) => state.accessToken);
    const userInfo = useAuthStore((state) => state.userInfo);
    const loginProvider = useAuthStore((state) => state.loginProvider);
    const isLoggedIn = useAuthStore((state) => state.isLoggedIn);

    return {
        // 상태
        accessToken,
        // 주의: refreshToken은 HttpOnly 쿠키에 저장되어 클라이언트에서 읽을 수 없으므로 제거됨
        userInfo,
        loginProvider,
        isLoggedIn,

        // 액션 (무상태 함수)
        logout: handleLogout,
    };
}

/**
 * 로그인 여부만 확인하는 경량 Hook
 */
export function useIsLoggedIn(): boolean {
    return useAuthStore((state) => state.isLoggedIn);
}

/**
 * 사용자 정보만 가져오는 Hook
 */
export function useUserInfo(): UserInfo | null {
    return useAuthStore((state) => state.userInfo);
}

/**
 * Access Token만 가져오는 Hook
 */
export function useAccessToken(): string | null {
    return useAuthStore((state) => state.accessToken);
}

