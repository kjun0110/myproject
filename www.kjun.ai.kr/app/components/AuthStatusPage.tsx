"use client";

import { useRouter } from "next/navigation";

interface AuthStatusPageProps {
    isLoading: boolean;
    error: string | null;
    onGoHome?: () => void;
}

export function AuthStatusPage({ isLoading, error, onGoHome }: AuthStatusPageProps) {
    const router = useRouter();
    const handleGoHome = onGoHome || (() => router.push("/"));

    if (isLoading) {
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
                            onClick={handleGoHome}
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

