import { create } from "zustand";
import type { OAuthProvider, UserInfo } from "@/types";

interface AuthState {
    // Access Token은 메모리에만 저장 (5-15분 짧은 수명)
    accessToken: string | null;

    // Refresh Token은 HttpOnly 쿠키에 저장 (클라이언트에서 읽을 수 없으므로 메모리에 저장하지 않음)
    // 주의: refreshToken 필드는 하위 호환성을 위해 유지하지만 항상 null입니다.
    refreshToken: string | null;

    // 사용자 정보
    userInfo: UserInfo | null;

    // 로그인 제공자
    loginProvider: OAuthProvider | null;

    // 로그인 여부 (User Info 또는 Login Provider 존재 여부로 판단)
    isLoggedIn: boolean;

    // Actions
    setAccessToken: (token: string | null) => void;
    setUserInfo: (userInfo: UserInfo | null) => void;
    setLoginProvider: (provider: OAuthProvider | null) => void;

    // 로그인 처리 (모든 정보를 한 번에 설정)
    login: (
        accessToken: string,
        refreshToken: string | null, // HttpOnly 쿠키에 저장되므로 여기서는 무시됨
        provider: OAuthProvider,
        userInfo?: UserInfo
    ) => void;

    // 로그아웃 처리 (모든 정보 초기화)
    logout: () => void;

    // Refresh Token으로 Access Token 갱신
    // 주의: HttpOnly 쿠키에서 refreshToken을 읽어야 하므로 API Route를 통해 처리해야 함
    refreshAccessToken: () => Promise<boolean>;
}

// localStorage에서 User Info 가져오기
const getUserInfoFromStorage = (): UserInfo | null => {
    if (typeof window === "undefined") return null;
    try {
        const userInfo = localStorage.getItem("user_info");
        return userInfo ? JSON.parse(userInfo) : null;
    } catch {
        return null;
    }
};

// localStorage에 User Info 저장
const saveUserInfoToStorage = (userInfo: UserInfo | null): void => {
    if (typeof window === "undefined") return;
    if (userInfo && Object.keys(userInfo).length > 0) {
        localStorage.setItem("user_info", JSON.stringify(userInfo));
    } else {
        localStorage.removeItem("user_info");
    }
};

// localStorage에서 Login Provider 가져오기
const getLoginProviderFromStorage = (): OAuthProvider | null => {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("login_provider") as OAuthProvider | null;
};

// localStorage에 Login Provider 저장
const saveLoginProviderToStorage = (provider: OAuthProvider | null): void => {
    if (typeof window === "undefined") return;
    if (provider) {
        localStorage.setItem("login_provider", provider);
    } else {
        localStorage.removeItem("login_provider");
    }
};

export const useAuthStore = create<AuthState>((set, get) => ({
    // 초기 상태: Access Token은 null (메모리에만 존재)
    accessToken: null,

    // Refresh Token은 HttpOnly 쿠키에 저장되므로 클라이언트에서 읽을 수 없음
    // 하위 호환성을 위해 필드는 유지하지만 항상 null
    refreshToken: null,

    // User Info는 localStorage에서 복원
    userInfo: getUserInfoFromStorage(),

    // Login Provider는 localStorage에서 복원
    loginProvider: getLoginProviderFromStorage(),

    // 로그인 여부는 User Info 또는 Login Provider 존재 여부로 판단
    // (Refresh Token은 HttpOnly 쿠키에 있어서 클라이언트에서 확인 불가)
    isLoggedIn: !!(getUserInfoFromStorage() || getLoginProviderFromStorage()),

    // Access Token 설정 (메모리에만 저장)
    setAccessToken: (token) => {
        set({ accessToken: token });
    },

    // User Info 설정 (localStorage에 저장)
    setUserInfo: (userInfo) => {
        saveUserInfoToStorage(userInfo);
        set({ userInfo });
    },

    // Login Provider 설정 (localStorage에 저장)
    setLoginProvider: (provider) => {
        saveLoginProviderToStorage(provider);
        set({ loginProvider: provider });
    },

    // 로그인 처리
    login: (accessToken, refreshToken, provider, userInfo) => {
        // Access Token은 메모리에만 저장
        set({ accessToken });

        // Refresh Token은 HttpOnly 쿠키에 저장되므로 여기서는 처리하지 않음
        // (successService.ts에서 별도로 처리)
        // 하위 호환성을 위해 refreshToken 필드는 null로 유지
        set({ refreshToken: null });

        // User Info 저장
        if (userInfo) {
            saveUserInfoToStorage(userInfo);
            set({ userInfo });
        }

        // Login Provider 저장
        saveLoginProviderToStorage(provider);
        set({ loginProvider: provider, isLoggedIn: true });

        console.log("✅ 로그인 완료 (Access Token은 메모리에만, Refresh Token은 HttpOnly 쿠키에 저장)");
    },

    // 로그아웃 처리
    logout: () => {
        // 메모리의 Access Token 삭제
        set({ accessToken: null });

        // localStorage의 모든 정보 삭제
        // Refresh Token은 HttpOnly 쿠키에 있으므로 dashboardService에서 별도로 삭제
        saveUserInfoToStorage(null);
        saveLoginProviderToStorage(null);

        set({
            refreshToken: null,
            userInfo: null,
            loginProvider: null,
            isLoggedIn: false,
        });

        console.log("✅ 로그아웃 완료 (localStorage 정리 완료, HttpOnly 쿠키는 dashboardService에서 삭제)");
    },

    // Refresh Token으로 Access Token 갱신
    // 주의: Refresh Token은 HttpOnly 쿠키에 저장되어 있으므로,
    // API Route를 통해 서버에서 쿠키를 읽어서 갱신해야 함
    refreshAccessToken: async () => {
        try {
            // TODO: API Route를 통해 HttpOnly 쿠키에서 refreshToken을 읽어서 Access Token 갱신
            // 예: const response = await fetch("/api/auth/refresh", { method: "POST" });
            // const data = await response.json();
            // set({ accessToken: data.accessToken });

            console.log("⚠️ Access Token 갱신 기능은 아직 구현되지 않았습니다.");
            console.log("⚠️ HttpOnly 쿠키에서 refreshToken을 읽어서 갱신해야 합니다.");
            return false;
        } catch (error) {
            console.error("❌ Access Token 갱신 실패:", error);

            // 갱신 실패 시 로그아웃 처리
            get().logout();
            return false;
        }
    },
}));

// ============================================
// 무상태 인터페이스 (Stateless Interface)
// React 컴포넌트 외부에서도 사용 가능한 순수 함수들
// ============================================

/**
 * 로그인 처리 (무상태 함수)
 */
export const authLogin = (
    accessToken: string,
    refreshToken: string | null,
    provider: OAuthProvider,
    userInfo?: UserInfo
): void => {
    useAuthStore.getState().login(accessToken, refreshToken, provider, userInfo);
};

/**
 * 로그아웃 처리 (무상태 함수)
 */
export const authLogout = (): void => {
    useAuthStore.getState().logout();
};

/**
 * Access Token 가져오기 (무상태 함수)
 */
export const getAccessToken = (): string | null => {
    return useAuthStore.getState().accessToken;
};

/**
 * Refresh Token 가져오기 (무상태 함수)
 * 주의: Refresh Token은 HttpOnly 쿠키에 저장되어 있어서 클라이언트에서 읽을 수 없습니다.
 * 항상 null을 반환합니다. 실제 refreshToken은 서버에서만 접근 가능합니다.
 */
export const getRefreshToken = (): string | null => {
    // HttpOnly 쿠키는 클라이언트에서 읽을 수 없으므로 항상 null 반환
    return null;
};

/**
 * 사용자 정보 가져오기 (무상태 함수)
 */
export const getUserInfo = (): UserInfo | null => {
    return useAuthStore.getState().userInfo;
};

/**
 * 로그인 제공자 가져오기 (무상태 함수)
 */
export const getLoginProvider = (): OAuthProvider | null => {
    return useAuthStore.getState().loginProvider;
};

/**
 * 로그인 여부 확인 (무상태 함수)
 */
export const isLoggedIn = (): boolean => {
    return useAuthStore.getState().isLoggedIn;
};

/**
 * Access Token 갱신 (무상태 함수)
 */
export const refreshAccessToken = async (): Promise<boolean> => {
    return await useAuthStore.getState().refreshAccessToken();
};

/**
 * Access Token 설정 (무상태 함수)
 */
export const setAccessToken = (token: string | null): void => {
    useAuthStore.getState().setAccessToken(token);
};

/**
 * Refresh Token 설정 (무상태 함수)
 * 주의: Refresh Token은 HttpOnly 쿠키에 저장되므로 이 함수는 사용하지 않습니다.
 * 대신 services/oauth/[provider]/success/successService.ts의 setRefreshTokenCookie()를 사용하세요.
 * @deprecated HttpOnly 쿠키 사용으로 인해 더 이상 사용하지 않음
 */
export const setRefreshToken = (token: string | null): void => {
    // HttpOnly 쿠키에 저장되므로 여기서는 아무 작업도 하지 않음
    console.warn("⚠️ setRefreshToken은 더 이상 사용하지 않습니다. HttpOnly 쿠키를 사용하세요.");
};

/**
 * 사용자 정보 설정 (무상태 함수)
 */
export const setUserInfo = (userInfo: UserInfo | null): void => {
    useAuthStore.getState().setUserInfo(userInfo);
};

/**
 * 로그인 제공자 설정 (무상태 함수)
 */
export const setLoginProvider = (provider: OAuthProvider | null): void => {
    useAuthStore.getState().setLoginProvider(provider);
};

