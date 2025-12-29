import { NextRequest, NextResponse } from "next/server";
import { readFile } from "fs/promises";
import { join } from "path";

export async function GET(request: NextRequest) {
    try {
        const searchParams = request.nextUrl.searchParams;
        const filePath = searchParams.get("path");

        if (!filePath) {
            return NextResponse.json(
                { error: "파일 경로가 제공되지 않았습니다." },
                { status: 400 }
            );
        }

        // FastAPI 서버에서 파일 가져오기
        const fastApiUrl = process.env.FASTAPI_URL || "http://localhost:9100";
        const fileUrl = `${fastApiUrl}/download?path=${encodeURIComponent(filePath)}`;

        const response = await fetch(fileUrl);

        if (!response.ok) {
            return NextResponse.json(
                { error: "파일을 찾을 수 없습니다." },
                { status: 404 }
            );
        }

        const fileBuffer = await response.arrayBuffer();
        const contentType = response.headers.get("content-type") || "application/octet-stream";

        return new NextResponse(fileBuffer, {
            headers: {
                "Content-Type": contentType,
                "Content-Disposition": `attachment; filename="${filePath.split("/").pop()}"`,
            },
        });
    } catch (error: any) {
        console.error("파일 다운로드 오류:", error);
        return NextResponse.json(
            { error: error.message || "파일 다운로드 중 오류가 발생했습니다." },
            { status: 500 }
        );
    }
}

