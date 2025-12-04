import React from "react";
import { type AuthProvider, requestSocialLogin, redirectToLoginUrl, handleTokenResponse } from "@/app/lib/auth";
import { ERROR_MESSAGES } from "@/app/constants/auth";

// 핸들러 반환 타입
export interface SocialLoginHandlers {
    handleSocialLogin: (provider: AuthProvider) => Promise<void>;
    handleKakaoLogin: () => void;
    handleNaverLogin: () => void;
    handleGoogleLogin: () => void;
}

// 클로저를 활용한 핸들러 생성 함수 (순수 함수)
export function createSocialLoginHandlers(
    router: { push: (path: string) => void },
    setLoading: React.Dispatch<React.SetStateAction<Record<AuthProvider, boolean>>>,
    setError: React.Dispatch<React.SetStateAction<string | null>>
): SocialLoginHandlers {
    // IIFE를 사용하여 클로저 환경 생성
    return (() => {
        // 일반 함수: 메인 소셜 로그인 핸들러 (클로저로 외부 스코프 접근)
        async function handleSocialLogin(provider: AuthProvider): Promise<void> {
            setLoading((prev) => ({ ...prev, [provider]: true }));
            setError(null);

            try {
                const data = await requestSocialLogin(provider);

                // 옵션 1: 로그인 URL을 반환하는 경우
                if (data.loginUrl) {
                    setLoading((prev) => ({ ...prev, [provider]: false }));
                    redirectToLoginUrl(data.loginUrl, provider);
                    return;
                }

                // 옵션 2: 토큰을 직접 반환하는 경우 (테스트용)
                handleTokenResponse(data, provider, router);
                setLoading((prev) => ({ ...prev, [provider]: false }));
            } catch (err) {
                console.error(`${provider} 로그인 에러:`, err);
                setError(
                    err instanceof Error
                        ? err.message
                        : ERROR_MESSAGES.SERVER_CONNECTION_FAILED
                );
            } finally {
                setLoading((prev) => ({ ...prev, [provider]: false }));
            }
        }

        // 일반 함수: 카카오 로그인 핸들러
        function handleKakaoLogin(): void {
            handleSocialLogin("kakao");
        }

        // 일반 함수: 네이버 로그인 핸들러
        function handleNaverLogin(): void {
            handleSocialLogin("naver");
        }

        // 일반 함수: 구글 로그인 핸들러
        function handleGoogleLogin(): void {
            handleSocialLogin("google");
        }

        // 클로저로 생성된 핸들러들 반환
        return {
            handleSocialLogin,
            handleKakaoLogin,
            handleNaverLogin,
            handleGoogleLogin,
        };
    })();
}

