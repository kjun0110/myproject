import { create } from "zustand";

// ============================================
// Types (Ducks Pattern)
// ============================================

/**
 * OAuth Provider 타입
 */
export type OAuthProvider = "kakao" | "naver" | "google";

/**
 * 사용자 정보 타입
 */
export interface UserInfo {
    id?: string;
    email?: string;
    nickname?: string;
}

/**
 * OAuth 응답 타입
 */
export interface OAuthResponse {
    success?: boolean;
    token?: string;
    refreshToken?: string;
    loginUrl?: string;
    user?: UserInfo;
    message?: string;
}

/**
 * OAuth 에러 타입
 */
export interface OAuthError {
    message: string;
    error?: string;
}

/**
 * Auth Store State
 * - accessToken: 메모리에만 저장 (5-15분 짧은 수명)
 * - refreshToken: HttpOnly 쿠키에 저장 (클라이언트에서 접근 불가)
 */
interface AuthState {
    // Access Token은 메모리에만 저장
    accessToken: string | null;

    // 사용자 정보 (localStorage에 저장)
    userInfo: UserInfo | null;

    // 로그인 제공자 (localStorage에 저장)
    loginProvider: OAuthProvider | null;

    // 로그인 여부
    isLoggedIn: boolean;
}

/**
 * Auth Store Actions (Ducks Pattern)
 */
interface AuthActions {
    // Access Token 관리
    setAccessToken: (token: string | null) => void;
    
    // User Info 관리
    setUserInfo: (userInfo: UserInfo | null) => void;
    
    // Login Provider 관리
    setLoginProvider: (provider: OAuthProvider | null) => void;

    // 로그인 처리 (accessToken만 받음, refreshToken은 HttpOnly 쿠키에 저장)
    login: (
        accessToken: string,
        provider: OAuthProvider,
        userInfo?: UserInfo
    ) => void;

    // 로그아웃 처리
    logout: () => void;

    // Access Token 갱신 (HttpOnly 쿠키의 refreshToken 사용)
    refreshAccessToken: () => Promise<boolean>;
}

/**
 * Combined Store Type
 */
type AuthStore = AuthState & AuthActions;

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

// ============================================
// Store Implementation (Ducks Pattern)
// ============================================

/**
 * Auth Store
 * - Zustand를 사용한 상태 관리
 * - accessToken만 메모리에 저장
 * - refreshToken은 HttpOnly 쿠키에 저장 (클라이언트 접근 불가)
 */
export const useAuthStore = create<AuthStore>((set, get) => ({
    // ============================================
    // State (초기값)
    // ============================================
    
    // Access Token은 메모리에만 저장 (새로고침 시 초기화됨)
    accessToken: null,

    // User Info는 localStorage에서 복원
    userInfo: getUserInfoFromStorage(),

    // Login Provider는 localStorage에서 복원
    loginProvider: getLoginProviderFromStorage(),

    // 로그인 여부는 User Info 또는 Login Provider 존재 여부로 판단
    isLoggedIn: !!(getUserInfoFromStorage() || getLoginProviderFromStorage()),

    // ============================================
    // Actions
    // ============================================

    /**
     * Access Token 설정 (메모리에만 저장)
     */
    setAccessToken: (token) => {
        set({ accessToken: token });
    },

    /**
     * User Info 설정 (localStorage에 저장)
     */
    setUserInfo: (userInfo) => {
        saveUserInfoToStorage(userInfo);
        set({ 
            userInfo,
            isLoggedIn: !!(userInfo || get().loginProvider)
        });
    },

    /**
     * Login Provider 설정 (localStorage에 저장)
     */
    setLoginProvider: (provider) => {
        saveLoginProviderToStorage(provider);
        set({ 
            loginProvider: provider,
            isLoggedIn: !!(provider || get().userInfo)
        });
    },

    /**
     * 로그인 처리
     * @param accessToken - Access Token (메모리에만 저장)
     * @param provider - OAuth Provider
     * @param userInfo - 사용자 정보 (선택)
     * 
     * 참고: refreshToken은 HttpOnly 쿠키에 저장되므로 파라미터에서 제거됨
     */
    login: (accessToken, provider, userInfo) => {
        // Access Token은 메모리에만 저장
        set({ accessToken });

        // User Info 저장 (있는 경우)
        if (userInfo) {
            saveUserInfoToStorage(userInfo);
            set({ userInfo });
        }

        // Login Provider 저장
        saveLoginProviderToStorage(provider);
        set({ 
            loginProvider: provider, 
            isLoggedIn: true 
        });

        console.log("✅ 로그인 완료");
        console.log("   - Access Token: 메모리에 저장");
        console.log("   - Refresh Token: HttpOnly 쿠키에 저장 (클라이언트 접근 불가)");
    },

    /**
     * 로그아웃 처리
     * - 메모리의 Access Token 삭제
     * - localStorage의 모든 정보 삭제
     * - HttpOnly 쿠키는 API Route에서 별도로 삭제 필요
     */
    logout: () => {
        // 메모리 초기화
        set({ accessToken: null });

        // localStorage 초기화
        saveUserInfoToStorage(null);
        saveLoginProviderToStorage(null);

        // 상태 초기화
        set({
            userInfo: null,
            loginProvider: null,
            isLoggedIn: false,
        });

        console.log("✅ 로그아웃 완료");
        console.log("   - 메모리 및 localStorage 정리 완료");
        console.log("   - HttpOnly 쿠키는 API Route에서 삭제 필요");
    },

    /**
     * Access Token 갱신
     * - HttpOnly 쿠키의 refreshToken을 사용하여 새로운 accessToken 발급
     * - API Route를 통해 서버에서 처리
     */
    refreshAccessToken: async () => {
        try {
            // API Route를 통해 HttpOnly 쿠키의 refreshToken으로 Access Token 갱신
            const response = await fetch("/api/auth/refresh", { 
                method: "POST",
                credentials: "include", // HttpOnly 쿠키 포함
            });

            if (!response.ok) {
                throw new Error("Access Token 갱신 실패");
            }

            const data = await response.json();
            
            // 새로운 Access Token 저장
            if (data.accessToken) {
                set({ accessToken: data.accessToken });
                console.log("✅ Access Token 갱신 성공");
                return true;
            }

            throw new Error("Access Token이 응답에 없습니다");
        } catch (error) {
            console.error("❌ Access Token 갱신 실패:", error);

            // 갱신 실패 시 로그아웃 처리
            get().logout();
            return false;
        }
    },
}));

// ============================================
// Selectors (Ducks Pattern)
// ============================================

/**
 * Access Token 선택자
 */
export const selectAccessToken = (state: AuthStore) => state.accessToken;

/**
 * User Info 선택자
 */
export const selectUserInfo = (state: AuthStore) => state.userInfo;

/**
 * Login Provider 선택자
 */
export const selectLoginProvider = (state: AuthStore) => state.loginProvider;

/**
 * 로그인 여부 선택자
 */
export const selectIsLoggedIn = (state: AuthStore) => state.isLoggedIn;

// ============================================
// Action Creators (Ducks Pattern)
// ============================================

/**
 * 로그인 액션
 */
export const authLogin = (
    accessToken: string,
    provider: OAuthProvider,
    userInfo?: UserInfo
): void => {
    useAuthStore.getState().login(accessToken, provider, userInfo);
};

/**
 * 로그아웃 액션
 */
export const authLogout = (): void => {
    useAuthStore.getState().logout();
};

/**
 * Access Token 갱신 액션
 */
export const authRefreshToken = async (): Promise<boolean> => {
    return await useAuthStore.getState().refreshAccessToken();
};

/**
 * Access Token 설정 액션
 */
export const authSetAccessToken = (token: string | null): void => {
    useAuthStore.getState().setAccessToken(token);
};

/**
 * User Info 설정 액션
 */
export const authSetUserInfo = (userInfo: UserInfo | null): void => {
    useAuthStore.getState().setUserInfo(userInfo);
};

/**
 * Login Provider 설정 액션
 */
export const authSetLoginProvider = (provider: OAuthProvider | null): void => {
    useAuthStore.getState().setLoginProvider(provider);
};

// ============================================
// Getters (컴포넌트 외부에서 사용)
// ============================================

/**
 * Access Token 가져오기
 */
export const getAccessToken = (): string | null => {
    return useAuthStore.getState().accessToken;
};

/**
 * User Info 가져오기
 */
export const getUserInfo = (): UserInfo | null => {
    return useAuthStore.getState().userInfo;
};

/**
 * Login Provider 가져오기
 */
export const getLoginProvider = (): OAuthProvider | null => {
    return useAuthStore.getState().loginProvider;
};

/**
 * 로그인 여부 확인
 */
export const getIsLoggedIn = (): boolean => {
    return useAuthStore.getState().isLoggedIn;
};

