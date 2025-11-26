# 카카오 코드 받는 과정

## OAuth 2.0 인가 코드 플로우

### 전체 흐름

```
1. 사용자가 "카카오로 로그인" 버튼 클릭
   ↓
2. 카카오 로그인 URL로 리다이렉트
   https://kauth.kakao.com/oauth/authorize?client_id=...&redirect_uri=...&response_type=code
   ↓
3. 사용자가 카카오에서 로그인
   ↓
4. 카카오가 콜백 URL로 리다이렉트하면서 code 전달
   http://localhost:8080/auth/kakao/callback?code={인가코드}
   ↓
5. Gateway가 code를 받아서 카카오 API로 토큰 요청
   ↓
6. Gateway가 우리 서비스 JWT 발급
   ↓
7. Gateway가 Next.js로 리다이렉트하면서 토큰 전달
   http://localhost:3000/auth/kakao?token={JWT}
```

## 구현 방법

### 방법 1: Gateway가 카카오 로그인 URL 반환 (현재 구조에 맞음)

**백엔드 (Gateway):**
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

**프론트엔드:**
```typescript
const handleKakaoLogin = async () => {
  const response = await fetch(`${apiGatewayUrl}/api/auth/kakao`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
  });

  const data = await response.json();
  
  // 카카오 로그인 URL을 받으면 리다이렉트
  if (data.loginUrl) {
    window.location.href = data.loginUrl;  // 카카오 로그인 페이지로 이동
  }
};
```

### 방법 2: 프론트엔드에서 직접 카카오 로그인 URL 생성

**프론트엔드:**
```typescript
const handleKakaoLogin = () => {
  const kakaoAuthUrl = `https://kauth.kakao.com/oauth/authorize?` +
    `client_id=${KAKAO_REST_API_KEY}&` +
    `redirect_uri=${encodeURIComponent('http://localhost:8080/auth/kakao/callback')}&` +
    `response_type=code`;
  
  window.location.href = kakaoAuthUrl;  // 카카오 로그인 페이지로 이동
};
```

⚠️ **주의**: 이 방법은 카카오 REST API 키가 프론트엔드에 노출됩니다.

## Gateway 콜백 처리

Gateway의 `/auth/kakao/callback` 엔드포인트에서:

```java
@GetMapping("/auth/kakao/callback")
public ResponseEntity<Void> kakaoCallback(@RequestParam String code) {
    // 1. code로 카카오 액세스 토큰 요청
    String kakaoToken = getKakaoToken(code);
    
    // 2. 액세스 토큰으로 사용자 정보 조회
    KakaoUserInfo userInfo = getKakaoUserInfo(kakaoToken);
    
    // 3. 우리 서비스 JWT 발급
    String jwt = jwtService.generateToken(userInfo.getId(), userInfo.getEmail());
    
    // 4. Next.js로 리다이렉트하면서 토큰 전달
    String callbackUrl = "http://localhost:3000/auth/kakao?token=" + jwt;
    return ResponseEntity.status(HttpStatus.FOUND)
        .location(URI.create(callbackUrl))
        .build();
}
```

## 현재 구조에 맞는 구현

현재 구조는 "Gateway에서만 카카오 처리, Next.js는 토큰만 받음"이므로:

1. **프론트엔드**: Gateway에 요청 → `loginUrl` 받음 → 카카오 로그인 페이지로 리다이렉트
2. **카카오**: 로그인 완료 → Gateway 콜백으로 code 전달
3. **Gateway**: code 처리 → JWT 발급 → Next.js로 리다이렉트
4. **Next.js**: 토큰 받아서 저장

이 흐름이 가장 적합합니다.

## ⚠️ 중요: code가 null인 이유와 해결

### 첫 번째 요청 (POST /api/auth/kakao)
- **code가 null인 이유**: 프론트엔드가 아직 카카오 로그인을 하지 않았기 때문
- **이것은 정상입니다!** code를 받으려면 먼저 카카오 로그인을 해야 합니다.

### 두 번째 요청 (GET /auth/kakao/callback)
- **code가 있는 이유**: 카카오가 로그인 완료 후 code와 함께 콜백을 호출
- **여기서 code를 받아서 처리합니다!**

### 전체 플로우 요약

```
1. POST /api/auth/kakao (code 없음) 
   → Gateway가 loginUrl 반환
   
2. 카카오 로그인 페이지로 리다이렉트
   → 사용자가 카카오에서 로그인
   
3. GET /auth/kakao/callback?code={인가코드} (code 있음!)
   → 카카오가 code와 함께 콜백 호출
   → Gateway가 code로 카카오 API 호출
   → Gateway가 JWT 발급
   → Next.js로 리다이렉트
```

**결론**: 첫 번째 요청에서 code가 null인 것은 정상입니다. 
카카오가 콜백으로 code를 전달하므로, 최종적으로는 code가 Gateway에 전달됩니다!

