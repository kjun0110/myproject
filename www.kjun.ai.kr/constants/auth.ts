import { type AuthProvider } from "@/lib/auth";

// API 설정
export const API_GATEWAY_URL = "http://localhost:8080";

// Provider 이름 매핑
export const PROVIDER_NAMES: Record<AuthProvider, string> = {
  kakao: "카카오",
  naver: "네이버",
  google: "구글",
};

// 에러 메시지
export const ERROR_MESSAGES = {
  SERVER_CONNECTION_FAILED: "서버 연결에 실패했습니다. 서버가 실행 중인지 확인해주세요.",
  TOKEN_SAVE_FAILED: "토큰 저장에 실패했습니다.",
  TOKEN_NOT_RECEIVED: "토큰을 받지 못했습니다.",
  LOGIN_FAILED: "로그인에 실패했습니다.",
  INVALID_REQUEST: "잘못된 요청입니다.",
  AUTHENTICATION_FAILED: "인증에 실패했습니다.",
  ENDPOINT_NOT_FOUND: "API 엔드포인트를 찾을 수 없습니다.",
} as const;

// 로컬스토리지 키
export const STORAGE_KEYS = {
  ACCESS_TOKEN: "access_token",
  USER_INFO: "user_info",
  LOGIN_PROVIDER: "login_provider",
  REFRESH_TOKEN: "refresh_token",
} as const;

