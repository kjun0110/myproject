import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
    try {
        const formData = await request.formData();
        const files = formData.getAll("files") as File[];

        if (!files || files.length === 0) {
            return NextResponse.json(
                { error: "파일이 제공되지 않았습니다." },
                { status: 400 }
            );
        }

        // FastAPI 서버 URL (환경 변수 또는 기본값)
        const fastApiUrl = process.env.FASTAPI_URL || "http://localhost:9100";

        // FastAPI 서버로 파일 전송
        const uploadFormData = new FormData();
        files.forEach((file) => {
            uploadFormData.append("files", file);
        });

        const response = await fetch(`${fastApiUrl}/upload`, {
            method: "POST",
            body: uploadFormData,
        });

        const data = await response.json();

        if (!response.ok) {
            return NextResponse.json(
                { error: data.detail || "FastAPI 서버 오류가 발생했습니다." },
                { status: response.status }
            );
        }

        return NextResponse.json(data, { status: 200 });
    } catch (error: any) {
        console.error("파일 업로드 API 오류:", error);
        return NextResponse.json(
            { error: error.message || "파일 업로드 중 오류가 발생했습니다." },
            { status: 500 }
        );
    }
}

