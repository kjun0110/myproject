/**
 * 대시보드 페이지 서비스
 * 로그아웃 관련 핸들러
 */

import { authLogout } from "@/store/authStore";

/**
 * Refresh Token 쿠키 삭제
 */
export async function deleteRefreshTokenCookie(): Promise<void> {
  try {
    const response = await fetch("/api/auth/set-refresh-token", {
      method: "DELETE",
    });

    if (!response.ok) {
      console.warn("⚠️ Failed to delete refresh token cookie");
    } else {
      console.log("✅ Refresh token cookie deleted");
    }
  } catch (error) {
    console.error("❌ Failed to delete refresh token cookie:", error);
    // 에러가 나도 로그아웃은 진행
  }
}

/**
 * 로그아웃 처리 (무상태 함수)
 * - Zustand 스토어 초기화
 * - HttpOnly 쿠키에서 refresh token 삭제
 */
export async function handleLogout(): Promise<void> {
  // Zustand 스토어 초기화
  authLogout();

  // HttpOnly 쿠키에서 refresh token 삭제
  await deleteRefreshTokenCookie();

  console.log("✅ 로그아웃 완료");
}

