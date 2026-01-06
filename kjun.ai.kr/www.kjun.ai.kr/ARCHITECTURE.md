# 프로젝트 아키텍처

## 📁 디렉토리 구조

```
www.kjun.ai.kr/
├── types/                  # 타입 정의 (중앙 관리)
│   ├── auth.ts            # 인증 관련 타입
│   └── index.ts           # 타입 export
│
├── utils/                  # 순수 유틸리티 함수
│   └── error.ts           # 에러 처리
│
├── services/               # 비즈니스 로직 (무상태, 페이지별 구조)
│   ├── page/              # 메인 페이지 서비스
│   │   └── pageService.ts
│   ├── dashboard/         # 대시보드 페이지 서비스
│   │   └── dashboardService.ts
│   ├── oauth/             # OAuth 관련 서비스
│   │   ├── [provider]/    # 동적 라우팅
│   │   │   └── success/
│   │   │       └── successService.ts
│   │   └── oauthApi.ts    # 공통 API 호출 레이어
│
├── hooks/                  # React Hooks (페이지별 구조)
│   ├── page/              # 메인 페이지 Hook
│   │   └── useSocialLogin.ts
│   └── dashboard/        # 대시보드 페이지 Hook
│       └── useAuth.ts
│
├── store/                  # Zustand 스토어
│   ├── authStore.ts       # 인증 스토어 (무상태 인터페이스 포함)
│   └── README.md          # 스토어 사용 가이드
│
├── constants/              # 상수
│   └── oauth.ts           # OAuth 관련 상수
│
├── components/             # React 컴포넌트
├── app/                    # Next.js 페이지
└── lib/                    # 레거시 (점진적 제거)
    └── oauth.ts           # @deprecated - 하위 호환성만 유지
```

## 🏗️ 레이어 구조

### 1. **Types Layer** (`types/`)
- 모든 타입 정의를 중앙에서 관리
- 타입 재사용성 극대화
- 순환 참조 방지

```typescript
// types/auth.ts
export type OAuthProvider = "kakao" | "naver" | "google";
export interface UserInfo { ... }
```

### 2. **Utils Layer** (`utils/`)
- 순수 함수로 구성
- 외부 의존성 최소화
- 테스트 용이

```typescript
// utils/error.ts
export async function parseErrorResponse(response, endpoint) { ... }
```

### 3. **Services Layer** (`services/`)
- 비즈니스 로직을 무상태 함수로 구현
- API 호출과 비즈니스 로직 분리

#### 3.1 API Layer (`services/oauth/oauthApi.ts`)
- 공통 API 호출 함수들
- 여러 페이지에서 공유 사용
- 백엔드와의 통신만 담당
- HTTP 요청/응답 처리
- 에러 핸들링

```typescript
export async function requestOAuthLogin(provider) {
  const response = await fetch(...);
  return await response.json();
}
```

#### 3.2 Business Logic Layer (페이지별 분리)
- `services/page/pageService.ts`: 메인 페이지 (소셜 로그인)
- `services/dashboard/dashboardService.ts`: 대시보드 (로그아웃)
- `services/oauth/[provider]/success/successService.ts`: OAuth 성공 페이지 (토큰 저장)
- 비즈니스 로직 구현
- 무상태 함수로 구성
- 스토어와 API를 연결

```typescript
export async function handleSocialLogin(provider, onSuccess, onError) {
  const data = await requestOAuthLogin(provider);
  if (data.loginUrl) redirectToLoginUrl(data.loginUrl, provider);
  else saveOAuthData(data.token, provider, ...);
}
```

### 4. **Store Layer** (`store/`)
- Zustand를 사용한 상태 관리
- **무상태 인터페이스** 제공
- Access Token은 메모리에만 저장

```typescript
// Zustand 스토어
export const useAuthStore = create<AuthState>((set, get) => ({ ... }));

// 무상태 인터페이스 (React 외부에서도 사용 가능)
export const authLogin = (...) => useAuthStore.getState().login(...);
export const getAccessToken = () => useAuthStore.getState().accessToken;
```

### 5. **Hooks Layer** (`hooks/`)
- React 컴포넌트에서 사용하는 Hook
- Zustand 스토어를 감싸서 제공
- 컴포넌트 로직 재사용

```typescript
// hooks/dashboard/useAuth.ts
export function useAuth() {
  const isLoggedIn = useAuthStore((state) => state.isLoggedIn);
  return { isLoggedIn, logout: handleLogout };
}

// hooks/page/useSocialLogin.ts
export function useSocialLogin() {
  const [loading, setLoading] = useState(...);
  const login = useCallback(async (provider) => {
    await handleSocialLogin(provider, ...);
  }, []);
  return { loading, login, loginWithKakao, ... };
}
```

## 🔄 데이터 흐름

```
┌─────────────────────────────────────────────────────────────┐
│                     React Component                          │
│                                                               │
│  const { login, loading } = useSocialLogin();               │
│  const { isLoggedIn } = useAuth();                          │
│  (hooks/page/useSocialLogin.ts)                             │
│  (hooks/dashboard/useAuth.ts)                              │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                    Hooks Layer (페이지별 분리)              │
│                                                               │
│  - hooks/page/useSocialLogin: 로딩/에러 상태 관리           │
│  - hooks/dashboard/useAuth: 인증 상태 구독                  │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                  Services Layer (페이지별 분리)              │
│                                                               │
│  - pageService.ts: handleSocialLogin()                       │
│  - dashboardService.ts: handleLogout()                       │
│  - successService.ts: saveOAuthData()                         │
└───────────┬─────────────────────────┬───────────────────────┘
            │                         │
            ↓                         ↓
┌───────────────────────┐   ┌───────────────────────┐
│   API Layer           │   │   Store Layer         │
│                       │   │                       │
│  oauthApi.ts          │   │  authStore.ts         │
│  - requestOAuthLogin()│   │  - authLogin()        │
└───────────────────────┘   │  - getAccessToken()   │
                             └───────────────────────┘
```

## 🎯 무상태 패턴 (Stateless Pattern)

### 왜 무상태 패턴인가?

1. **테스트 용이**: 순수 함수는 테스트하기 쉬움
2. **재사용성**: React 외부에서도 사용 가능
3. **예측 가능**: 같은 입력 → 같은 출력
4. **디버깅 용이**: 부작용 없음

### 무상태 함수 예시

```typescript
// ✅ 무상태 함수 (순수 함수)
export async function handleSocialLogin(
  provider: OAuthProvider,
  onSuccess?: (data: OAuthResponse) => void,
  onError?: (error: Error) => void
): Promise<void> {
  try {
    const data = await requestOAuthLogin(provider);
    if (data.loginUrl) redirectToLoginUrl(data.loginUrl, provider);
    else saveOAuthData(data.token, provider, ...);
    onSuccess?.(data);
  } catch (error) {
    onError?.(error);
  }
}

// ❌ 상태를 가진 함수 (안티패턴)
class SocialLoginService {
  private loading = false;
  private error = null;
  
  async login(provider) {
    this.loading = true;
    // ...
  }
}
```

## 🔐 보안 원칙

### Access Token 관리

- **저장 위치**: Zustand 메모리 (localStorage ❌)
- **수명**: 5-15분 (짧게)
- **장점**: XSS 공격으로부터 보호

### Refresh Token 관리

- **저장 위치**: localStorage
- **수명**: 7일
- **용도**: Access Token 갱신

## 📝 사용 예시

### 1. 컴포넌트에서 소셜 로그인

```typescript
import { useSocialLogin } from "@/hooks/page/useSocialLogin";

function LoginButton() {
  const { loginWithKakao, loading, error } = useSocialLogin();
  
  return (
    <button onClick={loginWithKakao} disabled={loading.kakao}>
      {loading.kakao ? "로그인 중..." : "카카오 로그인"}
    </button>
  );
}
```

### 2. 컴포넌트에서 인증 상태 확인

```typescript
import { useAuth } from "@/hooks/dashboard/useAuth";

function Header() {
  const { isLoggedIn, userInfo, logout } = useAuth();
  
  return (
    <div>
      {isLoggedIn ? (
        <>
          <span>{userInfo?.nickname}님</span>
          <button onClick={logout}>로그아웃</button>
        </>
      ) : (
        <button>로그인</button>
      )}
    </div>
  );
}
```

### 3. API 호출 시 Access Token 사용

```typescript
import { getAccessToken } from "@/store/authStore";

async function fetchUserData() {
  const token = getAccessToken();
  
  const response = await fetch("/api/user", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  
  return response.json();
}
```

## 🚀 마이그레이션 가이드

### 기존 코드 → 새 구조

```typescript
// ❌ 기존 (lib/oauth.ts)
import { requestOAuthLogin } from "@/lib/oauth";

// ✅ 새 구조
import { handleSocialLogin } from "@/services/page/pageService";
import { handleLogout } from "@/services/dashboard/dashboardService";
import { saveOAuthData } from "@/services/oauth/[provider]/success/successService";
```

```typescript
// ❌ 기존 (직접 스토어 접근)
const token = useAuthStore.getState().accessToken;

// ✅ 새 구조 (Hook 사용)
import { useAccessToken } from "@/hooks/dashboard/useAuth";
const token = useAccessToken();

// ✅ 또는 (무상태 함수)
import { getAccessToken } from "@/store/authStore";
const token = getAccessToken();
```

## 📚 참고 자료

- [Zustand 공식 문서](https://github.com/pmndrs/zustand)
- [무상태 패턴 가이드](./store/README.md)
- [OAuth 구현 가이드](./OAUTH_IMPLEMENTATION_GUIDE.md)

