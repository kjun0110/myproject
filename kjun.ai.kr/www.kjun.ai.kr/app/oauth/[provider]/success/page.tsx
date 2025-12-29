"use client";

import { useRouter, useSearchParams, useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { type OAuthProvider } from "@/lib/oauth";
import { saveOAuthData, type UserInfo } from "@/lib/oauth";
import { ERROR_MESSAGES } from "@/constants/oauth";
import { OAuthStatusPage } from "@/components/OAuthStatusPage";

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

        if (token) {
            try {
                // 사용자 정보 객체 생성
                const userInfo: UserInfo = {};
                if (id) userInfo.id = id;
                if (email) userInfo.email = email;
                if (nickname) userInfo.nickname = nickname;

                // OAuth 정보 저장
                saveOAuthData(token, provider, userInfo);
                
                // Refresh Token 저장 (있는 경우)
                if (refreshToken) {
                    localStorage.setItem("refresh_token", refreshToken);
                }

                console.log(`${provider} 로그인 성공, 토큰 저장 완료`, {
                    token: token.substring(0, 20) + "...",
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
    }, [searchParams, router, params]);

    return <OAuthStatusPage isLoading={isLoading} error={error} />;
}

