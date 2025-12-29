import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
    try {
        const searchParams = request.nextUrl.searchParams;
        const imagePath = searchParams.get("path");

        if (!imagePath) {
            return NextResponse.json(
                { error: "이미지 경로가 제공되지 않았습니다." },
                { status: 400 }
            );
        }

        // FastAPI 서버 URL
        const fastApiUrl = process.env.DIFFUSER_API_URL || "http://localhost:8000";

        // FastAPI 서버에서 이미지 가져오기
        const response = await fetch(`${fastApiUrl}${imagePath}`, {
            method: "GET",
        });

        if (!response.ok) {
            return NextResponse.json(
                { error: "이미지를 가져올 수 없습니다." },
                { status: response.status }
            );
        }

        // 이미지 데이터 가져오기
        const imageBuffer = await response.arrayBuffer();
        const contentType = response.headers.get("content-type") || "image/png";

        // 이미지 응답 반환
        return new NextResponse(imageBuffer, {
            status: 200,
            headers: {
                "Content-Type": contentType,
                "Cache-Control": "public, max-age=31536000, immutable",
            },
        });
    } catch (error: any) {
        console.error("이미지 가져오기 API 오류:", error);
        return NextResponse.json(
            { error: error.message || "이미지를 가져오는 중 오류가 발생했습니다." },
            { status: 500 }
        );
    }
}

