import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";

/**
 * Refresh Token을 HttpOnly 쿠키에 저장하는 API Route
 * 
 * POST /api/auth/set-refresh-token
 * Body: { refreshToken: string }
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { refreshToken } = body;

    if (!refreshToken || typeof refreshToken !== "string") {
      return NextResponse.json(
        { error: "Refresh token is required" },
        { status: 400 }
      );
    }

    // HttpOnly 쿠키 설정
    const cookieStore = await cookies();
    cookieStore.set("refresh_token", refreshToken, {
      httpOnly: true, // JavaScript에서 접근 불가
      secure: process.env.NODE_ENV === "production", // HTTPS에서만 전송 (프로덕션)
      sameSite: "lax", // CSRF 공격 방지
      maxAge: 60 * 60 * 24 * 7, // 7일
      path: "/", // 모든 경로에서 접근 가능
    });

    return NextResponse.json(
      { success: true, message: "Refresh token saved to HttpOnly cookie" },
      { status: 200 }
    );
  } catch (error) {
    console.error("Failed to set refresh token cookie:", error);
    return NextResponse.json(
      { error: "Failed to set refresh token" },
      { status: 500 }
    );
  }
}

/**
 * Refresh Token 쿠키 삭제
 * 
 * DELETE /api/auth/set-refresh-token
 */
export async function DELETE() {
  try {
    const cookieStore = await cookies();
    cookieStore.delete("refresh_token");

    return NextResponse.json(
      { success: true, message: "Refresh token cookie deleted" },
      { status: 200 }
    );
  } catch (error) {
    console.error("Failed to delete refresh token cookie:", error);
    return NextResponse.json(
      { error: "Failed to delete refresh token" },
      { status: 500 }
    );
  }
}

