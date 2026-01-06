/**
 * 메인 페이지 서비스
 * 소셜 로그인 관련 핸들러
 */

import { authLogin } from "@/store/authStore";
import { requestOAuthLogin } from "@/services/oauth/oauthApi";
import { ERROR_MESSAGES } from "@/constants/oauth";
import type { OAuthProvider, OAuthResponse } from "@/types";

/**
 * 로그인 URL로 리다이렉트
 */
export function redirectToLoginUrl(loginUrl: string, provider: OAuthProvider): void {
  console.log(`🔗 ${provider} 로그인 URL로 리다이렉트:`, loginUrl);
  window.location.replace(loginUrl);
}

/**
 * 소셜 로그인 처리 (무상태 함수)
 */
export async function handleSocialLogin(
  provider: OAuthProvider,
  onSuccess?: (data: OAuthResponse) => void,
  onError?: (error: Error) => void
): Promise<void> {
  try {
    const data = await requestOAuthLogin(provider);

    // 로그인 URL을 반환하는 경우
    if (data.loginUrl) {
      redirectToLoginUrl(data.loginUrl, provider);
      return;
    }

    // 토큰을 직접 반환하는 경우
    // 주의: refreshToken은 HttpOnly 쿠키에 저장되므로 authLogin에서 null로 전달해도 됨
    // 실제 refreshToken 저장은 successService에서 처리됨
    if (data.success && data.token) {
      authLogin(data.token, null, provider, data.user); // refreshToken은 null (HttpOnly 쿠키에 저장)
      onSuccess?.(data);
      return;
    }

    throw new Error(data.message || ERROR_MESSAGES.LOGIN_FAILED);
  } catch (error) {
    console.error(`❌ ${provider} 로그인 에러:`, error);
    onError?.(error instanceof Error ? error : new Error(ERROR_MESSAGES.SERVER_CONNECTION_FAILED));
    throw error;
  }
}

