import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { filename } = body;

        if (!filename) {
            return NextResponse.json(
                { error: "파일명이 제공되지 않았습니다." },
                { status: 400 }
            );
        }

        // FastAPI 서버 URL (환경 변수 또는 기본값)
        const fastApiUrl = process.env.FASTAPI_URL || "http://localhost:9100";

        // FastAPI 서버로 포즈 추정 요청 (JSON body 포함)
        const response = await fetch(`${fastApiUrl}/detect-pose`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ filename }),
        });

        const data = await response.json();

        if (!response.ok) {
            return NextResponse.json(
                { error: data.detail || "포즈 추정 중 오류가 발생했습니다." },
                { status: response.status }
            );
        }

        return NextResponse.json(data, { status: 200 });
    } catch (error: any) {
        console.error("포즈 추정 API 오류:", error);
        return NextResponse.json(
            { error: error.message || "포즈 추정 중 오류가 발생했습니다." },
            { status: 500 }
        );
    }
}

