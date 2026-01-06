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
 */
export async function logoutApi(accessToken: string): Promise<void> {
  const response = await fetch(`${API_GATEWAY_URL}/oauth/logout`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new Error("로그아웃 실패");
  }
}

