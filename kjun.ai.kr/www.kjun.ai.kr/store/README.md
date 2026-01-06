# Zustand 기반 인증 스토어 (authStore)

## 개요

Access Token을 **메모리(Zustand 스토어)**에만 저장하고, Refresh Token과 사용자 정보는 localStorage에 저장하는 보안 강화 방식입니다.

## 보안 원칙

- **Access Token (5-15분)**: 메모리에만 저장 → XSS 공격으로부터 보호
- **Refresh Token (7일)**: localStorage에 저장 → 페이지 새로고침 후에도 로그인 유지
- **User Info**: localStorage에 저장 → 사용자 정보 표시용

## 사용 방법

### 🎯 무상태 인터페이스 (권장)

React 컴포넌트 외부에서도 사용 가능한 순수 함수 인터페이스입니다.

```typescript
import {
  authLogin,
  authLogout,
  getAccessToken,
  getUserInfo,
  isLoggedIn,
} from "@/store/authStore";

// 로그인
authLogin(accessToken, refreshToken, "kakao", userInfo);

// Access Token 가져오기
const token = getAccessToken();

// 사용자 정보 가져오기
const user = getUserInfo();

// 로그인 여부 확인
const loggedIn = isLoggedIn();

// 로그아웃
authLogout();
```

### 🔧 Zustand Hook (React 컴포넌트 내부)

### 1. 로그인 처리 (무상태 인터페이스)

```typescript
import { authLogin } from "@/store/authStore";

function LoginComponent() {
  const handleLogin = async () => {
    // 백엔드에서 받은 토큰
    const accessToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...";
    const refreshToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...";
    const userInfo = { id: "123", email: "user@example.com", nickname: "홍길동" };

    // 로그인 처리 (Access Token은 메모리, Refresh Token은 localStorage)
    authLogin(accessToken, refreshToken, "kakao", userInfo);
  };

  return <button onClick={handleLogin}>로그인</button>;
}
```

### 2. 로그인 상태 확인

```typescript
import { useAuthStore } from "@/store/authStore";

function Header() {
  // Zustand 스토어에서 로그인 상태 가져오기 (자동 리렌더링)
  const isLoggedIn = useAuthStore((state) => state.isLoggedIn);
  const userInfo = useAuthStore((state) => state.userInfo);

  return (
    <div>
      {isLoggedIn ? (
        <p>환영합니다, {userInfo?.nickname}님!</p>
      ) : (
        <button>로그인</button>
      )}
    </div>
  );
}
```

### 3. Access Token 사용 (API 호출) - 무상태 인터페이스

```typescript
import { getAccessToken } from "@/store/authStore";

async function fetchUserData() {
  // 메모리에서 Access Token 가져오기 (무상태 함수)
  const accessToken = getAccessToken();

  if (!accessToken) {
    console.error("로그인이 필요합니다.");
    return;
  }

  const response = await fetch("https://api.kjun.ai.kr/api/user", {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  return response.json();
}
```

### 4. Access Token 갱신 (무상태 인터페이스)

```typescript
import { refreshAccessToken } from "@/store/authStore";

async function refreshToken() {
  // Refresh Token으로 Access Token 갱신 (무상태 함수)
  const success = await refreshAccessToken();

  if (success) {
    console.log("토큰 갱신 성공");
  } else {
    console.log("토큰 갱신 실패 (로그아웃 처리됨)");
  }
}
```

### 5. 로그아웃 (무상태 인터페이스)

```typescript
import { authLogout } from "@/store/authStore";

function LogoutButton() {
  const handleLogout = () => {
    // 메모리와 localStorage의 모든 정보 삭제 (무상태 함수)
    authLogout();
    console.log("로그아웃 완료");
  };

  return <button onClick={handleLogout}>로그아웃</button>;
}
```

## API

### 무상태 인터페이스 (권장)

React 컴포넌트 외부에서도 사용 가능한 순수 함수들:

- `authLogin(accessToken, refreshToken, provider, userInfo)`: 로그인 처리
- `authLogout()`: 로그아웃 처리
- `getAccessToken()`: Access Token 가져오기
- `getRefreshToken()`: Refresh Token 가져오기
- `getUserInfo()`: 사용자 정보 가져오기
- `getLoginProvider()`: 로그인 제공자 가져오기
- `isLoggedIn()`: 로그인 여부 확인
- `refreshAccessToken()`: Access Token 갱신
- `setAccessToken(token)`: Access Token 설정
- `setRefreshToken(token)`: Refresh Token 설정
- `setUserInfo(userInfo)`: 사용자 정보 설정
- `setLoginProvider(provider)`: 로그인 제공자 설정

### Zustand Hook (React 컴포넌트 내부)

- `useAuthStore((state) => state.accessToken)`: Access Token 구독
- `useAuthStore((state) => state.isLoggedIn)`: 로그인 상태 구독
- `useAuthStore((state) => state.userInfo)`: 사용자 정보 구독

## 보안 이점

1. **XSS 공격 방지**: Access Token이 메모리에만 있어 JavaScript로 탈취 불가
2. **짧은 수명**: Access Token은 5-15분으로 짧게 설정
3. **Refresh Token 분리**: 긴 수명의 Refresh Token은 localStorage에 저장하되, Access Token 갱신 시에만 사용
4. **자동 로그아웃**: Refresh Token 갱신 실패 시 자동 로그아웃

## 주의사항

- 페이지 새로고침 시 Access Token은 사라지므로, Refresh Token으로 재발급 필요
- Refresh Token도 탈취 위험이 있으므로, 백엔드에서 Refresh Token Rotation 구현 권장
- 더 높은 보안을 위해서는 HttpOnly 쿠키 사용 권장

