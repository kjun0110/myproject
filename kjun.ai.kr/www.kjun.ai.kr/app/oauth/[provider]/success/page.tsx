"use client";

import { useRouter, useSearchParams, useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { saveOAuthData } from "@/services/oauth/[provider]/success/successService";
import { ERROR_MESSAGES } from "@/constants/oauth";
import { OAuthStatusPage } from "@/components/OAuthStatusPage";
import type { OAuthProvider, UserInfo } from "@/store/auth.index";

/**
 * 동적 라우팅 경로: app/oauth/[provider]/success/page.tsx
 * 
 * 백엔드에서 리다이렉트하는 경로: /oauth/{provider}/success
 * - /oauth/google/success
 * - /oauth/kakao/success
 * - /oauth/naver/success
 */
export default function OAuthSuccess() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const params = useParams();

    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // 동적 라우팅에서 추출한 provider 값을 OAuthProvider 타입으로 변환
        const provider = params.provider as OAuthProvider;
        const token = searchParams.get("token");
        const refreshToken = searchParams.get("refreshToken");
        const id = searchParams.get("id");
        const email = searchParams.get("email");
        const nickname = searchParams.get("nickname");

        // async 함수를 내부에서 정의하고 호출
        const handleOAuthSuccess = async () => {
            if (token) {
                try {
                    // 사용자 정보 객체 생성
                    const userInfo: UserInfo = {};
                    if (id) userInfo.id = id;
                    if (email) userInfo.email = email;
                    if (nickname) userInfo.nickname = nickname;

                    // OAuth 정보 저장 (Access Token은 메모리, Refresh Token은 HttpOnly 쿠키)
                    await saveOAuthData(token, provider, refreshToken, userInfo);

                    console.log(`${provider} 로그인 성공, 토큰 저장 완료 (Access Token은 메모리에만, Refresh Token은 HttpOnly 쿠키에)`, {
                        token: token.substring(0, 20) + "...",
                        refreshToken: refreshToken ? refreshToken.substring(0, 20) + "..." : null,
                        userInfo,
                    });

                    setIsLoading(false);

                    // 메인 페이지로 이동
                    router.push("/");
                } catch (err) {
                    console.error("토큰 저장 에러:", err);
                    setError(ERROR_MESSAGES.TOKEN_SAVE_FAILED);
                    setIsLoading(false);
                }
            } else {
                setError(ERROR_MESSAGES.TOKEN_NOT_RECEIVED);
                console.error("토큰이 없습니다.");
                setIsLoading(false);
            }
        };

        handleOAuthSuccess();
    }, [searchParams, router, params]);

    return <OAuthStatusPage isLoading={isLoading} error={error} />;
}

