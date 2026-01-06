# HttpOnly 쿠키 구현 코드 위치 검토

## ✅ 현재 구조 (적절함)

### 1. API Route
**위치**: `app/api/auth/set-refresh-token/route.ts`
- ✅ **적절함**: 인증 관련 API이므로 `app/api/auth/` 경로가 적절합니다.
- 기능:
  - `POST`: Refresh token을 HttpOnly 쿠키에 저장
  - `DELETE`: Refresh token 쿠키 삭제

### 2. OAuth 성공 페이지 서비스
**위치**: `services/oauth/[provider]/success/successService.ts`
- ✅ **적절함**: OAuth 성공 페이지의 서비스 레이어이므로 위치가 적절합니다.
- 함수:
  - `setRefreshTokenCookie()`: API Route를 호출하여 쿠키 저장
  - `saveOAuthData()`: Access Token은 Zustand에, Refresh Token은 HttpOnly 쿠키에 저장

### 3. 대시보드 페이지 서비스
**위치**: `services/dashboard/dashboardService.ts`
- ✅ **적절함**: 로그아웃 관련 서비스이므로 위치가 적절합니다.
- 함수:
  - `deleteRefreshTokenCookie()`: API Route를 호출하여 쿠키 삭제
  - `handleLogout()`: Zustand 초기화 + 쿠키 삭제

### 4. OAuth 성공 페이지 컴포넌트
**위치**: `app/oauth/[provider]/success/page.tsx`
- ✅ **적절함**: OAuth 성공 페이지이므로 위치가 적절합니다.
- `saveOAuthData()` 서비스를 호출하여 토큰 저장

## 📋 코드 흐름

### 로그인 시:
1. `app/oauth/[provider]/success/page.tsx` (페이지)
   ↓
2. `services/oauth/[provider]/success/successService.ts` (서비스)
   - `saveOAuthData()` 호출
   - `setRefreshTokenCookie()` 호출
   ↓
3. `app/api/auth/set-refresh-token/route.ts` (API Route)
   - HttpOnly 쿠키에 refresh token 저장

### 로그아웃 시:
1. `components/Header.tsx` 또는 `app/dashboard/page.tsx` (페이지)
   ↓
2. `services/dashboard/dashboardService.ts` (서비스)
   - `handleLogout()` 호출
   - `deleteRefreshTokenCookie()` 호출
   ↓
3. `app/api/auth/set-refresh-token/route.ts` (API Route)
   - HttpOnly 쿠키에서 refresh token 삭제

## ✅ 결론

**모든 코드가 적절한 위치에 있습니다.**

- 페이지별 구조에 맞게 서비스가 분리되어 있음
- API Route는 인증 관련 경로에 적절히 위치
- 각 서비스 함수가 해당 페이지의 책임에 맞게 배치됨
- 코드 흐름이 명확하고 일관성 있음

## 💡 추가 개선 제안 (선택사항)

현재 구조가 적절하지만, 만약 공통 인증 기능을 더 중앙화하고 싶다면:

1. **옵션 1**: `services/oauth/oauthApi.ts`에 쿠키 관련 함수 추가
   - 장점: OAuth 관련 모든 API 호출이 한 곳에 모임
   - 단점: 페이지별 구조와 약간 불일치

2. **옵션 2**: `services/auth/` 폴더 생성 (현재는 제거됨)
   - 장점: 인증 관련 기능을 완전히 분리
   - 단점: 페이지별 구조 원칙과 충돌

**현재 구조를 유지하는 것을 권장합니다.** ✅

