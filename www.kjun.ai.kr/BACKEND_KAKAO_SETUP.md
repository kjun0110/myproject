# 백엔드 카카오 로그인 설정 가이드

## 환경 변수 설정

```properties
KAKAO_REDIRECT_URI=http://localhost:8080/auth/kakao/callback
```

## 필수 엔드포인트

### 1. 카카오 로그인 URL 반환 엔드포인트

**URL**: `POST /api/auth/kakao/login`

**요청**:
```json
{}
```

**응답**:
```json
{
  "loginUrl": "https://kauth.kakao.com/oauth/authorize?client_id=...&redirect_uri=http://localhost:8080/auth/kakao/callback&response_type=code"
}
```

**구현 예시**:
```java
@PostMapping("/api/auth/kakao/login")
public ResponseEntity<Map<String, Object>> getKakaoLoginUrl() {
    String kakaoAuthUrl = "https://kauth.kakao.com/oauth/authorize?" +
        "client_id=" + kakaoRestApiKey +
        "&redirect_uri=" + URLEncoder.encode("http://localhost:8080/auth/kakao/callback", "UTF-8") +
        "&response_type=code";
    
    Map<String, Object> response = new HashMap<>();
    response.put("loginUrl", kakaoAuthUrl);
    return ResponseEntity.ok(response);
}
```

---

### 2. 카카오 콜백 처리 엔드포인트 (중요!)

**URL**: `GET /auth/kakao/callback`

**요청**: 카카오가 자동으로 리다이렉트
```
GET /auth/kakao/callback?code={인가코드}
```

**응답**: Next.js로 리다이렉트
```
HTTP 302 Found
Location: http://localhost:3000/auth/kakao/success?token={JWT}&id={id}&email={email}&nickname={nickname}
```

**구현 예시**:
```java
@GetMapping("/auth/kakao/callback")
public ResponseEntity<Void> kakaoCallback(@RequestParam String code) {
    try {
        // 1. code로 카카오 액세스 토큰 요청
        String kakaoToken = getKakaoToken(code);
        
        // 2. 액세스 토큰으로 사용자 정보 조회
        KakaoUserInfo userInfo = getKakaoUserInfo(kakaoToken);
        
        // 3. 우리 서비스 JWT 발급
        String jwt = jwtService.generateToken(userInfo.getId(), userInfo.getEmail());
        
        // 4. Next.js로 리다이렉트하면서 토큰 및 사용자 정보 전달
        String callbackUrl = "http://localhost:3000/auth/kakao/success" +
            "?token=" + jwt +
            "&id=" + userInfo.getId() +
            "&email=" + URLEncoder.encode(userInfo.getEmail(), "UTF-8") +
            "&nickname=" + URLEncoder.encode(userInfo.getNickname(), "UTF-8");
        
        return ResponseEntity.status(HttpStatus.FOUND)  // HTTP 302
            .location(URI.create(callbackUrl))
            .build();
    } catch (Exception e) {
        // 에러 처리
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
    }
}
```

---

## 전체 플로우

```
1. 프론트엔드 → POST /api/auth/kakao/login
   → Gateway가 loginUrl 반환

2. 프론트엔드 → 카카오 로그인 페이지로 리다이렉트
   → 사용자가 카카오에서 로그인

3. 카카오 → GET /auth/kakao/callback?code={인가코드}
   → Gateway가 code 처리
   → Gateway가 JWT 발급
   → Gateway가 Next.js로 리다이렉트

4. Next.js → /auth/kakao/success?token=...&id=...&email=...&nickname=...
   → 토큰 저장
   → 대시보드로 이동
```

---

## 중요 사항

1. **리다이렉트 URI**: 반드시 `http://localhost:8080/auth/kakao/callback`로 설정
2. **카카오 개발자 콘솔**: 리다이렉트 URI를 등록해야 함
3. **CORS 설정**: `http://localhost:3000`에서 오는 요청 허용
4. **에러 처리**: 콜백 엔드포인트에서 에러 발생 시 적절한 에러 페이지로 리다이렉트

---

## 카카오 개발자 콘솔 설정

1. [카카오 개발자 콘솔](https://developers.kakao.com/) 접속
2. 내 애플리케이션 선택
3. 플랫폼 설정 → Web 플랫폼 등록
4. Redirect URI 등록: `http://localhost:8080/auth/kakao/callback`

---

## 테스트 체크리스트

- [ ] `POST /api/auth/kakao/login` 엔드포인트 구현
- [ ] `GET /auth/kakao/callback` 엔드포인트 구현
- [ ] 카카오 개발자 콘솔에 리다이렉트 URI 등록
- [ ] 환경 변수 `KAKAO_REDIRECT_URI` 설정
- [ ] CORS 설정 확인
- [ ] JWT 발급 로직 구현
- [ ] 사용자 정보 조회 로직 구현

