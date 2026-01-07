/**
 * OAuth 성공 페이지 서비스
 * OAuth 콜백 후 토큰 저장 관련 핸들러
 */

import { authLogin } from "@/store/auth.store";
import type { OAuthProvider, UserInfo } from "@/store/auth.index";

/**
 * Refresh Token을 HttpOnly 쿠키에 저장
 */
export async function setRefreshTokenCookie(refreshToken: string): Promise<void> {
  try {
    const response = await fetch("/api/auth/set-refresh-token", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ refreshToken }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Failed to set refresh token cookie");
    }

    console.log("✅ Refresh token saved to HttpOnly cookie");
  } catch (error) {
    console.error("❌ Failed to set refresh token cookie:", error);
    throw error;
  }
}

/**
 * OAuth 정보 저장
 * - Access Token: Zustand 메모리에 저장
 * - Refresh Token: HttpOnly 쿠키에 저장
 */
export async function saveOAuthData(
  token: string,
  provider: OAuthProvider,
  refreshToken?: string | null,
  user?: UserInfo
): Promise<void> {
  // Access Token과 사용자 정보는 Zustand에 저장
  // refreshToken 파라미터는 제거됨 (HttpOnly 쿠키에 저장하므로)
  authLogin(token, provider, user);

  // Refresh Token이 있으면 HttpOnly 쿠키에 저장
  if (refreshToken) {
    await setRefreshTokenCookie(refreshToken);
  }

  console.log(`✅ ${provider} 로그인 정보 저장 완료 (Access Token은 메모리에만, Refresh Token은 HttpOnly 쿠키에)`);
}
