/**
 * Auth Store Module (Ducks Pattern)
 * 
 * Ducks Pattern 원칙:
 * - 모든 관련 코드를 하나의 모듈에 모음 (Types, Store, Actions, Selectors)
 * - 외부 의존성 최소화
 * - 명확한 export 구조
 * 
 * 구조:
 * - auth.store.ts: Types + Zustand Store + Actions + Selectors + Getters
 * - auth.provider.tsx: React Provider 컴포넌트
 * - auth.index.ts: 통합 Export (Ducks Pattern)
 * 
 * 사용법:
 * 1. Provider 설정: app/layout.tsx에서 <AuthProvider> 래핑
 * 2. 컴포넌트 내부: useAuthStore 훅 사용
 * 3. 컴포넌트 외부: getter 함수 사용 (getAccessToken, getUserInfo 등)
 * 
 * 보안:
 * - accessToken: 메모리에만 저장 (새로고침 시 초기화)
 * - refreshToken: HttpOnly 쿠키에 저장 (클라이언트 접근 불가)
 * - userInfo: localStorage에 저장
 * - loginProvider: localStorage에 저장
 */

// ============================================
// Types (Ducks Pattern - 모든 타입을 스토어 내부에 정의)
// ============================================
export type {
    OAuthProvider,
    UserInfo,
    OAuthResponse,
    OAuthError,
} from "./auth.store";

// ============================================
// Store & Provider
// ============================================
export { useAuthStore } from "./auth.store";
export { AuthProvider } from "./auth.provider";

// ============================================
// Selectors
// ============================================
export {
    selectAccessToken,
    selectUserInfo,
    selectLoginProvider,
    selectIsLoggedIn,
} from "./auth.store";

// ============================================
// Action Creators
// ============================================
export {
    authLogin,
    authLogout,
    authRefreshToken,
    authSetAccessToken,
    authSetUserInfo,
    authSetLoginProvider,
} from "./auth.store";

// ============================================
// Getters (컴포넌트 외부에서 사용)
// ============================================
export {
    getAccessToken,
    getUserInfo,
    getLoginProvider,
    getIsLoggedIn,
} from "./auth.store";

