# 배포 전 확인 체크리스트

## 📋 배포 전 필수 확인 사항

### 1. 환경변수 설정 확인

#### 🔵 Vercel (프론트엔드) 환경변수
Vercel 대시보드 → 프로젝트 → Settings → Environment Variables

필수 환경변수:
- ✅ `NEXT_PUBLIC_BACKEND_URL` = `https://api.kjun.ai.kr` (포트 없이!)
  - ❌ 잘못된 예: `https://api.kjun.ai.kr:8080`
  - ✅ 올바른 예: `https://api.kjun.ai.kr`

#### 🔴 EC2 (백엔드) 환경변수
EC2 인스턴스의 `/home/ubuntu/api/.env` 파일 확인

필수 환경변수:
```bash
# Redis (Upstash)
UPSTASH_REDIS_HOST=your_upstash_redis_host
UPSTASH_REDIS_PORT=6379
UPSTASH_REDIS_PASSWORD=your_upstash_redis_password

# Neon PostgreSQL
NEON_DB_HOST=your_neon_db_host
NEON_DB_NAME=your_neon_db_name
NEON_DB_USER=your_neon_db_user
NEON_DB_PASSWORD=your_neon_db_password

# JWT 설정
JWT_SECRET=your_jwt_secret_key (최소 256비트 권장)
JWT_EXPIRATION=900000  # 15분 (밀리초)
JWT_REFRESH_EXPIRATION=604800000  # 7일 (밀리초)

# OAuth - 카카오
KAKAO_REST_API_KEY=your_kakao_rest_api_key
KAKAO_REDIRECT_URI=https://api.kjun.ai.kr/oauth/kakao/callback

# OAuth - 네이버
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret
NAVER_REDIRECT_URI=https://api.kjun.ai.kr/oauth/naver/callback

# OAuth - 구글
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=https://api.kjun.ai.kr/oauth/google/callback

# 프론트엔드 콜백 URL
FRONT_LOGIN_CALLBACK_URL=https://www.kjun.ai.kr
```

### 2. CORS 설정 확인

#### 백엔드 CORS 설정
`api.kjun.ai.kr/src/main/java/kr/ai/kjun/api/config/CorsConfig.java`

✅ 확인 사항:
- `https://www.kjun.ai.kr` 포함되어 있는지
- `https://kjun.ai.kr` 포함되어 있는지
- `allowCredentials: true` 설정되어 있는지

### 3. OAuth 리다이렉트 URI 확인

#### 카카오 개발자 콘솔
- [카카오 개발자 콘솔](https://developers.kakao.com/)
- 애플리케이션 → 플랫폼 → Web 플랫폼 등록
- 제품 설정 → 카카오 로그인 → Redirect URI 등록:
  - ✅ `https://api.kjun.ai.kr/oauth/kakao/callback`

#### 네이버 개발자 콘솔
- [네이버 개발자 콘솔](https://developers.naver.com/)
- 내 애플리케이션 → API 설정 → Callback URL 등록:
  - ✅ `https://api.kjun.ai.kr/oauth/naver/callback`

#### 구글 클라우드 콘솔
- [구글 클라우드 콘솔](https://console.cloud.google.com/)
- APIs & Services → Credentials → OAuth 2.0 Client IDs
- Authorized redirect URIs 등록:
  - ✅ `https://api.kjun.ai.kr/oauth/google/callback`

### 4. 데이터베이스 연결 확인

#### Neon PostgreSQL
- ✅ `refresh_tokens` 테이블 존재 확인
- ✅ 테이블 스키마 확인:
  ```sql
  CREATE TABLE refresh_tokens (
      id BIGSERIAL PRIMARY KEY,
      user_id BIGINT NOT NULL UNIQUE,
      token VARCHAR(500) NOT NULL UNIQUE,
      expires_at TIMESTAMP NOT NULL,
      created_at TIMESTAMP NOT NULL,
      updated_at TIMESTAMP
  );
  ```

#### Upstash Redis
- ✅ Redis 연결 테스트
- ✅ `auth:access:{userId}` 키 패턴으로 저장되는지 확인

### 5. API 엔드포인트 확인

#### 백엔드 엔드포인트
- ✅ `POST /oauth/kakao/login` - 카카오 로그인 URL 반환
- ✅ `GET /oauth/kakao/callback` - 카카오 콜백 처리
- ✅ `POST /oauth/naver/login` - 네이버 로그인 URL 반환
- ✅ `GET /oauth/naver/callback` - 네이버 콜백 처리
- ✅ `POST /oauth/google/login` - 구글 로그인 URL 반환
- ✅ `GET /oauth/google/callback` - 구글 콜백 처리
- ✅ `POST /oauth/logout` - 로그아웃 (토큰 삭제)
- ✅ `POST /oauth/refresh` - Access Token 갱신

#### 프론트엔드 API Route
- ✅ `POST /api/auth/set-refresh-token` - Refresh Token 쿠키 설정
- ✅ `DELETE /api/auth/set-refresh-token` - Refresh Token 쿠키 삭제

### 6. 코드 변경사항 확인

#### 최근 변경된 파일들
- ✅ `RefreshTokenService.java` - 하드코딩 제거, application.yaml에서 읽기
- ✅ `OAuthController.java` - 로그아웃 시 모든 저장소에서 토큰 삭제
- ✅ `dashboardService.ts` - 백엔드 로그아웃 API 호출 추가
- ✅ `oauthApi.ts` - logoutApi 함수 수정 (userId, accessToken 전달)
- ✅ `application.yaml` - Access Token 만료시간 15분으로 변경

### 7. 배포 순서

#### 1단계: 백엔드 배포 (EC2)
```bash
# GitHub Actions를 통해 자동 배포되거나
# 수동 배포 시:
cd api.kjun.ai.kr
./mvnw clean package
docker build -t kjun0110/api.kjun.ai.kr:v1 .
docker push kjun0110/api.kjun.ai.kr:v1
# EC2에서
docker pull kjun0110/api.kjun.ai.kr:v1
docker-compose up -d
```

#### 2단계: 프론트엔드 배포 (Vercel)
```bash
# Vercel은 자동 배포되거나
# 수동 배포 시:
cd www.kjun.ai.kr
vercel --prod
```

### 8. 배포 후 테스트 체크리스트

#### 로그인 테스트
- [ ] 카카오 로그인 성공
- [ ] 네이버 로그인 성공
- [ ] 구글 로그인 성공
- [ ] 로그인 후 Access Token이 Zustand 메모리에 저장되는지 확인
- [ ] 로그인 후 Refresh Token이 HttpOnly 쿠키에 저장되는지 확인
- [ ] 로그인 후 Access Token이 Upstash Redis에 저장되는지 확인
- [ ] 로그인 후 Refresh Token이 Neon PostgreSQL에 저장되는지 확인

#### 로그아웃 테스트
- [ ] 로그아웃 버튼 클릭
- [ ] Zustand 메모리에서 Access Token 삭제 확인
- [ ] HttpOnly 쿠키에서 Refresh Token 삭제 확인
- [ ] Upstash Redis에서 Access Token 삭제 확인
- [ ] Neon PostgreSQL에서 Refresh Token 삭제 확인
- [ ] localStorage에서 UserInfo, LoginProvider 삭제 확인

#### 토큰 만료 시간 확인
- [ ] Access Token 만료 시간: 15분
- [ ] Refresh Token 만료 시간: 7일

### 9. 디버깅 팁

#### 브라우저 개발자 도구
- Network 탭: API 호출 확인
- Application 탭 → Cookies: HttpOnly 쿠키 확인
- Application 탭 → Local Storage: UserInfo, LoginProvider 확인
- Console 탭: 에러 메시지 확인

#### 백엔드 로그 확인
```bash
# EC2에서 Docker 컨테이너 로그 확인
docker logs -f api-service
```

#### Redis 확인
```bash
# Upstash Redis 대시보드에서 확인
# 또는 Redis CLI로:
redis-cli -h your_upstash_host -p 6379 -a your_password
KEYS auth:access:*
```

#### PostgreSQL 확인
```sql
-- Neon PostgreSQL에서 확인
SELECT * FROM refresh_tokens WHERE user_id = YOUR_USER_ID;
```

### 10. 주의사항

⚠️ **중요:**
- Access Token은 15분 후 자동 만료됩니다
- Refresh Token은 7일 후 자동 만료됩니다
- 로그아웃 시 모든 저장소에서 토큰이 삭제되어야 합니다
- 환경변수는 절대 코드에 하드코딩하지 마세요
- JWT_SECRET은 충분히 길고 복잡한 값으로 설정하세요

---

## ✅ 최종 확인

배포 전에 위의 모든 항목을 확인하고 체크하세요!

