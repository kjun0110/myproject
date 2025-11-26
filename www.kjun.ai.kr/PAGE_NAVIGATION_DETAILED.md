# 페이지 이동 방식 상세 설명

## 카카오 로그인 플로우에서 사용되는 페이지 이동 방식

카카오 로그인 플로우에서는 **3가지 다른 방식**의 페이지 이동이 사용됩니다:

1. **`window.location.href`** - 전체 페이지 리다이렉트 (서버 사이드)
2. **HTTP 302 Redirect** - 서버에서 브라우저로 리다이렉트
3. **`router.push()`** - 클라이언트 사이드 라우팅 (SPA 방식)

---

## 1단계: 프론트엔드 → 카카오 로그인 페이지

### 사용 방식: `window.location.href`

**위치**: `app/page.tsx` - `handleKakaoLogin` 함수

```typescript
if (data.loginUrl) {
    console.log("카카오 로그인 URL로 리다이렉트:", data.loginUrl);
    setIsLoading(false);
    // 카카오 로그인 페이지로 리다이렉트
    window.location.href = data.loginUrl;
    return;
}
```

### 동작 방식

1. **전체 페이지 리로드**
   - 브라우저가 현재 페이지를 완전히 새로고침합니다
   - Next.js 앱의 상태가 모두 초기화됩니다
   - React 컴포넌트가 언마운트되고 새 페이지가 로드됩니다

2. **서버 요청**
   - 브라우저가 새로운 URL로 HTTP GET 요청을 보냅니다
   - 서버(카카오)가 HTML 페이지를 반환합니다
   - 브라우저가 해당 페이지를 렌더링합니다

3. **주소창 변경**
   - 브라우저 주소창이 `https://kauth.kakao.com/oauth/authorize?...`로 변경됩니다
   - 브라우저 히스토리에 새로운 항목이 추가됩니다

### 왜 이 방식을 사용하나요?

- **외부 도메인으로 이동**: 카카오는 완전히 다른 도메인(`kauth.kakao.com`)이므로 전체 페이지 리로드가 필요합니다
- **OAuth 2.0 표준**: OAuth 2.0 플로우는 브라우저 리다이렉트를 사용합니다
- **보안**: 외부 서비스로 이동할 때는 전체 페이지 리로드가 안전합니다

### 특징

- ✅ 외부 도메인으로 이동 가능
- ✅ 브라우저 히스토리 관리
- ❌ Next.js 상태 초기화 (React 상태 손실)
- ❌ 느림 (전체 페이지 리로드)

---

## 2단계: 카카오 → Gateway 콜백

### 사용 방식: HTTP 302 Redirect

**위치**: 카카오 서버 → Gateway

```
HTTP/1.1 302 Found
Location: http://localhost:8080/auth/kakao/callback?code={인가코드}
```

### 동작 방식

1. **카카오 서버가 HTTP 302 응답**
   - 카카오가 로그인 완료 후 HTTP 302 (Found) 상태 코드를 반환합니다
   - `Location` 헤더에 리다이렉트할 URL을 포함합니다

2. **브라우저가 자동 리다이렉트**
   - 브라우저가 `Location` 헤더를 읽고 자동으로 해당 URL로 이동합니다
   - 사용자 개입 없이 자동으로 처리됩니다

3. **Gateway 콜백 엔드포인트 호출**
   - 브라우저가 `GET /auth/kakao/callback?code=...`를 요청합니다
   - Gateway가 이 요청을 처리합니다

### 왜 이 방식을 사용하나요?

- **OAuth 2.0 표준**: OAuth 2.0은 HTTP 리다이렉트를 사용합니다
- **자동 처리**: 사용자가 추가 작업을 할 필요가 없습니다
- **보안**: 인가 코드가 URL 파라미터로 전달되지만, HTTPS를 사용하면 안전합니다

### 특징

- ✅ 자동 처리 (사용자 개입 불필요)
- ✅ OAuth 2.0 표준 준수
- ✅ 브라우저가 자동으로 처리

---

## 3단계: Gateway → Next.js 성공 페이지

### 사용 방식: HTTP 302 Redirect

**위치**: Gateway - `KakaoController.java`

```java
@GetMapping("/auth/kakao/callback")
public ResponseEntity<Void> kakaoCallback(@RequestParam String code) {
    // ... code 처리 및 JWT 발급 ...
    
    // Next.js로 리다이렉트하면서 토큰 전달
    String callbackUrl = "http://localhost:3000/auth/kakao/success?token=" + jwt;
    return ResponseEntity.status(HttpStatus.FOUND)  // HTTP 302
        .location(URI.create(callbackUrl))
        .build();
}
```

### 동작 방식

1. **Gateway가 HTTP 302 응답**
   - Gateway가 JWT 발급 후 HTTP 302 상태 코드를 반환합니다
   - `Location` 헤더에 Next.js 성공 페이지 URL을 포함합니다
   - URL에 JWT 토큰을 쿼리 파라미터로 포함합니다

2. **브라우저가 자동 리다이렉트**
   - 브라우저가 `Location` 헤더를 읽고 자동으로 Next.js로 이동합니다
   - URL: `http://localhost:3000/auth/kakao/success?token=eyJhbGci...`

3. **Next.js 앱이 로드**
   - 브라우저가 Next.js 앱을 요청합니다
   - Next.js가 `/auth/kakao/success` 페이지를 렌더링합니다

### 왜 이 방식을 사용하나요?

- **도메인 간 이동**: Gateway(`localhost:8080`)에서 Next.js(`localhost:3000`)로 이동하므로 HTTP 리다이렉트가 필요합니다
- **토큰 전달**: JWT를 URL 쿼리 파라미터로 전달합니다
- **자동 처리**: 사용자 개입 없이 자동으로 처리됩니다

### 특징

- ✅ 도메인 간 이동 가능
- ✅ 자동 처리
- ⚠️ 토큰이 URL에 노출 (HTTPS 사용 시 안전)

---

## 4단계: Next.js 성공 페이지 → 대시보드

### 사용 방식: `router.push()` (클라이언트 사이드 라우팅)

**위치**: `app/auth/kakao/success/page.tsx`

```typescript
useEffect(() => {
    const token = searchParams.get("token");

    if (token) {
        // 토큰 저장
        localStorage.setItem("access_token", token);
        localStorage.setItem("login_provider", "kakao");

        // 대시보드로 이동
        router.push("/dashboard");
    }
}, [searchParams, router]);
```

### 동작 방식

1. **클라이언트 사이드 라우팅**
   - `router.push()`는 Next.js의 클라이언트 사이드 라우터를 사용합니다
   - **전체 페이지 리로드 없이** URL만 변경합니다
   - React 컴포넌트가 언마운트/마운트되지만, Next.js 앱은 유지됩니다

2. **상태 유지**
   - Next.js 앱의 상태가 유지됩니다
   - React 컴포넌트 트리가 유지됩니다
   - JavaScript 컨텍스트가 유지됩니다

3. **빠른 전환**
   - 서버 요청 없이 클라이언트에서만 처리됩니다
   - 필요한 페이지만 로드합니다 (코드 스플리팅)

### 동작 순서

```
1. useEffect 실행
   ↓
2. URL에서 token 추출
   ↓
3. localStorage에 토큰 저장
   ↓
4. router.push("/dashboard") 호출
   ↓
5. Next.js가 /dashboard 페이지 로드 (서버 요청 없이)
   ↓
6. Dashboard 컴포넌트 렌더링
   ↓
7. 브라우저 주소창이 /dashboard로 변경
```

### 왜 이 방식을 사용하나요?

- **같은 도메인**: Next.js 앱 내에서 이동하므로 클라이언트 사이드 라우팅이 가능합니다
- **빠름**: 전체 페이지 리로드 없이 빠르게 전환됩니다
- **상태 유지**: Next.js 앱의 상태가 유지됩니다
- **SPA 경험**: 단일 페이지 애플리케이션(SPA)처럼 부드러운 전환을 제공합니다

### 특징

- ✅ 빠름 (전체 페이지 리로드 없음)
- ✅ 상태 유지
- ✅ 부드러운 전환 (SPA 경험)
- ❌ 같은 도메인 내에서만 가능

---

## 전체 플로우 요약

```
1. 프론트엔드 (Next.js)
   window.location.href = "https://kauth.kakao.com/..."
   → 전체 페이지 리로드
   → 카카오 로그인 페이지로 이동

2. 카카오 서버
   HTTP 302 Redirect
   Location: http://localhost:8080/auth/kakao/callback?code=...
   → 브라우저가 자동 리다이렉트
   → Gateway 콜백으로 이동

3. Gateway
   HTTP 302 Redirect
   Location: http://localhost:3000/auth/kakao/success?token=...
   → 브라우저가 자동 리다이렉트
   → Next.js 성공 페이지로 이동

4. Next.js 성공 페이지
   router.push("/dashboard")
   → 클라이언트 사이드 라우팅
   → 대시보드로 이동 (전체 페이지 리로드 없음)
```

---

## 각 방식의 비교

| 방식 | 사용 시점 | 페이지 리로드 | 상태 유지 | 속도 | 도메인 간 이동 |
|------|----------|--------------|----------|------|---------------|
| `window.location.href` | 외부 도메인으로 이동 | ✅ 전체 리로드 | ❌ 초기화 | 느림 | ✅ 가능 |
| HTTP 302 Redirect | 서버에서 리다이렉트 | ✅ 전체 리로드 | ❌ 초기화 | 보통 | ✅ 가능 |
| `router.push()` | 같은 앱 내 이동 | ❌ 리로드 없음 | ✅ 유지 | 빠름 | ❌ 불가능 |

---

## 실제 사용자 경험

1. **사용자가 버튼 클릭**
   - 프론트엔드가 카카오 로그인 페이지로 이동 (전체 페이지 리로드)

2. **카카오 로그인 완료**
   - 카카오가 Gateway로 자동 리다이렉트 (사용자는 거의 느끼지 못함)

3. **Gateway 처리**
   - Gateway가 JWT 발급 후 Next.js로 자동 리다이렉트 (사용자는 거의 느끼지 못함)

4. **Next.js 성공 페이지**
   - 토큰 저장 후 대시보드로 이동 (빠른 전환, 사용자는 거의 느끼지 못함)

**결과**: 사용자는 버튼 클릭 → 대시보드 도달까지 부드러운 경험을 느낍니다.


