"use client";

import { useSearchParams, useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { ERROR_MESSAGES } from "@/constants/oauth";
import { OAuthStatusPage } from "@/components/OAuthStatusPage";
import type { OAuthProvider } from "@/types";

/**
 * 동적 라우팅 경로: app/oauth/[provider]/error/page.tsx
 * 
 * 백엔드에서 리다이렉트하는 경로: /oauth/{provider}/error
 * - /oauth/google/error
 * - /oauth/kakao/error
 * - /oauth/naver/error
 */
export default function OAuthError() {
    const searchParams = useSearchParams();
    const params = useParams();

    const [error, setError] = useState<string | null>(ERROR_MESSAGES.LOGIN_FAILED);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        const provider = params.provider as OAuthProvider;
        const errorMessage = searchParams.get("error");

        if (errorMessage) {
            // URL 디코딩
            const decodedError = decodeURIComponent(errorMessage);
            console.error(`❌ [${provider} 로그인 오류]`, decodedError);

            // 사용자 친화적인 오류 메시지로 변환
            let userFriendlyError: string = ERROR_MESSAGES.LOGIN_FAILED;

            if (decodedError.includes("duplicate key")) {
                userFriendlyError = "이미 로그인된 계정입니다. 잠시 후 다시 시도해주세요.";
            } else if (decodedError.includes("could not execute statement")) {
                userFriendlyError = "데이터베이스 오류가 발생했습니다. 잠시 후 다시 시도해주세요.";
            } else if (decodedError.includes("timeout") || decodedError.includes("connection")) {
                userFriendlyError = "서버 연결 오류가 발생했습니다. 잠시 후 다시 시도해주세요.";
            }

            setError(userFriendlyError);
        }
    }, [params.provider, searchParams]);

    return <OAuthStatusPage isLoading={isLoading} error={error} />;
}

