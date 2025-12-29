import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // FastAPI 서버 URL (환경 변수 또는 기본값)
    const fastApiUrl = process.env.DIFFUSER_API_URL || "http://localhost:8000";

    // FastAPI 서버로 요청 전달
    const response = await fetch(`${fastApiUrl}/api/v1/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(
        { error: data.detail || "이미지 생성에 실패했습니다." },
        { status: response.status }
      );
    }

    return NextResponse.json(data, { status: 200 });
  } catch (error: any) {
    console.error("이미지 생성 API 오류:", error);
    return NextResponse.json(
      { error: error.message || "이미지 생성 중 오류가 발생했습니다." },
      { status: 500 }
    );
  }
}

