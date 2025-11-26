// 인증 관련 유틸리티 함수

export const API_GATEWAY_URL = "http://localhost:8080";

export type AuthProvider = "kakao" | "naver" | "google";

export interface AuthResponse {
    success?: boolean;
    token?: string;
    loginUrl?: string;
    user?: {
        id?: string;
        email?: string;
        nickname?: string;
    };
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
        return `Gateway API 엔드포인트를 찾을 수 없습니다.\nGateway에 POST ${endpoint} 엔드포인트가 있는지 확인해주세요.`;
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
    user?: { id?: string; email?: string; nickname?: string }
): void {
    localStorage.setItem("access_token", token);
    localStorage.setItem("login_provider", provider);

    if (user && Object.keys(user).length > 0) {
        localStorage.setItem("user_info", JSON.stringify(user));
    }
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
            : `/api/auth/${provider}`;

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
    window.location.href = loginUrl;
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
        throw new Error(data.message || "로그인에 실패했습니다.");
    }
}

