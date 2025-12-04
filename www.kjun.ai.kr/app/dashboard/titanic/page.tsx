"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { API_GATEWAY_URL } from "@/app/constants/auth";

interface Passenger {
    rank: number;
    passengerId: number;
    name: string;
    survived: string;
    pclass: string;
    sex: string;
    age: number | null;
    fare: number;
    cabin: string | null;
}

export default function TitanicPage() {
    const router = useRouter();
    const [passengers, setPassengers] = useState<Passenger[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchTitanicData();
    }, []);

    const fetchTitanicData = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await fetch(`${API_GATEWAY_URL}/api/titanic/top10`);
            
            if (!response.ok) {
                throw new Error("데이터를 불러오는데 실패했습니다.");
            }
            
            const result = await response.json();
            if (result.success) {
                setPassengers(result.data);
            } else {
                throw new Error(result.error || "데이터를 불러오는데 실패했습니다.");
            }
        } catch (err) {
            console.error("Titanic 데이터 로드 오류:", err);
            if (err instanceof TypeError && err.message.includes("fetch")) {
                setError("서버에 연결할 수 없습니다. 서비스가 실행 중인지 확인해주세요.");
            } else {
                setError(err instanceof Error ? err.message : "알 수 없는 오류가 발생했습니다.");
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black py-8">
            <main className="flex w-full max-w-4xl flex-col gap-8 px-6">
                <div className="flex items-center justify-between">
                    <h1 className="text-4xl font-bold text-black dark:text-zinc-50">
                        타이타닉 - 요금 기준 상위 10명
                    </h1>
                    <button
                        onClick={() => router.push("/dashboard")}
                        className="px-4 py-2 rounded-lg bg-zinc-200 dark:bg-zinc-700 text-zinc-800 dark:text-zinc-200 hover:bg-zinc-300 dark:hover:bg-zinc-600 transition-colors"
                    >
                        뒤로가기
                    </button>
                </div>

                {loading && (
                    <div className="text-center py-8">
                        <p className="text-zinc-600 dark:text-zinc-400">데이터를 불러오는 중...</p>
                    </div>
                )}

                {error && (
                    <div className="rounded-lg bg-red-100 dark:bg-red-900 p-4 text-red-800 dark:text-red-200">
                        <p>오류: {error}</p>
                        <button
                            onClick={fetchTitanicData}
                            className="mt-2 px-4 py-2 rounded bg-red-200 dark:bg-red-800 text-red-900 dark:text-red-100 hover:bg-red-300 dark:hover:bg-red-700"
                        >
                            다시 시도
                        </button>
                    </div>
                )}

                {!loading && !error && passengers.length > 0 && (
                    <div className="grid gap-4">
                        {passengers.map((passenger) => (
                            <div
                                key={passenger.passengerId}
                                className="rounded-lg bg-white dark:bg-zinc-800 p-6 shadow-md border border-zinc-200 dark:border-zinc-700"
                            >
                                <div className="flex items-start justify-between mb-4">
                                    <div className="flex items-center gap-3">
                                        <span className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                                            #{passenger.rank}
                                        </span>
                                        <h2 className="text-xl font-semibold text-black dark:text-zinc-50">
                                            {passenger.name}
                                        </h2>
                                    </div>
                                    <span
                                        className={`px-3 py-1 rounded-full text-sm font-medium ${
                                            passenger.survived === "생존"
                                                ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                                                : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
                                        }`}
                                    >
                                        {passenger.survived}
                                    </span>
                                </div>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                    <div>
                                        <p className="text-zinc-600 dark:text-zinc-400 mb-1">승객 ID</p>
                                        <p className="font-medium text-black dark:text-zinc-50">
                                            {passenger.passengerId}
                                        </p>
                                    </div>
                                    <div>
                                        <p className="text-zinc-600 dark:text-zinc-400 mb-1">등급</p>
                                        <p className="font-medium text-black dark:text-zinc-50">
                                            {passenger.pclass}
                                        </p>
                                    </div>
                                    <div>
                                        <p className="text-zinc-600 dark:text-zinc-400 mb-1">성별</p>
                                        <p className="font-medium text-black dark:text-zinc-50">
                                            {passenger.sex}
                                        </p>
                                    </div>
                                    <div>
                                        <p className="text-zinc-600 dark:text-zinc-400 mb-1">나이</p>
                                        <p className="font-medium text-black dark:text-zinc-50">
                                            {passenger.age ? `${passenger.age}세` : "미상"}
                                        </p>
                                    </div>
                                    <div>
                                        <p className="text-zinc-600 dark:text-zinc-400 mb-1">요금</p>
                                        <p className="font-medium text-black dark:text-zinc-50">
                                            ${passenger.fare.toFixed(2)}
                                        </p>
                                    </div>
                                    <div>
                                        <p className="text-zinc-600 dark:text-zinc-400 mb-1">객실</p>
                                        <p className="font-medium text-black dark:text-zinc-50">
                                            {passenger.cabin || "미상"}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </main>
        </div>
    );
}

