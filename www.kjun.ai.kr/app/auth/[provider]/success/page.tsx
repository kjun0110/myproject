"use client";

import { useRouter, useSearchParams, useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { type AuthProvider } from "@/app/lib/auth";
import { saveAuthData, type UserInfo } from "@/app/lib/auth";
import { ERROR_MESSAGES } from "@/app/constants/auth";
import { AuthStatusPage } from "@/app/components/AuthStatusPage";

/**
 * 동적 라우팅 경로: app/auth/[provider]/success/page.tsx
 * 
 * Next.js 동적 라우팅:
 * - 파일 경로의 [provider]가 URL의 provider 값을 캡처
 * - 예: /auth/google/success → [provider] = "google"
 * - 예: /auth/kakao/success → [provider] = "kakao"
 * - 예: /auth/naver/success → [provider] = "naver"
 */
export default function AuthSuccess() {
    const router = useRouter();
    const searchParams = useSearchParams();

    // 동적 라우팅 파라미터 추출: useParams()로 [provider] 값 가져오기
    // URL: /auth/google/success → params = { provider: "google" }
    // URL: /auth/kakao/success → params = { provider: "kakao" }
    const params = useParams();

    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // 동적 라우팅에서 추출한 provider 값을 AuthProvider 타입으로 변환
        // params.provider는 Next.js가 URL에서 자동으로 추출한 값
        // 예: /auth/google/success → params.provider = "google"
        const provider = params.provider as AuthProvider;
        const token = searchParams.get("token");
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

                // 인증 정보 저장
                saveAuthData(token, provider, userInfo);

                console.log(`${provider} 로그인 성공, 토큰 저장 완료`, {
                    token: token.substring(0, 20) + "...",
                    userInfo,
                });

                setIsLoading(false);

                // 대시보드로 이동
                router.push("/dashboard");
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

    return <AuthStatusPage isLoading={isLoading} error={error} />;
}

