// 인증 관련 유틸리티 함수

import { API_GATEWAY_URL, STORAGE_KEYS, ERROR_MESSAGES } from "@/app/constants/auth";

export type AuthProvider = "kakao" | "naver" | "google";

export interface UserInfo {
    id?: string;
    email?: string;
    nickname?: string;
}

export interface AuthResponse {
    success?: boolean;
    token?: string;
    loginUrl?: string;
    user?: UserInfo;
    message?: string;
}

export interface AuthError {
    message: string;
    error?: string;
}

/**
 * 에러 응답을 파싱하여 에러 메시지를 추출
 */
export async function parseErrorResponse(
    response: Response,
    endpoint: string
): Promise<string> {
    if (response.status === 404) {
        return `${ERROR_MESSAGES.ENDPOINT_NOT_FOUND}\nGateway에 POST ${endpoint} 엔드포인트가 있는지 확인해주세요.`;
    }

    let errorMessage = `HTTP error! status: ${response.status}`;
    try {
        const errorText = await response.text();
        console.error("🔴 에러 응답 본문:", errorText);

        try {
            const errorData: AuthError = JSON.parse(errorText);
            errorMessage = errorData.message || errorData.error || errorText;
            console.error("🔴 에러 데이터:", errorData);
        } catch {
            errorMessage = errorText || errorMessage;
        }
    } catch (e) {
        console.error("🔴 에러 응답 읽기 실패:", e);
    }

    return errorMessage;
}

/**
 * 로컬스토리지에 인증 정보 저장
 */
export function saveAuthData(
    token: string,
    provider: AuthProvider,
    user?: UserInfo
): void {
    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, token);
    localStorage.setItem(STORAGE_KEYS.LOGIN_PROVIDER, provider);

    if (user && Object.keys(user).length > 0) {
        localStorage.setItem(STORAGE_KEYS.USER_INFO, JSON.stringify(user));
    }
}

/**
 * 로컬스토리지에서 사용자 정보 가져오기
 */
export function getUserInfo(): UserInfo | null {
    try {
        const userInfo = localStorage.getItem(STORAGE_KEYS.USER_INFO);
        return userInfo ? JSON.parse(userInfo) : null;
    } catch (e) {
        console.error("사용자 정보 파싱 에러:", e);
        return null;
    }
}

/**
 * 로컬스토리지에서 로그인 제공자 가져오기
 */
export function getLoginProvider(): AuthProvider | null {
    return localStorage.getItem(STORAGE_KEYS.LOGIN_PROVIDER) as AuthProvider | null;
}

/**
 * 로컬스토리지에서 액세스 토큰 가져오기
 */
export function getAccessToken(): string | null {
    return localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
}

/**
 * 로컬스토리지에서 모든 인증 정보 삭제
 */
export function clearAuthData(): void {
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.USER_INFO);
    localStorage.removeItem(STORAGE_KEYS.LOGIN_PROVIDER);
    localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
}

/**
 * 소셜 로그인 API 호출
 */
export async function requestSocialLogin(
    provider: AuthProvider
): Promise<AuthResponse> {
    const endpoint =
        provider === "kakao"
            ? "/api/auth/kakao/login"
            : `/api/auth/${provider}/login`;

    const response = await fetch(`${API_GATEWAY_URL}${endpoint}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({}),
    });

    if (!response.ok) {
        const errorMessage = await parseErrorResponse(response, endpoint);
        throw new Error(errorMessage);
    }

    const data: AuthResponse = await response.json();
    console.log(`Gateway 응답 (${provider}):`, data);

    return data;
}

/**
 * 로그인 URL로 리다이렉트
 */
export function redirectToLoginUrl(loginUrl: string, provider: AuthProvider): void {
    console.log(`${provider} 로그인 URL로 리다이렉트:`, loginUrl);
    // window.location.href 대신 window.location.replace 사용 (뒤로가기 방지)
    window.location.replace(loginUrl);
}

/**
 * 토큰을 받아서 저장하고 대시보드로 이동
 */
export function handleTokenResponse(
    data: AuthResponse,
    provider: AuthProvider,
    router: { push: (path: string) => void }
): void {
    if (data.success === true && data.token) {
        saveAuthData(data.token, provider, data.user);
        console.log(`${provider} 로그인 성공:`, data);
        router.push("/dashboard");
    } else {
        throw new Error(data.message || ERROR_MESSAGES.LOGIN_FAILED);
    }
}

