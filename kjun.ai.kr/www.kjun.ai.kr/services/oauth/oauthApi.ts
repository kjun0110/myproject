/**
 * OAuth API 호출 레이어
 * 백엔드와의 통신만 담당 (순수 함수)
 */

import { API_GATEWAY_URL } from "@/constants/oauth";
import { parseErrorResponse } from "@/utils/error";
import type { OAuthProvider, OAuthResponse } from "@/types";

/**
 * OAuth 로그인 API 호출
 */
export async function requestOAuthLogin(
  provider: OAuthProvider
): Promise<OAuthResponse> {
  const endpoint =
    provider === "kakao"
      ? "/oauth/kakao/login"
      : `/oauth/${provider}/login`;

  const response = await fetch(`${API_GATEWAY_URL}${endpoint}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({}),
  });

  if (!response.ok) {
    const errorMessage = await parseErrorResponse(response, endpoint);
    throw new Error(errorMessage);
  }

  const data: OAuthResponse = await response.json();
  console.log(`✅ Gateway 응답 (${provider}):`, data);

  return data;
}

/**
 * Access Token 갱신 API 호출
 */
export async function refreshAccessTokenApi(
  refreshToken: string
): Promise<{ accessToken: string }> {
  const response = await fetch(`${API_GATEWAY_URL}/oauth/refresh`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ refreshToken }),
  });

  if (!response.ok) {
    throw new Error("토큰 갱신 실패");
  }

  return await response.json();
}

/**
 * 로그아웃 API 호출
 * - Upstash Redis에서 Access Token 삭제
 * - Neon PostgreSQL에서 Refresh Token 삭제
 * - Access Token 블랙리스트 추가
 */
export async function logoutApi(userId: string | number, accessToken: string | null): Promise<void> {
  if (!userId) {
    throw new Error("사용자 ID가 필요합니다");
  }

  const response = await fetch(`${API_GATEWAY_URL}/oauth/logout`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      userId: typeof userId === "string" ? parseInt(userId, 10) : userId,
      accessToken: accessToken || undefined, // null이면 undefined로 전송하지 않음
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || "로그아웃 실패");
  }

  console.log("✅ 백엔드 로그아웃 완료 (Redis, Neon DB에서 토큰 삭제 완료)");
}

