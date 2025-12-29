# OAuth 2.0 구현 완전 가이드

이 문서는 현재 프로젝트에서 구현된 OAuth 2.0 인증 시스템의 모든 전략과 과정을 설명합니다.

## 📚 목차

1. [OAuth 2.0 기본 개념](#oauth-20-기본-개념)
2. [아키텍처 개요](#아키텍처-개요)
3. [전체 플로우](#전체-플로우)
4. [프론트엔드 구현](#프론트엔드-구현)
5. [백엔드 구현](#백엔드-구현)
6. [보안 고려사항](#보안-고려사항)
7. [에러 처리](#에러-처리)
8. [테스트 전략](#테스트-전략)
9. [트러블슈팅](#트러블슈팅)

---

## OAuth 2.0 기본 개념

### OAuth 2.0이란?

OAuth 2.0은 **인가(Authorization) 프레임워크**로, 사용자가 제3자 서비스(카카오, 네이버, 구글 등)의 계정 정보를 직접 제공하지 않고도, 해당 서비스를 통해 인증할 수 있게 해주는 프로토콜입니다.

### 주요 용어

- **Resource Owner (리소스 소유자)**: 사용자
- **Client (클라이언트)**: 우리 애플리케이션 (프론트엔드)
- **Authorization Server (인가 서버)**: 카카오/네이버/구글 서버
- **Resource Server (리소스 서버)**: 사용자 정보를 제공하는 서버
- **Authorization Code (인가 코드)**: 임시 코드, 액세스 토큰으로 교환됨
- **Access Token (액세스 토큰)**: API 호출에 사용되는 토큰
- **Redirect URI (리다이렉트 URI)**: 인증 후 돌아올 URL

### OAuth 2.0 플로우 타입

우리 프로젝트는 **Authorization Code Flow**를 사용합니다:

```
1. 사용자가 로그인 버튼 클릭
2. 인가 서버로 리다이렉트 (로그인 페이지)
3. 사용자가 로그인 및 동의
4. 인가 코드를 받아서 돌아옴
5. 인가 코드를 액세스 토큰으로 교환
6. 액세스 토큰으로 사용자 정보 조회
```

---

## 아키텍처 개요

### 시스템 구조

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Next.js   │────────▶│   Gateway   │────────▶│   OAuth     │
│  (Frontend) │         │  (Backend)  │         │   Provider  │
│             │◀────────│             │◀────────│  (Kakao/    │
│             │         │             │         │  Naver/     │
└─────────────┘         └──────────────┘         │  Google)    │
                                                  └─────────────┘
```

### 역할 분담

#### 프론트엔드 (Next.js)
- 로그인 버튼 UI 제공
- OAuth 로그인 URL로 리다이렉트
- 백엔드로부터 받은 JWT 토큰 저장
- 사용자 정보 표시

#### 백엔드 (Gateway)
- OAuth 로그인 URL 생성
- OAuth 콜백 처리
- OAuth Provider API와 통신
- JWT 토큰 발급
- 프론트엔드로 리다이렉트

#### OAuth Provider (카카오/네이버/구글)
- 사용자 인증
- 인가 코드 발급
- 액세스 토큰 발급
- 사용자 정보 제공

---

## 전체 플로우

### 단계별 상세 플로우

```
┌─────────────────────────────────────────────────────────────────┐
│ 1단계: 사용자가 로그인 버튼 클릭                                 │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2단계: 프론트엔드 → 백엔드 API 호출                              │
│ POST /api/auth/{provider}                                       │
│ Body: {}                                                         │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3단계: 백엔드가 OAuth 로그인 URL 생성 및 반환                    │
│ Response: { "loginUrl": "https://..." }                         │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4단계: 프론트엔드가 OAuth 로그인 페이지로 리다이렉트            │
│ window.location.href = loginUrl                                 │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5단계: 사용자가 OAuth Provider에서 로그인 및 동의               │
│ (카카오/네이버/구글 로그인 페이지)                              │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6단계: OAuth Provider가 백엔드 콜백으로 리다이렉트             │
│ GET /auth/{provider}/callback?code={인가코드}&state={state}     │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7단계: 백엔드가 인가 코드를 액세스 토큰으로 교환                │
│ POST {OAuth Provider}/oauth/token                               │
│ Body: { code, client_id, client_secret, redirect_uri }         │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 8단계: 백엔드가 액세스 토큰으로 사용자 정보 조회                │
│ GET {OAuth Provider}/v2/user/me                                │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 9단계: 백엔드가 JWT 토큰 발급                                   │
│ jwtService.generateToken(userId, email)                         │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 10단계: 백엔드가 프론트엔드로 리다이렉트                        │
│ HTTP 302                                                         │
│ Location: /auth/{provider}/success?token={JWT}&id={id}&...      │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 11단계: 프론트엔드가 토큰 저장 및 대시보드로 이동               │
│ localStorage.setItem("access_token", token)                     │
│ router.push("/dashboard")                                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 프론트엔드 구현

### 프로젝트 구조

```
app/
├── page.tsx                    # 로그인 페이지 (메인)
├── lib/
│   └── oauth.ts                 # OAuth 유틸리티 함수
└── oauth/
    └── [provider]/
        └── success/
            └── page.tsx         # OAuth 로그인 성공 페이지
```

### 1. OAuth 유틸리티 (`app/lib/oauth.ts`)

#### 타입 정의

```typescript
export type OAuthProvider = "kakao" | "naver" | "google";

export interface OAuthResponse {
  success?: boolean;
  token?: string;
  loginUrl?: string;
  user?: {
    id?: string;
    email?: string;
    nickname?: string;
  };
  message?: string;
}

export interface OAuthError {
  message: string;
  error?: string;
}
```

#### 핵심 함수들

##### `requestOAuthLogin`: OAuth 로그인 요청

```typescript
export async function requestOAuthLogin(
  provider: OAuthProvider
): Promise<OAuthResponse> {
  const endpoint =
    provider === "kakao"
      ? "/api/oauth/kakao/login"
      : `/api/oauth/${provider}/login`;

  const response = await fetch(`${API_GATEWAY_URL}${endpoint}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({}),
  });

  if (!response.ok) {
    const errorMessage = await parseErrorResponse(response, endpoint);
    throw new Error(errorMessage);
  }

  const data: OAuthResponse = await response.json();
  return data;
}
```

**설명:**
- 백엔드 API에 POST 요청
- provider에 따라 엔드포인트 결정
- 에러 발생 시 상세한 에러 메시지 반환

##### `parseErrorResponse`: 에러 응답 파싱

```typescript
export async function parseErrorResponse(
  response: Response,
  endpoint: string
): Promise<string> {
  if (response.status === 404) {
    return `Gateway API 엔드포인트를 찾을 수 없습니다.\nGateway에 POST ${endpoint} 엔드포인트가 있는지 확인해주세요.`;
  }

  let errorMessage = `HTTP error! status: ${response.status}`;
  try {
    const errorText = await response.text();
    try {
      const errorData: OAuthError = JSON.parse(errorText);
      errorMessage = errorData.message || errorData.error || errorText;
    } catch {
      errorMessage = errorText || errorMessage;
    }
  } catch (e) {
    console.error("🔴 에러 응답 읽기 실패:", e);
  }

  return errorMessage;
}
```

**설명:**
- HTTP 상태 코드에 따른 에러 메시지 생성
- JSON 형식의 에러 응답 파싱
- 404 에러는 특별 처리

##### `saveOAuthData`: OAuth 정보 저장

```typescript
export function saveOAuthData(
  token: string,
  provider: OAuthProvider,
  user?: { id?: string; email?: string; nickname?: string }
): void {
  localStorage.setItem("access_token", token);
  localStorage.setItem("login_provider", provider);

  if (user && Object.keys(user).length > 0) {
    localStorage.setItem("user_info", JSON.stringify(user));
  }
}
```

**설명:**
- JWT 토큰을 localStorage에 저장
- 로그인 제공자 정보 저장
- 사용자 정보가 있으면 함께 저장

##### `redirectToLoginUrl`: OAuth 로그인 페이지로 리다이렉트

```typescript
export function redirectToLoginUrl(
  loginUrl: string,
  provider: OAuthProvider
): void {
  console.log(`${provider} 로그인 URL로 리다이렉트:`, loginUrl);
  window.location.href = loginUrl;
}
```

**설명:**
- 전체 페이지 리다이렉트 (SPA 라우팅 아님)
- OAuth Provider의 로그인 페이지로 이동

##### `handleTokenResponse`: 토큰 응답 처리

```typescript
export function handleTokenResponse(
  data: OAuthResponse,
  provider: OAuthProvider,
  router: { push: (path: string) => void }
): void {
  if (data.success === true && data.token) {
    saveOAuthData(data.token, provider, data.user);
    console.log(`${provider} 로그인 성공:`, data);
    router.push("/dashboard");
  } else {
    throw new Error(data.message || "로그인에 실패했습니다.");
  }
}
```

**설명:**
- 토큰이 포함된 응답 처리
- 인증 정보 저장 후 대시보드로 이동
- 실패 시 에러 발생

### 2. 로그인 페이지 (`app/page.tsx`)

#### 상태 관리

```typescript
const [loading, setLoading] = useState<Record<OAuthProvider, boolean>>({
  kakao: false,
  naver: false,
  google: false,
});
const [error, setError] = useState<string | null>(null);

const isAnyLoading = Object.values(loading).some((isLoading) => isLoading);
```

**설명:**
- 각 provider별 로딩 상태를 객체로 관리
- 하나라도 로딩 중이면 모든 버튼 비활성화

#### 통합 로그인 핸들러

```typescript
const handleSocialLogin = async (provider: OAuthProvider) => {
  setLoading((prev) => ({ ...prev, [provider]: true }));
  setError(null);

  try {
    const data = await requestOAuthLogin(provider);

    // 옵션 1: 로그인 URL을 반환하는 경우
    if (data.loginUrl) {
      setLoading((prev) => ({ ...prev, [provider]: false }));
      redirectToLoginUrl(data.loginUrl, provider);
      return;
    }

    // 옵션 2: 토큰을 직접 반환하는 경우 (테스트용)
    handleTokenResponse(data, provider, router);
    setLoading((prev) => ({ ...prev, [provider]: false }));
  } catch (err) {
    console.error(`${provider} 로그인 에러:`, err);
    setError(
      err instanceof Error
        ? err.message
        : "서버 연결에 실패했습니다. 서버가 실행 중인지 확인해주세요."
    );
  } finally {
    setLoading((prev) => ({ ...prev, [provider]: false }));
  }
};
```

**설명:**
- 모든 provider에 대해 동일한 로직 사용
- `loginUrl`이 있으면 OAuth 페이지로 리다이렉트
- 토큰이 직접 오면 저장 후 대시보드로 이동

#### 개별 핸들러 (래퍼 함수)

```typescript
const handleKakaoLogin = () => handleSocialLogin("kakao");
const handleNaverLogin = () => handleSocialLogin("naver");
const handleGoogleLogin = () => handleSocialLogin("google");
```

**설명:**
- 각 버튼에 연결하기 위한 간단한 래퍼 함수
- 코드 중복 최소화

### 3. 성공 페이지 (`app/oauth/[provider]/success/page.tsx`)

#### 구조

```typescript
export default function KakaoAuthSuccess() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = searchParams.get("token");
    const id = searchParams.get("id");
    const email = searchParams.get("email");
    const nickname = searchParams.get("nickname");

    if (token) {
      try {
        // 토큰 저장
        localStorage.setItem("access_token", token);
        
        // 사용자 정보 저장
        const userInfo: any = {};
        if (id) userInfo.id = id;
        if (email) userInfo.email = email;
        if (nickname) userInfo.nickname = nickname;

        if (Object.keys(userInfo).length > 0) {
          localStorage.setItem("user_info", JSON.stringify(userInfo));
        }

        localStorage.setItem("login_provider", "kakao");

        setIsLoading(false);
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

  // 로딩/에러 UI 렌더링
  // ...
}
```

**설명:**
- URL 쿼리 파라미터에서 토큰 및 사용자 정보 추출
- localStorage에 저장
- 대시보드로 자동 이동
- 에러 발생 시 에러 메시지 표시

---

## 백엔드 구현

### 필수 엔드포인트

#### 1. 로그인 URL 반환 엔드포인트

**카카오:**
```
POST /api/auth/kakao/login
```

**네이버/구글:**
```
POST /api/auth/{provider}
```

**요청:**
```json
{}
```

**응답:**
```json
{
  "loginUrl": "https://kauth.kakao.com/oauth/authorize?client_id=...&redirect_uri=...&response_type=code"
}
```

**Java 구현 예시:**
```java
@PostMapping("/api/auth/kakao/login")
public ResponseEntity<Map<String, Object>> getKakaoLoginUrl() {
    String kakaoAuthUrl = "https://kauth.kakao.com/oauth/authorize?" +
        "client_id=" + kakaoRestApiKey +
        "&redirect_uri=" + URLEncoder.encode(
            "http://localhost:8080/auth/kakao/callback", 
            "UTF-8"
        ) +
        "&response_type=code";
    
    Map<String, Object> response = new HashMap<>();
    response.put("loginUrl", kakaoAuthUrl);
    return ResponseEntity.ok(response);
}
```

**네이버 구현 예시:**
```java
@PostMapping("/api/auth/naver")
public ResponseEntity<Map<String, Object>> getNaverLoginUrl() {
    String state = UUID.randomUUID().toString(); // CSRF 방지
    
    String naverAuthUrl = "https://nid.naver.com/oauth2.0/authorize?" +
        "client_id=" + naverClientId +
        "&redirect_uri=" + URLEncoder.encode(
            "http://localhost:8080/auth/naver/callback", 
            "UTF-8"
        ) +
        "&response_type=code" +
        "&state=" + state;
    
    // state를 세션이나 Redis에 저장 (검증용)
    session.setAttribute("naver_state", state);
    
    Map<String, Object> response = new HashMap<>();
    response.put("loginUrl", naverAuthUrl);
    return ResponseEntity.ok(response);
}
```

**구글 구현 예시:**
```java
@PostMapping("/api/auth/google")
public ResponseEntity<Map<String, Object>> getGoogleLoginUrl() {
    String state = UUID.randomUUID().toString(); // CSRF 방지
    
    String googleAuthUrl = "https://accounts.google.com/o/oauth2/v2/auth?" +
        "client_id=" + googleClientId +
        "&redirect_uri=" + URLEncoder.encode(
            "http://localhost:8080/auth/google/callback", 
            "UTF-8"
        ) +
        "&response_type=code" +
        "&scope=openid email profile" +
        "&state=" + state;
    
    // state를 세션이나 Redis에 저장 (검증용)
    session.setAttribute("google_state", state);
    
    Map<String, Object> response = new HashMap<>();
    response.put("loginUrl", googleAuthUrl);
    return ResponseEntity.ok(response);
}
```

#### 2. 콜백 처리 엔드포인트

**카카오:**
```
GET /auth/kakao/callback?code={인가코드}
```

**네이버:**
```
GET /auth/naver/callback?code={인가코드}&state={state}
```

**구글:**
```
GET /auth/google/callback?code={인가코드}&state={state}
```

**Java 구현 예시 (카카오):**
```java
@GetMapping("/auth/kakao/callback")
public ResponseEntity<Void> kakaoCallback(@RequestParam String code) {
    try {
        // 1. 인가 코드로 액세스 토큰 요청
        String kakaoToken = getKakaoToken(code);
        
        // 2. 액세스 토큰으로 사용자 정보 조회
        KakaoUserInfo userInfo = getKakaoUserInfo(kakaoToken);
        
        // 3. 우리 서비스 JWT 발급
        String jwt = jwtService.generateToken(
            userInfo.getId(), 
            userInfo.getEmail()
        );
        
        // 4. Next.js로 리다이렉트하면서 토큰 및 사용자 정보 전달
        String callbackUrl = "http://localhost:3000/auth/kakao/success" +
            "?token=" + jwt +
            "&id=" + userInfo.getId() +
            "&email=" + URLEncoder.encode(userInfo.getEmail(), "UTF-8") +
            "&nickname=" + URLEncoder.encode(userInfo.getNickname(), "UTF-8");
        
        return ResponseEntity.status(HttpStatus.FOUND)
            .location(URI.create(callbackUrl))
            .build();
    } catch (Exception e) {
        // 에러 처리
        String errorUrl = "http://localhost:3000/auth/kakao/success?error=" +
            URLEncoder.encode(e.getMessage(), "UTF-8");
        return ResponseEntity.status(HttpStatus.FOUND)
            .location(URI.create(errorUrl))
            .build();
    }
}
```

**카카오 액세스 토큰 요청:**
```java
private String getKakaoToken(String code) throws Exception {
    String url = "https://kauth.kakao.com/oauth/token";
    
    HttpHeaders headers = new HttpHeaders();
    headers.setContentType(MediaType.APPLICATION_FORM_URLENCODED);
    
    MultiValueMap<String, String> params = new LinkedMultiValueMap<>();
    params.add("grant_type", "authorization_code");
    params.add("client_id", kakaoRestApiKey);
    params.add("redirect_uri", "http://localhost:8080/auth/kakao/callback");
    params.add("code", code);
    
    HttpEntity<MultiValueMap<String, String>> request = 
        new HttpEntity<>(params, headers);
    
    ResponseEntity<Map> response = restTemplate.postForEntity(
        url, 
        request, 
        Map.class
    );
    
    return (String) response.getBody().get("access_token");
}
```

**카카오 사용자 정보 조회:**
```java
private KakaoUserInfo getKakaoUserInfo(String accessToken) throws Exception {
    String url = "https://kapi.kakao.com/v2/user/me";
    
    HttpHeaders headers = new HttpHeaders();
    headers.set("Authorization", "Bearer " + accessToken);
    
    HttpEntity<String> request = new HttpEntity<>(headers);
    
    ResponseEntity<Map> response = restTemplate.exchange(
        url,
        HttpMethod.GET,
        request,
        Map.class
    );
    
    Map<String, Object> kakaoAccount = 
        (Map<String, Object>) response.getBody().get("kakao_account");
    Map<String, Object> properties = 
        (Map<String, Object>) response.getBody().get("properties");
    
    KakaoUserInfo userInfo = new KakaoUserInfo();
    userInfo.setId((Long) response.getBody().get("id"));
    userInfo.setEmail((String) kakaoAccount.get("email"));
    userInfo.setNickname((String) properties.get("nickname"));
    
    return userInfo;
}
```

**네이버 구현 예시:**
```java
@GetMapping("/auth/naver/callback")
public ResponseEntity<Void> naverCallback(
        @RequestParam String code,
        @RequestParam String state) {
    try {
        // 1. state 검증 (CSRF 방지)
        String savedState = (String) session.getAttribute("naver_state");
        if (!state.equals(savedState)) {
            throw new SecurityException("Invalid state parameter");
        }
        
        // 2. 인가 코드로 액세스 토큰 요청
        String naverToken = getNaverToken(code, state);
        
        // 3. 액세스 토큰으로 사용자 정보 조회
        NaverUserInfo userInfo = getNaverUserInfo(naverToken);
        
        // 4. 우리 서비스 JWT 발급
        String jwt = jwtService.generateToken(
            userInfo.getId(), 
            userInfo.getEmail()
        );
        
        // 5. Next.js로 리다이렉트
        String callbackUrl = "http://localhost:3000/auth/naver/success" +
            "?token=" + jwt +
            "&id=" + userInfo.getId() +
            "&email=" + URLEncoder.encode(userInfo.getEmail(), "UTF-8") +
            "&nickname=" + URLEncoder.encode(userInfo.getNickname(), "UTF-8");
        
        return ResponseEntity.status(HttpStatus.FOUND)
            .location(URI.create(callbackUrl))
            .build();
    } catch (Exception e) {
        // 에러 처리
        String errorUrl = "http://localhost:3000/auth/naver/success?error=" +
            URLEncoder.encode(e.getMessage(), "UTF-8");
        return ResponseEntity.status(HttpStatus.FOUND)
            .location(URI.create(errorUrl))
            .build();
    }
}
```

**구글 구현 예시:**
```java
@GetMapping("/auth/google/callback")
public ResponseEntity<Void> googleCallback(
        @RequestParam String code,
        @RequestParam String state) {
    try {
        // 1. state 검증 (CSRF 방지)
        String savedState = (String) session.getAttribute("google_state");
        if (!state.equals(savedState)) {
            throw new SecurityException("Invalid state parameter");
        }
        
        // 2. 인가 코드로 액세스 토큰 요청
        String googleToken = getGoogleToken(code);
        
        // 3. 액세스 토큰으로 사용자 정보 조회
        GoogleUserInfo userInfo = getGoogleUserInfo(googleToken);
        
        // 4. 우리 서비스 JWT 발급
        String jwt = jwtService.generateToken(
            userInfo.getId(), 
            userInfo.getEmail()
        );
        
        // 5. Next.js로 리다이렉트
        String callbackUrl = "http://localhost:3000/auth/google/success" +
            "?token=" + jwt +
            "&id=" + userInfo.getId() +
            "&email=" + URLEncoder.encode(userInfo.getEmail(), "UTF-8") +
            "&nickname=" + URLEncoder.encode(userInfo.getName(), "UTF-8");
        
        return ResponseEntity.status(HttpStatus.FOUND)
            .location(URI.create(callbackUrl))
            .build();
    } catch (Exception e) {
        // 에러 처리
        String errorUrl = "http://localhost:3000/auth/google/success?error=" +
            URLEncoder.encode(e.getMessage(), "UTF-8");
        return ResponseEntity.status(HttpStatus.FOUND)
            .location(URI.create(errorUrl))
            .build();
    }
}
```

**구글 액세스 토큰 요청:**
```java
private String getGoogleToken(String code) throws Exception {
    String url = "https://oauth2.googleapis.com/token";
    
    HttpHeaders headers = new HttpHeaders();
    headers.setContentType(MediaType.APPLICATION_FORM_URLENCODED);
    
    MultiValueMap<String, String> params = new LinkedMultiValueMap<>();
    params.add("grant_type", "authorization_code");
    params.add("client_id", googleClientId);
    params.add("client_secret", googleClientSecret);
    params.add("redirect_uri", "http://localhost:8080/auth/google/callback");
    params.add("code", code);
    
    HttpEntity<MultiValueMap<String, String>> request = 
        new HttpEntity<>(params, headers);
    
    ResponseEntity<Map> response = restTemplate.postForEntity(
        url, 
        request, 
        Map.class
    );
    
    return (String) response.getBody().get("access_token");
}
```

**구글 사용자 정보 조회:**
```java
private GoogleUserInfo getGoogleUserInfo(String accessToken) throws Exception {
    String url = "https://www.googleapis.com/oauth2/v2/userinfo";
    
    HttpHeaders headers = new HttpHeaders();
    headers.set("Authorization", "Bearer " + accessToken);
    
    HttpEntity<String> request = new HttpEntity<>(headers);
    
    ResponseEntity<Map> response = restTemplate.exchange(
        url,
        HttpMethod.GET,
        request,
        Map.class
    );
    
    GoogleUserInfo userInfo = new GoogleUserInfo();
    userInfo.setId((String) response.getBody().get("id"));
    userInfo.setEmail((String) response.getBody().get("email"));
    userInfo.setName((String) response.getBody().get("name"));
    
    return userInfo;
}
```

---

## 보안 고려사항

### 1. HTTPS 사용

**프로덕션 환경에서는 반드시 HTTPS를 사용해야 합니다.**

- OAuth 인가 코드가 URL에 포함되어 전달됨
- HTTP는 중간자 공격에 취약
- 모든 통신은 HTTPS로 암호화

### 2. State 파라미터 (CSRF 방지)

**네이버/구글은 state 파라미터를 사용합니다:**

```java
// 로그인 URL 생성 시
String state = UUID.randomUUID().toString();
session.setAttribute("naver_state", state);

String naverAuthUrl = "https://nid.naver.com/oauth2.0/authorize?" +
    "..." +
    "&state=" + state;

// 콜백 처리 시
String receivedState = request.getParameter("state");
String savedState = (String) session.getAttribute("naver_state");

if (!receivedState.equals(savedState)) {
    throw new SecurityException("Invalid state parameter");
}
```

**설명:**
- CSRF 공격 방지
- 세션에 저장한 state와 콜백으로 받은 state 비교
- 일치하지 않으면 요청 거부

### 3. Client Secret 보호

**절대 프론트엔드에 노출하지 마세요!**

```typescript
// ❌ 나쁜 예: 프론트엔드에 노출
const CLIENT_SECRET = "my-secret-key";

// ✅ 좋은 예: 백엔드에서만 사용
// 백엔드 환경 변수나 설정 파일에 저장
```

### 4. 토큰 저장

**현재는 localStorage를 사용하지만, 프로덕션에서는 고려사항:**

```typescript
// 현재 방식 (localStorage)
localStorage.setItem("access_token", token);

// 대안 1: httpOnly 쿠키 (XSS 방지)
// 백엔드에서 Set-Cookie 헤더로 설정

// 대안 2: 메모리 저장 (페이지 새로고침 시 사라짐)
// const token = useState<string | null>(null);
```

**장단점:**

| 방식 | 장점 | 단점 |
|------|------|------|
| localStorage | 간단, 지속성 | XSS 공격에 취약 |
| httpOnly Cookie | XSS 방지 | CSRF 공격에 취약 |
| 메모리 | 가장 안전 | 새로고침 시 사라짐 |

### 5. 토큰 만료 처리

```typescript
// JWT 토큰 만료 시간 확인
function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const exp = payload.exp * 1000; // 초를 밀리초로 변환
    return Date.now() >= exp;
  } catch {
    return true;
  }
}

// API 호출 전 토큰 검증
async function apiCall() {
  const token = localStorage.getItem("access_token");
  
  if (!token || isTokenExpired(token)) {
    // 토큰 갱신 또는 재로그인
    router.push("/");
    return;
  }
  
  // API 호출
}
```

### 6. 리다이렉트 URI 검증

**백엔드에서 리다이렉트 URI를 화이트리스트로 관리:**

```java
private static final List<String> ALLOWED_REDIRECT_URIS = Arrays.asList(
    "http://localhost:3000/auth/kakao/success",
    "http://localhost:3000/auth/naver/success",
    "https://yourdomain.com/auth/kakao/success"
);

private void validateRedirectUri(String redirectUri) {
    if (!ALLOWED_REDIRECT_URIS.contains(redirectUri)) {
        throw new SecurityException("Invalid redirect URI");
    }
}
```

---

## 에러 처리

### 프론트엔드 에러 처리

#### 1. 네트워크 에러

```typescript
try {
  const data = await requestOAuthLogin(provider);
} catch (err) {
  if (err instanceof TypeError && err.message.includes("fetch")) {
    setError("네트워크 연결을 확인해주세요.");
  } else {
    setError(err.message);
  }
}
```

#### 2. HTTP 에러 상태 코드

```typescript
if (!response.ok) {
  switch (response.status) {
    case 400:
      throw new Error("잘못된 요청입니다.");
    case 401:
      throw new Error("인증에 실패했습니다.");
    case 404:
      throw new Error("API 엔드포인트를 찾을 수 없습니다.");
    case 500:
      throw new Error("서버 오류가 발생했습니다.");
    default:
      throw new Error(`HTTP error! status: ${response.status}`);
  }
}
```

#### 3. OAuth Provider 에러

```typescript
// OAuth Provider가 에러를 반환하는 경우
// 예: 사용자가 로그인 취소
// http://localhost:8080/auth/kakao/callback?error=access_denied

useEffect(() => {
  const error = searchParams.get("error");
  if (error) {
    switch (error) {
      case "access_denied":
        setError("로그인이 취소되었습니다.");
        break;
      case "invalid_request":
        setError("잘못된 요청입니다.");
        break;
      default:
        setError("로그인에 실패했습니다.");
    }
  }
}, [searchParams]);
```

### 백엔드 에러 처리

#### 1. 인가 코드 교환 실패

```java
try {
    String accessToken = getKakaoToken(code);
} catch (Exception e) {
    // 인가 코드가 만료되었거나 잘못된 경우
    log.error("카카오 토큰 요청 실패: {}", e.getMessage());
    
    String errorUrl = "http://localhost:3000/auth/kakao/success" +
        "?error=" + URLEncoder.encode("인가 코드가 유효하지 않습니다.", "UTF-8");
    
    return ResponseEntity.status(HttpStatus.FOUND)
        .location(URI.create(errorUrl))
        .build();
}
```

#### 2. 사용자 정보 조회 실패

```java
try {
    KakaoUserInfo userInfo = getKakaoUserInfo(accessToken);
} catch (Exception e) {
    log.error("카카오 사용자 정보 조회 실패: {}", e.getMessage());
    
    String errorUrl = "http://localhost:3000/auth/kakao/success" +
        "?error=" + URLEncoder.encode("사용자 정보를 가져올 수 없습니다.", "UTF-8");
    
    return ResponseEntity.status(HttpStatus.FOUND)
        .location(URI.create(errorUrl))
        .build();
}
```

---

## 테스트 전략

### 1. 단위 테스트

#### 프론트엔드 유틸리티 함수 테스트

```typescript
// __tests__/lib/oauth.test.ts
import { saveOAuthData, parseErrorResponse } from '@/lib/oauth';

describe('saveOAuthData', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('토큰과 provider를 저장해야 함', () => {
    saveOAuthData('test-token', 'kakao');
    
    expect(localStorage.getItem('access_token')).toBe('test-token');
    expect(localStorage.getItem('login_provider')).toBe('kakao');
  });

  it('사용자 정보도 함께 저장해야 함', () => {
    const user = { id: '123', email: 'test@example.com' };
    saveOAuthData('test-token', 'kakao', user);
    
    const savedUser = JSON.parse(localStorage.getItem('user_info') || '{}');
    expect(savedUser.id).toBe('123');
    expect(savedUser.email).toBe('test@example.com');
  });
});
```

### 2. 통합 테스트

#### E2E 테스트 (Playwright 예시)

```typescript
// e2e/login.spec.ts
import { test, expect } from '@playwright/test';

test('카카오 로그인 플로우', async ({ page }) => {
  // 1. 로그인 페이지로 이동
  await page.goto('http://localhost:3000');
  
  // 2. 카카오 로그인 버튼 클릭
  await page.click('text=카카오로 로그인');
  
  // 3. OAuth 로그인 페이지로 리다이렉트 확인
  await expect(page).toHaveURL(/kauth\.kakao\.com/);
  
  // 4. 로그인 (실제 카카오 계정 필요)
  // ...
  
  // 5. 콜백으로 돌아와서 성공 페이지 확인
  await expect(page).toHaveURL(/\/auth\/kakao\/success/);
  
  // 6. 대시보드로 리다이렉트 확인
  await expect(page).toHaveURL(/\/dashboard/);
  
  // 7. localStorage에 토큰 저장 확인
  const token = await page.evaluate(() => 
    localStorage.getItem('access_token')
  );
  expect(token).toBeTruthy();
});
```

### 3. 수동 테스트 체크리스트

- [ ] 각 provider 로그인 버튼 클릭 시 로그인 페이지로 이동
- [ ] 로그인 성공 시 토큰이 localStorage에 저장됨
- [ ] 로그인 성공 시 대시보드로 자동 이동
- [ ] 로그인 취소 시 적절한 에러 메시지 표시
- [ ] 네트워크 에러 시 적절한 에러 메시지 표시
- [ ] 여러 provider 간 전환 시 정상 동작
- [ ] 토큰 만료 시 재로그인 유도

---

## 트러블슈팅

### 문제 1: "네이버 인가 코드(code)가 필요합니다" 에러

**원인:**
- 프론트엔드에서 빈 객체 `{}`를 보내는데, 백엔드가 code를 기대함

**해결:**
- 백엔드에서 code가 없을 때 `loginUrl`을 반환하도록 수정

```java
@PostMapping("/api/auth/naver")
public ResponseEntity<Map<String, Object>> naverLogin(
        @RequestBody(required = false) Map<String, String> request) {
    
    String code = request != null ? request.get("code") : null;
    
    // code가 없으면 네이버 로그인 URL 반환
    if (code == null || code.isEmpty()) {
        String naverAuthUrl = "https://nid.naver.com/oauth2.0/authorize?" +
            "client_id=" + naverClientId +
            "&redirect_uri=" + URLEncoder.encode(
                "http://localhost:8080/auth/naver/callback", 
                "UTF-8"
            ) +
            "&response_type=code" +
            "&state=" + generateState();
        
        Map<String, Object> response = new HashMap<>();
        response.put("loginUrl", naverAuthUrl);
        return ResponseEntity.ok(response);
    }
    
    // code가 있으면 실제 네이버 API 호출
    // ...
}
```

### 문제 2: 콜백 엔드포인트 404 에러

**원인:**
- 백엔드에 `/auth/{provider}/callback` 엔드포인트가 없음

**해결:**
- 백엔드에 콜백 엔드포인트 추가

```java
@GetMapping("/auth/naver/callback")
public ResponseEntity<Void> naverCallback(
        @RequestParam String code,
        @RequestParam String state) {
    // 콜백 처리 로직
}
```

### 문제 2-1: 구글 "redirect_uri_mismatch" 에러

**원인:**
- 구글 클라우드 콘솔에 등록된 redirect_uri와 백엔드에서 사용하는 redirect_uri가 일치하지 않음
- 구글은 redirect_uri를 정확히 일치시켜야 함 (대소문자, 슬래시, 포트 번호 등 모두 일치해야 함)

**해결:**
1. **구글 클라우드 콘솔에서 확인:**
   - [Google Cloud Console](https://console.cloud.google.com/) 접속
   - APIs & Services > Credentials > OAuth 2.0 Client IDs 선택
   - 사용 중인 클라이언트 ID 클릭
   - "승인된 리디렉션 URI" 섹션 확인

2. **백엔드 코드에서 사용하는 redirect_uri 확인:**
   ```java
   // 백엔드에서 사용하는 redirect_uri
   String redirectUri = "http://localhost:8080/auth/google/callback";
   ```

3. **구글 클라우드 콘솔에 정확히 동일한 URI 등록:**
   - 승인된 리디렉션 URI에 `http://localhost:8080/auth/google/callback` 추가
   - 프로토콜(http/https), 호스트, 포트, 경로가 모두 일치해야 함
   - 마지막 슬래시(/)도 일치해야 함

4. **주의사항:**
   - `http://localhost:8080/auth/google/callback` ✅
   - `http://localhost:8080/auth/google/callback/` ❌ (슬래시 차이)
   - `https://localhost:8080/auth/google/callback` ❌ (프로토콜 차이)
   - `http://127.0.0.1:8080/auth/google/callback` ❌ (호스트 차이)

5. **프로덕션 환경:**
   - 프로덕션 도메인도 동일하게 등록 필요
   - 예: `https://yourdomain.com/auth/google/callback`

### 문제 3: CORS 에러

**원인:**
- 백엔드가 프론트엔드 도메인을 허용하지 않음

**해결:**
- 백엔드 CORS 설정 추가

```java
@Configuration
public class CorsConfig {
    @Bean
    public WebMvcConfigurer corsConfigurer() {
        return new WebMvcConfigurer() {
            @Override
            public void addCorsMappings(CorsRegistry registry) {
                registry.addMapping("/api/**")
                    .allowedOrigins("http://localhost:3000")
                    .allowedMethods("GET", "POST", "PUT", "DELETE")
                    .allowedHeaders("*")
                    .allowCredentials(true);
            }
        };
    }
}
```

### 문제 4: State 파라미터 불일치

**원인:**
- 세션에 저장한 state와 콜백으로 받은 state가 다름
- 네이버/구글 모두 state 파라미터를 사용하므로 동일한 문제 발생 가능

**해결:**
- 세션 관리 확인 및 state 검증 로직 점검

```java
// state 생성 시 세션에 저장 (네이버)
String state = UUID.randomUUID().toString();
session.setAttribute("naver_state", state);

// state 생성 시 세션에 저장 (구글)
String state = UUID.randomUUID().toString();
session.setAttribute("google_state", state);

// 콜백에서 검증 (네이버/구글 동일)
String receivedState = request.getParameter("state");
String savedState = (String) session.getAttribute("{provider}_state");

if (savedState == null || !receivedState.equals(savedState)) {
    throw new SecurityException("Invalid state parameter");
}
```

### 문제 5: 토큰이 URL에 노출됨

**원인:**
- JWT 토큰이 URL 쿼리 파라미터로 전달됨

**해결:**
- 프로덕션에서는 httpOnly 쿠키 사용 고려
- 또는 POST 요청으로 토큰 전달

```java
// 대안: POST 요청으로 토큰 전달
@PostMapping("/auth/kakao/callback")
public ResponseEntity<String> kakaoCallback(@RequestParam String code) {
    // ... 토큰 발급 ...
    
    // HTML 폼으로 토큰 전달
    String html = "<html><body>" +
        "<form id='tokenForm' method='post' action='http://localhost:3000/auth/kakao/success'>" +
        "<input type='hidden' name='token' value='" + jwt + "'>" +
        "</form>" +
        "<script>document.getElementById('tokenForm').submit();</script>" +
        "</body></html>";
    
    return ResponseEntity.ok()
        .contentType(MediaType.TEXT_HTML)
        .body(html);
}
```

---

## 추가 개선 사항

### 1. 토큰 갱신 (Refresh Token)

```typescript
// 토큰 만료 전 자동 갱신
async function refreshToken() {
  const refreshToken = localStorage.getItem("refresh_token");
  
  const response = await fetch(`${API_GATEWAY_URL}/api/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refreshToken }),
  });
  
  const data = await response.json();
  if (data.token) {
    localStorage.setItem("access_token", data.token);
  }
}
```

### 2. 로그아웃

```typescript
function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("user_info");
  localStorage.removeItem("login_provider");
  
  router.push("/");
}
```

### 3. 인증 상태 확인

```typescript
function isAuthenticated(): boolean {
  const token = localStorage.getItem("access_token");
  if (!token) return false;
  
  // 토큰 만료 확인
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const exp = payload.exp * 1000;
    return Date.now() < exp;
  } catch {
    return false;
  }
}
```

---

## 참고 자료

### 공식 문서

- [OAuth 2.0 RFC 6749](https://tools.ietf.org/html/rfc6749)
- [카카오 로그인 가이드](https://developers.kakao.com/docs/latest/ko/kakaologin/rest-api)
- [네이버 로그인 가이드](https://developers.naver.com/docs/login/overview/)
- [구글 OAuth 2.0 가이드](https://developers.google.com/identity/protocols/oauth2)

### 프로젝트 파일 구조

```
프론트엔드:
- app/page.tsx                    # 로그인 페이지
- lib/oauth.ts                     # OAuth 유틸리티
- app/oauth/[provider]/success/   # 성공 페이지 (kakao, naver, google)

백엔드:
- /api/auth/{provider}            # 로그인 URL 반환 (kakao는 /api/auth/kakao/login)
- /auth/{provider}/callback       # OAuth 콜백 처리 (kakao, naver, google)
```

---

## 요약

이 가이드는 OAuth 2.0 인증 시스템의 전체 구현 과정을 다룹니다:

1. **OAuth 2.0 기본 개념** 이해
2. **프론트엔드와 백엔드 역할** 분담
3. **단계별 플로우** 구현
4. **보안 고려사항** 적용
5. **에러 처리** 및 **테스트 전략**
6. **트러블슈팅** 가이드

이 문서를 참고하여 안전하고 확장 가능한 OAuth 인증 시스템을 구축할 수 있습니다.

