# 백엔드 개발자를 위한 프론트엔드 정보

## 현재 프론트엔드 상황

### 1. 요청 형식

**프론트엔드가 보내는 요청:**
```
POST http://localhost:8080/api/auth/kakao
Content-Type: application/json

Body: {}  // 빈 객체 (code 없음)
```

### 2. 문제점

- ❌ **code가 없음**: 프론트엔드에서 카카오 인가 코드를 받지 않음
- ❌ **직접 API 호출**: 카카오 로그인 URL로 리다이렉트하지 않고 바로 백엔드 API 호출
- ❌ **OAuth 2.0 플로우 미준수**: 표준 OAuth 2.0 인가 코드 플로우를 따르지 않음

## 해결 방법 옵션

### 옵션 1: 백엔드에서 code 없이 처리 (테스트용 - 권장)

백엔드에서 `code`가 없을 때 테스트용 더미 데이터로 처리:

```java
@PostMapping
public ResponseEntity<Map<String, Object>> kakaoLogin(
        @RequestBody(required = false) Map<String, String> request) {
    
    String code = request != null ? request.get("code") : null;
    
    System.out.println("요청 코드: " + code);
    
    // code가 없으면 테스트용 더미 응답
    if (code == null || code.isEmpty()) {
        System.out.println("⚠️ code가 없음 - 테스트 모드로 처리");
        
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("token", "mock_jwt_token_" + System.currentTimeMillis());
        
        Map<String, Object> user = new HashMap<>();
        user.put("id", 123456L);
        user.put("email", "test@example.com");
        user.put("nickname", "테스트 사용자");
        response.put("user", user);
        
        return ResponseEntity.ok(response);
    }
    
    // code가 있으면 실제 카카오 API 호출
    // ... 기존 로직
}
```

### 옵션 2: 백엔드에서 카카오 로그인 URL 반환

백엔드가 카카오 로그인 URL을 반환하고, 프론트엔드에서 리다이렉트:

**백엔드 응답:**
```json
{
  "loginUrl": "https://kauth.kakao.com/oauth/authorize?client_id=...&redirect_uri=..."
}
```

### 옵션 3: 프론트엔드에서 카카오 로그인 URL로 직접 리다이렉트

프론트엔드에서 카카오 로그인 URL을 직접 생성하여 리다이렉트 (하지만 카카오 키가 프론트엔드에 있어야 함)

## 현재 프론트엔드 요청 정보

### 요청 URL
```
POST http://localhost:8080/api/auth/kakao
```

### 요청 헤더
```
Content-Type: application/json
```

### 요청 Body
```json
{}
```

### 기대하는 응답 형식
```json
{
  "success": true,
  "token": "jwt_token_here",
  "user": {
    "id": 123456,
    "email": "test@example.com",
    "nickname": "테스트 사용자"
  }
}
```

## 권장 해결 방법

**가장 간단한 방법: 옵션 1 (테스트용 더미 응답)**

백엔드에서 `code`가 `null`이거나 없을 때 테스트용 더미 응답을 반환하도록 수정하면, 프론트엔드 코드 변경 없이 바로 동작합니다.

나중에 실제 카카오 로그인을 구현할 때는 옵션 2를 사용하면 됩니다.
