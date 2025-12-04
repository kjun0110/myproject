"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getUserInfo, getLoginProvider, clearAuthData, type UserInfo } from "@/app/lib/auth";
import { type AuthProvider } from "@/app/lib/auth";
import { PROVIDER_NAMES } from "@/app/constants/auth";

export default function Dashboard() {
    const router = useRouter();
    const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
    const [loginProvider, setLoginProvider] = useState<AuthProvider | null>(null);

    useEffect(() => {
        const storedUserInfo = getUserInfo();
        const provider = getLoginProvider();

        setUserInfo(storedUserInfo);
        setLoginProvider(provider);
    }, []);

    const handleLogout = () => {
        clearAuthData();
        router.push("/");
    };

    const getProviderName = (provider: AuthProvider | null): string => {
        return provider ? PROVIDER_NAMES[provider] : "소셜";
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
                        onClick={() => router.push("/dashboard/titanic")}
                        className="flex h-12 w-full max-w-xs items-center justify-center gap-3 rounded-lg bg-blue-600 px-6 text-base font-medium text-white transition-colors hover:bg-blue-700 dark:bg-blue-600 dark:hover:bg-blue-700"
                    >
                        타이타닉
                    </button>
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

