/**
 * 대시보드 페이지 서비스
 * 로그아웃 관련 핸들러
 */

import { authLogout, getAccessToken, getUserInfo } from "@/store/authStore";
import { logoutApi } from "@/services/oauth/oauthApi";

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
 * - 백엔드 API 호출하여 모든 저장소에서 토큰 삭제:
 *   - Upstash Redis에서 Access Token 삭제
 *   - Neon PostgreSQL에서 Refresh Token 삭제
 *   - Access Token 블랙리스트 추가
 * - HttpOnly 쿠키에서 Refresh Token 삭제
 * - Zustand 스토어 초기화 (Access Token 메모리에서 삭제)
 */
export async function handleLogout(): Promise<void> {
  try {
    // 사용자 ID와 Access Token 가져오기
    const userInfo = getUserInfo();
    const accessToken = getAccessToken();
    const userId = userInfo?.id;

    // 백엔드 로그아웃 API 호출 (모든 저장소에서 토큰 삭제)
    if (userId) {
      try {
        await logoutApi(userId, accessToken);
      } catch (error) {
        console.error("❌ 백엔드 로그아웃 API 호출 실패:", error);
        // 백엔드 호출 실패해도 프론트엔드 로그아웃은 진행
      }
    } else {
      console.warn("⚠️ 사용자 ID가 없어 백엔드 로그아웃 API를 호출하지 않습니다.");
    }

    // HttpOnly 쿠키에서 Refresh Token 삭제
    await deleteRefreshTokenCookie();

    // Zustand 스토어 초기화 (Access Token 메모리에서 삭제, localStorage 정리)
    authLogout();

    console.log("✅ 로그아웃 완료 (모든 저장소에서 토큰 삭제 완료)");
  } catch (error) {
    console.error("❌ 로그아웃 처리 중 오류 발생:", error);
    // 에러가 나도 최소한 프론트엔드 로그아웃은 진행
    authLogout();
    await deleteRefreshTokenCookie();
  }
}

