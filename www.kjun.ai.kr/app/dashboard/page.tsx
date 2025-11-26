"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function Dashboard() {
    const router = useRouter();
    const [userInfo, setUserInfo] = useState<any>(null);
    const [loginProvider, setLoginProvider] = useState<string | null>(null);

    useEffect(() => {
        // localStorage에서 사용자 정보 가져오기
        const storedUserInfo = localStorage.getItem("user_info");
        if (storedUserInfo) {
            try {
                setUserInfo(JSON.parse(storedUserInfo));
            } catch (e) {
                console.error("사용자 정보 파싱 에러:", e);
            }
        }

        // 로그인 제공자 정보 가져오기
        const provider = localStorage.getItem("login_provider");
        setLoginProvider(provider);
    }, []);

    const handleLogout = () => {
        // 토큰 및 사용자 정보 삭제
        localStorage.removeItem("access_token");
        localStorage.removeItem("user_info");
        localStorage.removeItem("login_provider");

        // 홈으로 이동
        router.push("/");
    };

    const getProviderName = (provider: string | null) => {
        switch (provider) {
            case "kakao":
                return "카카오";
            case "naver":
                return "네이버";
            case "google":
                return "구글";
            default:
                return "소셜";
        }
    };

    return (
        <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
            <main className="flex w-full max-w-md flex-col items-center gap-8 py-16 px-6">
                <div className="flex w-full flex-col items-center gap-6 text-center">
                    <h1 className="text-4xl font-bold text-black dark:text-zinc-50">
                        로그인이 성공했습니다
                    </h1>
                    {loginProvider && (
                        <p className="text-xl font-semibold text-zinc-600 dark:text-zinc-400">
                            {getProviderName(loginProvider)} 사용자
                        </p>
                    )}
                    {userInfo && (
                        <div className="w-full rounded-lg bg-zinc-100 dark:bg-zinc-800 p-4 text-left">
                            <p className="text-sm font-medium text-zinc-600 dark:text-zinc-400 mb-2">
                                사용자 정보:
                            </p>
                            {userInfo.id && (
                                <p className="text-sm text-zinc-800 dark:text-zinc-200">
                                    ID: {userInfo.id}
                                </p>
                            )}
                            {userInfo.email && (
                                <p className="text-sm text-zinc-800 dark:text-zinc-200">
                                    이메일: {userInfo.email}
                                </p>
                            )}
                            {userInfo.nickname && (
                                <p className="text-sm text-zinc-800 dark:text-zinc-200">
                                    닉네임: {userInfo.nickname}
                                </p>
                            )}
                        </div>
                    )}
                    <button
                        onClick={handleLogout}
                        className="flex h-12 w-full max-w-xs items-center justify-center gap-3 rounded-lg bg-[#03C75A] px-6 text-base font-medium text-white transition-colors hover:bg-[#02B350] dark:bg-[#03C75A] dark:hover:bg-[#02B350]"
                    >
                        로그아웃
                    </button>
                </div>
            </main>
        </div>
    );
}

