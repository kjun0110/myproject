"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Header } from "@/components/Header";
import { Sidebar } from "@/components/Sidebar";

export default function DiffuserPage() {
    const router = useRouter();
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);
    const [prompt, setPrompt] = useState("");
    const [negativePrompt, setNegativePrompt] = useState("");
    const [width, setWidth] = useState(768);
    const [height, setHeight] = useState(768);
    const [steps, setSteps] = useState(4);
    const [seed, setSeed] = useState<number | null>(null);
    const [isGenerating, setIsGenerating] = useState(false);
    const [generatedImage, setGeneratedImage] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleGenerate = async () => {
        if (!prompt.trim()) {
            setError("프롬프트를 입력해주세요.");
            return;
        }

        setIsGenerating(true);
        setError(null);
        setGeneratedImage(null);

        try {
            const requestBody: any = {
                prompt: prompt.trim(),
                width: width,
                height: height,
                steps: steps,
            };

            if (negativePrompt.trim()) {
                requestBody.negative_prompt = negativePrompt.trim();
            }

            if (seed !== null && seed !== undefined) {
                requestBody.seed = seed;
            }

            // Next.js API route를 통해 FastAPI로 프록시
            const response = await fetch("/api/diffuser/generate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(requestBody),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || errorData.detail || "이미지 생성에 실패했습니다.");
            }

            const data = await response.json();

            // image_url이 상대 경로인 경우 Next.js API route를 통해 프록시
            let imageUrl = data.image_url;
            if (imageUrl.startsWith("/")) {
                // Next.js API route를 통해 이미지 프록시
                imageUrl = `/api/diffuser/image?path=${encodeURIComponent(imageUrl)}`;
            }

            setGeneratedImage(imageUrl);
        } catch (err: any) {
            setError(err.message || "이미지 생성 중 오류가 발생했습니다.");
            console.error("Error generating image:", err);
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <div className="flex min-h-screen bg-zinc-50 font-sans dark:bg-black">
            {/* 헤더 */}
            <Header
                onLoginClick={() => router.push("/")}
                onAIClick={() => { }}
                isSidebarOpen={isSidebarOpen}
                onSidebarToggle={() => setIsSidebarOpen(!isSidebarOpen)}
            />

            {/* 사이드바 */}
            <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />

            {/* 메인 콘텐츠 */}
            <main
                className={`flex-1 transition-all duration-300 ${isSidebarOpen ? "ml-64" : "ml-0"
                    }`}
                style={{ paddingTop: "64px" }}
            >
                <div className="min-h-[calc(100vh-64px)] p-8">
                    <div className="max-w-6xl mx-auto">
                        {/* 헤더 */}
                        <div className="flex items-center justify-between mb-8">
                            <h1 className="text-4xl font-bold text-black dark:text-zinc-50">
                                이미지 생성 (Diffuser)
                            </h1>
                            <button
                                onClick={() => router.push("/")}
                                className="px-4 py-2 rounded-lg bg-zinc-200 dark:bg-zinc-700 text-zinc-800 dark:text-zinc-200 hover:bg-zinc-300 dark:hover:bg-zinc-600 transition-colors"
                            >
                                뒤로가기
                            </button>
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                            {/* 입력 폼 */}
                            <div className="space-y-6">
                                <div className="bg-white dark:bg-zinc-900 rounded-lg p-6 shadow-sm border border-zinc-200 dark:border-zinc-800">
                                    <h2 className="text-2xl font-semibold mb-6 text-black dark:text-zinc-50">
                                        생성 설정
                                    </h2>

                                    {/* 프롬프트 */}
                                    <div className="mb-4">
                                        <label className="block text-sm font-medium mb-2 text-zinc-700 dark:text-zinc-300">
                                            프롬프트 *
                                        </label>
                                        <textarea
                                            value={prompt}
                                            onChange={(e) => setPrompt(e.target.value)}
                                            placeholder="예: a cute robot barista, cinematic lighting"
                                            className="w-full px-4 py-3 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-black dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
                                            rows={4}
                                        />
                                    </div>

                                    {/* 네거티브 프롬프트 */}
                                    <div className="mb-4">
                                        <label className="block text-sm font-medium mb-2 text-zinc-700 dark:text-zinc-300">
                                            네거티브 프롬프트 (선택)
                                        </label>
                                        <textarea
                                            value={negativePrompt}
                                            onChange={(e) => setNegativePrompt(e.target.value)}
                                            placeholder="제외할 내용을 입력하세요"
                                            className="w-full px-4 py-3 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-black dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
                                            rows={3}
                                        />
                                    </div>

                                    {/* 설정 옵션 */}
                                    <div className="grid grid-cols-2 gap-4 mb-4">
                                        <div>
                                            <label className="block text-sm font-medium mb-2 text-zinc-700 dark:text-zinc-300">
                                                너비
                                            </label>
                                            <input
                                                type="number"
                                                value={width}
                                                onChange={(e) => setWidth(parseInt(e.target.value) || 768)}
                                                min="64"
                                                max="2048"
                                                step="64"
                                                className="w-full px-4 py-2 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-black dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-purple-500"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium mb-2 text-zinc-700 dark:text-zinc-300">
                                                높이
                                            </label>
                                            <input
                                                type="number"
                                                value={height}
                                                onChange={(e) => setHeight(parseInt(e.target.value) || 768)}
                                                min="64"
                                                max="2048"
                                                step="64"
                                                className="w-full px-4 py-2 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-black dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-purple-500"
                                            />
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-2 gap-4 mb-6">
                                        <div>
                                            <label className="block text-sm font-medium mb-2 text-zinc-700 dark:text-zinc-300">
                                                스텝 수
                                            </label>
                                            <input
                                                type="number"
                                                value={steps}
                                                onChange={(e) => setSteps(parseInt(e.target.value) || 4)}
                                                min="1"
                                                max="50"
                                                className="w-full px-4 py-2 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-black dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-purple-500"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium mb-2 text-zinc-700 dark:text-zinc-300">
                                                시드 (선택)
                                            </label>
                                            <input
                                                type="number"
                                                value={seed || ""}
                                                onChange={(e) =>
                                                    setSeed(e.target.value ? parseInt(e.target.value) : null)
                                                }
                                                placeholder="랜덤"
                                                className="w-full px-4 py-2 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-black dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-purple-500"
                                            />
                                        </div>
                                    </div>

                                    {/* 생성 버튼 */}
                                    <button
                                        onClick={handleGenerate}
                                        disabled={isGenerating || !prompt.trim()}
                                        className="w-full px-6 py-3 rounded-lg bg-purple-600 hover:bg-purple-700 disabled:bg-zinc-400 disabled:cursor-not-allowed text-white font-medium transition-colors"
                                    >
                                        {isGenerating ? "생성 중..." : "이미지 생성"}
                                    </button>

                                    {/* 에러 메시지 */}
                                    {error && (
                                        <div className="mt-4 p-4 rounded-lg bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200">
                                            {error}
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* 생성된 이미지 */}
                            <div className="space-y-6">
                                <div className="bg-white dark:bg-zinc-900 rounded-lg p-6 shadow-sm border border-zinc-200 dark:border-zinc-800">
                                    <h2 className="text-2xl font-semibold mb-6 text-black dark:text-zinc-50">
                                        생성된 이미지
                                    </h2>

                                    {isGenerating && (
                                        <div className="flex items-center justify-center h-96">
                                            <div className="text-center">
                                                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mb-4"></div>
                                                <p className="text-zinc-600 dark:text-zinc-400">
                                                    이미지를 생성하고 있습니다...
                                                </p>
                                            </div>
                                        </div>
                                    )}

                                    {!isGenerating && !generatedImage && (
                                        <div className="flex items-center justify-center h-96 border-2 border-dashed border-zinc-300 dark:border-zinc-700 rounded-lg">
                                            <p className="text-zinc-500 dark:text-zinc-400">
                                                생성된 이미지가 여기에 표시됩니다
                                            </p>
                                        </div>
                                    )}

                                    {!isGenerating && generatedImage && (
                                        <div className="space-y-4">
                                            <div className="relative w-full aspect-square rounded-lg overflow-hidden border border-zinc-200 dark:border-zinc-700">
                                                <img
                                                    src={generatedImage}
                                                    alt="Generated"
                                                    className="w-full h-full object-contain"
                                                />
                                            </div>
                                            <a
                                                href={generatedImage}
                                                download
                                                className="block w-full px-4 py-2 text-center rounded-lg bg-zinc-200 dark:bg-zinc-700 text-zinc-800 dark:text-zinc-200 hover:bg-zinc-300 dark:hover:bg-zinc-600 transition-colors"
                                            >
                                                이미지 다운로드
                                            </a>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}

