/**
 * 인증 관련 타입 정의
 */

export type OAuthProvider = "kakao" | "naver" | "google";

export interface UserInfo {
    id?: string;
    email?: string;
    nickname?: string;
}

export interface OAuthResponse {
    success?: boolean;
    token?: string;
    refreshToken?: string;
    loginUrl?: string;
    user?: UserInfo;
    message?: string;
}

export interface OAuthError {
    message: string;
    error?: string;
}

export interface AuthState {
    accessToken: string | null;
    refreshToken: string | null;
    userInfo: UserInfo | null;
    loginProvider: OAuthProvider | null;
    isLoggedIn: boolean;
}

