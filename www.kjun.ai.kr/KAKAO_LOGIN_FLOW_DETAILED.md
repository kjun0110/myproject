# 카카오 로그인 플로우 상세 설명

## 전체 플로우 개요

```
1. 사용자 클릭 → 프론트엔드 → Gateway (POST /api/auth/kakao)
2. Gateway → 카카오 로그인 URL 반환
3. 프론트엔드 → 카카오 로그인 페이지로 리다이렉트
4. 사용자 → 카카오에서 로그인
5. 카카오 → Gateway 콜백 (GET /auth/kakao/callback?code=...)
6. Gateway → 카카오 API 호출 → JWT 발급
7. Gateway → Next.js로 리다이렉트 (GET /auth/kakao/success?token=...)
8. Next.js → 토큰 저장 → 대시보드로 이동
```

---

## 단계별 상세 설명

### 1단계: 사용자가 "카카오로 로그인" 버튼 클릭

**위치**: `app/page.tsx` - `handleKakaoLogin` 함수

```typescript
const handleKakaoLogin = async () => {
  setIsLoading(true);
  setError(null);

  try {
    // Gateway에 직접 fetch로 연결
    const apiGatewayUrl = "http://localhost:8080";
    const response = await fetch(`${apiGatewayUrl}/api/auth/kakao`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({}),  // 빈 객체 (code 없음)
    });
```

**설명**:
- 사용자가 버튼을 클릭하면 `handleKakaoLogin` 함수가 실행됩니다
- 프론트엔드는 Gateway의 `POST /api/auth/kakao` 엔드포인트로 요청을 보냅니다
- 이 시점에서는 아직 카카오 로그인을 하지 않았으므로 `code`가 없습니다
- 요청 body는 빈 객체 `{}`입니다

---

### 2단계: Gateway가 카카오 로그인 URL 반환

**위치**: Gateway - `KakaoController.java`

```java
@PostMapping("/api/auth/kakao")
public ResponseEntity<Map<String, Object>> kakaoLogin(
        @RequestBody(required = false) Map<String, String> request) {
    
    String code = request != null ? request.get("code") : null;
    
    // code가 없으면 카카오 로그인 URL 반환
    if (code == null || code.isEmpty()) {
        String kakaoAuthUrl = "https://kauth.kakao.com/oauth/authorize?" +
            "client_id=" + kakaoRestApiKey +
            "&redirect_uri=" + URLEncoder.encode("http://localhost:8080/auth/kakao/callback", "UTF-8") +
            "&response_type=code";
        
        Map<String, Object> response = new HashMap<>();
        response.put("loginUrl", kakaoAuthUrl);
        return ResponseEntity.ok(response);
    }
    
    // code가 있으면 실제 카카오 API 호출
    // ... 기존 로직
}
```

**설명**:
- Gateway는 요청 body에서 `code`를 확인합니다
- `code`가 `null`이거나 없으면, 카카오 로그인 URL을 생성합니다
- 카카오 로그인 URL 구성:
  - `client_id`: 카카오 REST API 키
  - `redirect_uri`: 카카오가 로그인 후 돌아올 Gateway 콜백 URL
  - `response_type=code`: 인가 코드 방식 사용
- 응답 형식: `{ "loginUrl": "https://kauth.kakao.com/oauth/authorize?..." }`

---

### 3단계: 프론트엔드가 카카오 로그인 페이지로 리다이렉트

**위치**: `app/page.tsx` - `handleKakaoLogin` 함수 (계속)

```typescript
const data = await response.json();
console.log("Gateway 응답:", data);

// Gateway 응답 형식 처리
// 옵션 1: 카카오 로그인 URL을 반환하는 경우
if (data.loginUrl) {
  console.log("카카오 로그인 URL로 리다이렉트:", data.loginUrl);
  setIsLoading(false);
  // 카카오 로그인 페이지로 리다이렉트
  window.location.href = data.loginUrl;
  return;
}
```

**설명**:
- Gateway로부터 받은 응답에서 `loginUrl`을 확인합니다
- `loginUrl`이 있으면, 브라우저를 카카오 로그인 페이지로 리다이렉트합니다
- `window.location.href`를 사용하여 전체 페이지를 카카오 로그인 페이지로 이동시킵니다
- 이 시점에서 사용자는 카카오 로그인 페이지를 보게 됩니다

---

### 4단계: 사용자가 카카오에서 로그인

**위치**: 카카오 서버 (외부)

**설명**:
- 사용자가 카카오 로그인 페이지에서 이메일/비밀번호를 입력합니다
- 카카오가 사용자 인증을 처리합니다
- 로그인이 성공하면, 카카오는 `redirect_uri`로 리다이렉트합니다
- 리다이렉트 URL에 `code` 파라미터를 포함합니다

---

### 5단계: 카카오가 Gateway 콜백으로 code 전달

**위치**: 카카오 → Gateway - `GET /auth/kakao/callback?code=...`

**설명**:
- 카카오는 사용자를 Gateway의 콜백 URL로 리다이렉트합니다
- URL 형식: `http://localhost:8080/auth/kakao/callback?code={인가코드}`
- `code`는 일회용 인가 코드입니다 (보통 5-10분 유효)

---

### 6단계: Gateway가 code로 카카오 API 호출 및 JWT 발급

**위치**: Gateway - `KakaoController.java` - `kakaoCallback` 메서드

```java
@GetMapping("/auth/kakao/callback")
public ResponseEntity<Void> kakaoCallback(@RequestParam String code) {
    System.out.println("🔴 카카오 콜백 받음, code: " + code);
    
    try {
        // 1. code로 카카오 액세스 토큰 요청
        String kakaoToken = getKakaoToken(code);
        
        // 2. 액세스 토큰으로 사용자 정보 조회
        KakaoUserInfo userInfo = getKakaoUserInfo(kakaoToken);
        
        // 3. 우리 서비스 JWT 발급
        String jwt = jwtService.generateToken(userInfo.getId(), userInfo.getEmail());
        
        // 4. Next.js로 리다이렉트하면서 토큰 전달
        String callbackUrl = "http://localhost:3000/auth/kakao/success?token=" + jwt;
        return ResponseEntity.status(HttpStatus.FOUND)
            .location(URI.create(callbackUrl))
            .build();
    } catch (Exception e) {
        // 에러 처리
    }
}
```

**설명**:
- Gateway는 `code`를 받아서 카카오 API로 액세스 토큰을 요청합니다
- 액세스 토큰으로 카카오 사용자 정보를 조회합니다
- 조회한 사용자 정보로 우리 서비스용 JWT를 발급합니다
- JWT를 포함하여 Next.js로 리다이렉트합니다

---

### 7단계: Gateway가 Next.js로 리다이렉트하면서 토큰 전달

**위치**: Gateway → Next.js - `GET /auth/kakao/success?token=...`

**설명**:
- Gateway는 HTTP 302 리다이렉트를 사용하여 Next.js로 이동시킵니다
- 리다이렉트 URL: `http://localhost:3000/auth/kakao/success?token={JWT}`
- JWT는 URL 쿼리 파라미터로 전달됩니다

---

### 8단계: Next.js가 토큰 받아서 저장하고 대시보드로 이동

**위치**: `app/auth/kakao/success/page.tsx`

```typescript
export default function KakaoAuthSuccess() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // URL에서 token 파라미터 가져오기
        const token = searchParams.get("token");

        if (token) {
            try {
                // 토큰을 localStorage에 저장
                localStorage.setItem("access_token", token);

                // 로그인 제공자 정보 저장
                localStorage.setItem("login_provider", "kakao");

                console.log("카카오 로그인 성공, 토큰 저장 완료");

                setIsLoading(false);

                // 대시보드로 이동
                router.push("/dashboard");
            } catch (err) {
                console.error("토큰 저장 에러:", err);
                setError("토큰 저장에 실패했습니다.");
                setIsLoading(false);
            }
        } else {
            setError("토큰을 받지 못했습니다.");
            setIsLoading(false);
        }
    }, [searchParams, router]);
```

**설명**:
- Next.js는 URL에서 `token` 쿼리 파라미터를 읽습니다
- 토큰을 `localStorage`에 저장합니다 (`access_token`)
- 로그인 제공자 정보도 저장합니다 (`login_provider: "kakao"`)
- 저장이 완료되면 대시보드로 자동 이동합니다

---

## 데이터 흐름 요약

```
1. 프론트엔드 → Gateway
   POST /api/auth/kakao
   Body: {}

2. Gateway → 프론트엔드
   { "loginUrl": "https://kauth.kakao.com/..." }

3. 프론트엔드 → 카카오
   GET https://kauth.kakao.com/oauth/authorize?...

4. 카카오 → Gateway
   GET /auth/kakao/callback?code={인가코드}

5. Gateway → 카카오 API
   POST https://kauth.kakao.com/oauth/token
   Body: { code, client_id, redirect_uri }

6. 카카오 API → Gateway
   { access_token, ... }

7. Gateway → 카카오 API
   GET https://kapi.kakao.com/v2/user/me
   Header: Authorization: Bearer {access_token}

8. 카카오 API → Gateway
   { id, email, nickname, ... }

9. Gateway → Next.js
   HTTP 302 Redirect
   Location: /auth/kakao/success?token={JWT}

10. Next.js → 대시보드
    router.push("/dashboard")
```

---

## 보안 고려사항

1. **JWT 토큰**: URL 쿼리 파라미터로 전달되지만, HTTPS를 사용하면 안전합니다
2. **인가 코드**: 일회용이며 짧은 시간(5-10분)만 유효합니다
3. **카카오 키**: Gateway에만 저장되어 프론트엔드에 노출되지 않습니다
4. **localStorage**: 클라이언트 측 저장소이므로 XSS 공격에 취약할 수 있습니다 (향후 HttpOnly 쿠키로 개선 가능)

---

## 현재 구조의 장점

1. **보안**: 카카오 키가 프론트엔드에 노출되지 않음
2. **중앙화**: 모든 OAuth 로직이 Gateway에 집중됨
3. **단순화**: 프론트엔드는 토큰만 받아서 저장하면 됨
4. **확장성**: 다른 소셜 로그인(네이버, 구글)도 동일한 패턴으로 추가 가능

