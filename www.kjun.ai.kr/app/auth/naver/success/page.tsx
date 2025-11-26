"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

export default function NaverAuthSuccess() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // URL에서 파라미터 가져오기
        const token = searchParams.get("token");
        const id = searchParams.get("id");
        const email = searchParams.get("email");
        const nickname = searchParams.get("nickname");

        if (token) {
            try {
                // 토큰을 localStorage에 저장
                localStorage.setItem("access_token", token);

                // 사용자 정보 객체 생성
                const userInfo: any = {};
                if (id) userInfo.id = id;
                if (email) userInfo.email = email;
                if (nickname) userInfo.nickname = nickname;

                // 사용자 정보가 있으면 localStorage에 저장
                if (Object.keys(userInfo).length > 0) {
                    localStorage.setItem("user_info", JSON.stringify(userInfo));
                }

                // 로그인 제공자 정보 저장
                localStorage.setItem("login_provider", "naver");

                console.log("네이버 로그인 성공, 토큰 저장 완료", {
                    token: token.substring(0, 20) + "...",
                    userInfo,
                });

                setIsLoading(false);

                // 대시보드로 이동
                router.push("/dashboard");
            } catch (err) {
                console.error("토큰 저장 에러:", err);
                setError("토큰 저장에 실패했습니다.");
                setIsLoading(false);
            }
        } else {
            // 토큰이 없으면 에러
            setError("토큰을 받지 못했습니다.");
            console.error("토큰이 없습니다.");
            setIsLoading(false);
        }
    }, [searchParams, router]);

    if (isLoading) {
        // 로딩 중
        return (
            <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
                <main className="flex w-full max-w-md flex-col items-center gap-8 py-16 px-6">
                    <div className="flex w-full flex-col items-center gap-6 text-center">
                        <h1 className="text-4xl font-bold text-black dark:text-zinc-50">
                            로그인 처리 중...
                        </h1>
                        <p className="text-lg text-zinc-600 dark:text-zinc-400">
                            잠시만 기다려주세요.
                        </p>
                    </div>
                </main>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
                <main className="flex w-full max-w-md flex-col items-center gap-8 py-16 px-6">
                    <div className="flex w-full flex-col items-center gap-6 text-center">
                        <h1 className="text-4xl font-bold text-red-600 dark:text-red-400">
                            로그인 실패
                        </h1>
                        <p className="text-lg text-zinc-600 dark:text-zinc-400">
                            {error}
                        </p>
                        <button
                            onClick={() => router.push("/")}
                            className="flex h-12 w-full max-w-xs items-center justify-center gap-3 rounded-lg bg-[#03C75A] px-6 text-base font-medium text-white transition-colors hover:bg-[#02B350]"
                        >
                            홈으로 돌아가기
                        </button>
                    </div>
                </main>
            </div>
        );
    }

    return null;
}

