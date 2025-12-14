# 데이터베이스 연결 전략: Neon & Upstash

## 📋 목차
1. [개요](#개요)
2. [아키텍처 전략](#아키텍처-전략)
3. [Neon (PostgreSQL) 전략](#neon-postgresql-전략)
4. [Upstash (Redis) 전략](#upstash-redis-전략)
5. [환경 변수 설정](#환경-변수-설정)
6. [서비스별 구현 상세](#서비스별-구현-상세)
7. [주의사항 및 베스트 프랙티스](#주의사항-및-베스트-프랙티스)

---

## 개요

이 프로젝트는 **마이크로서비스 아키텍처**를 기반으로 하며, 데이터 저장소는 다음과 같이 분리되어 있습니다:

- **Neon (PostgreSQL)**: 영구 데이터 저장 (사용자 정보, 계정, 권한)
- **Upstash (Redis)**: 임시 데이터 및 세션 관리 (JWT 블랙리스트, Refresh Token, Rate Limit)

### 핵심 원칙

1. **데이터 분리**: 영구 데이터와 임시 데이터를 명확히 구분
2. **서비스 책임 분리**: 각 마이크로서비스는 자신의 역할에 맞는 데이터만 접근
3. **확장성 고려**: 향후 서비스 추가 시에도 동일한 전략 적용 가능

---

## 아키텍처 전략

### 서비스별 데이터베이스 사용 현황

```
┌─────────────────────────────────────────────────────────────┐
│                      Gateway Service                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Upstash Redis 사용:                                  │  │
│  │  - JWT 검증 및 블랙리스트 관리                        │  │
│  │  - Rate Limit (IP 기반)                              │  │
│  │  - 세션 체크                                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌───────▼────────┐  ┌───────▼────────┐
│ OAuth Service  │  │  User Service  │  │   AI Service   │
│                │  │                │  │   (향후)        │
│ Upstash Redis: │  │  Neon DB:      │  │  Upstash Redis: │
│ - Refresh Token│  │  - Users       │  │  - Cache       │
│ - Login Session│  │  - Accounts     │  │  - Job Status  │
│                │  │  - Permissions │  │  - Temp Data    │
└────────────────┘  └────────────────┘  └────────────────┘
```

### 데이터 흐름

1. **OAuth 로그인 흐름**:
   ```
   Frontend → Gateway → OAuth Service → User Service (Neon DB)
                                    ↓
                            Upstash Redis (Refresh Token 저장)
   ```

2. **API 요청 흐름**:
   ```
   Frontend → Gateway (JWT 검증, Rate Limit) → Backend Services
                ↓
         Upstash Redis (블랙리스트 체크)
   ```

---

## Neon (PostgreSQL) 전략

### 사용 서비스
- **User Service** (`userservice`)만 사용

### 저장 데이터
- OAuth 사용자 정보 (email, nickname, profileImageUrl)
- OAuth 제공자 정보 (KAKAO, NAVER, GOOGLE)
- 사용자 권한 (USER, ADMIN)
- 계정 생성/수정 시간

### 환경 변수

`.env` 파일에 다음 변수 설정:
```env
NEON_DB_HOST=your-neon-host.neon.tech
NEON_DB_NAME=neondb
NEON_DB_USER=your-username
NEON_DB_PASSWORD=your-password
```

### 설정 파일

**`userservice/src/main/resources/application.yaml`**:
```yaml
spring:
  datasource:
    url: jdbc:postgresql://${NEON_DB_HOST}/${NEON_DB_NAME}
    username: ${NEON_DB_USER}
    password: ${NEON_DB_PASSWORD}
    driver-class-name: org.postgresql.Driver
  
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: false
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect
        format_sql: true
```

### Docker Compose 설정

**`docker-compose.yaml`**:
```yaml
userservice:
  environment:
    - NEON_DB_HOST=${NEON_DB_HOST}
    - NEON_DB_NAME=${NEON_DB_NAME}
    - NEON_DB_USER=${NEON_DB_USER}
    - NEON_DB_PASSWORD=${NEON_DB_PASSWORD}
```

### 주요 특징

1. **단일 서비스 접근**: User Service만 Neon DB에 접근
2. **JPA 사용**: Spring Data JPA로 영구 데이터 관리
3. **Entity 분리**: `User` Entity와 `UserModel` DTO 분리
4. **Repository 패턴**: `UserRepository`, `UserRepositoryCustom`, `UserRepositoryImpl` 구조

---

## Upstash (Redis) 전략

### 사용 서비스
- **Gateway Service** (`gatewayserver`)
- **OAuth Service** (`oauthservice`)
- **AI Service** (`aiservice`) - 향후 확장 예정

### 서비스별 사용 목적

#### 1. Gateway Service
- **JWT 블랙리스트**: 로그아웃된 Access Token 관리
  - Key 패턴: `auth:blacklist:{jti}`
  - TTL: Access Token 만료 시간까지
- **Rate Limit**: IP 기반 요청 제한
  - Key 패턴: `gateway:ratelimit:{ip}`
- **세션 체크**: 인증된 사용자 세션 확인

#### 2. OAuth Service
- **Refresh Token 저장**: 사용자별 Refresh Token 관리
  - Key 패턴: `auth:refresh:{userId}`
  - TTL: 7일
- **로그인 세션 관리**: OAuth 로그인 세션 정보

#### 3. AI Service (향후)
- **캐시**: ML 모델 결과 캐싱
- **작업 상태**: 비동기 작업 상태 추적
- **임시 데이터**: 처리 중인 데이터 임시 저장

### 환경 변수

`.env` 파일에 다음 변수 설정:
```env
UPSTASH_REDIS_HOST=your-upstash-host.upstash.io
UPSTASH_REDIS_PORT=6379
UPSTASH_REDIS_PASSWORD=your-upstash-password
```

### 설정 파일

#### Gateway Service

**`gateway/src/main/resources/application.yaml`**:
```yaml
spring:
  data:
    redis:
      host: ${UPSTASH_REDIS_HOST}
      port: ${UPSTASH_REDIS_PORT}
      password: ${UPSTASH_REDIS_PASSWORD}
      ssl:
        enabled: true
      timeout: 2000ms
      lettuce:
        pool:
          max-active: 8
          max-idle: 8
          min-idle: 0
```

**`gateway/src/main/java/kr/ai/kjun/api/config/GatewayJwtConfig.java`**:
```java
@Configuration
public class GatewayJwtConfig {
    @Value("${jwt.secret}")
    private String jwtSecret;

    @Bean
    public SecretKey jwtSecretKey() {
        return Keys.hmacShaKeyFor(jwtSecret.getBytes(StandardCharsets.UTF_8));
    }

    @Bean
    public ReactiveStringRedisTemplate reactiveStringRedisTemplate(
            ReactiveRedisConnectionFactory connectionFactory) {
        // Reactive Redis Template 설정 (WebFlux용)
    }
}
```

#### OAuth Service

**`oauthservice/src/main/resources/application.yaml`**:
```yaml
spring:
  data:
    redis:
      host: ${UPSTASH_REDIS_HOST}
      port: ${UPSTASH_REDIS_PORT}
      password: ${UPSTASH_REDIS_PASSWORD}
      ssl:
        enabled: true
      timeout: 2000ms
      lettuce:
        pool:
          max-active: 8
          max-idle: 8
          min-idle: 0
```

**`oauthservice/src/main/java/kr/ai/kjun/api/config/RedisConfig.java`**:
```java
@Configuration
public class RedisConfig {
    @Value("${spring.data.redis.host}")
    private String host;
    
    @Value("${spring.data.redis.port}")
    private int port;
    
    @Value("${spring.data.redis.password}")
    private String password;
    
    @Value("${spring.data.redis.ssl.enabled:false}")
    private boolean ssl;

    @Bean
    public RedisConnectionFactory redisConnectionFactory() {
        RedisStandaloneConfiguration config = new RedisStandaloneConfiguration();
        config.setHostName(host);
        config.setPort(port);
        config.setPassword(password);

        var clientConfigBuilder = LettuceClientConfiguration.builder()
                .commandTimeout(Duration.ofSeconds(2));

        if (ssl) {
            clientConfigBuilder.useSsl();
        }

        return new LettuceConnectionFactory(config, clientConfigBuilder.build());
    }

    @Bean
    public RedisTemplate<String, String> redisTemplate(
            RedisConnectionFactory connectionFactory) {
        RedisTemplate<String, String> template = new RedisTemplate<>();
        template.setConnectionFactory(connectionFactory);
        template.setKeySerializer(new StringRedisSerializer());
        template.setValueSerializer(new StringRedisSerializer());
        template.afterPropertiesSet();
        return template;
    }
}
```

### Docker Compose 설정

**`docker-compose.yaml`**:
```yaml
gatewayserver:
  environment:
    - UPSTASH_REDIS_HOST=${UPSTASH_REDIS_HOST}
    - UPSTASH_REDIS_PORT=${UPSTASH_REDIS_PORT}
    - UPSTASH_REDIS_PASSWORD=${UPSTASH_REDIS_PASSWORD}

oauthservice:
  environment:
    - UPSTASH_REDIS_HOST=${UPSTASH_REDIS_HOST}
    - UPSTASH_REDIS_PORT=${UPSTASH_REDIS_PORT}
    - UPSTASH_REDIS_PASSWORD=${UPSTASH_REDIS_PASSWORD}
```

### Redis Key 네이밍 규칙

| 서비스 | 용도 | Key 패턴 | 예시 |
|--------|------|----------|------|
| Gateway | JWT 블랙리스트 | `auth:blacklist:{jti}` | `auth:blacklist:abc123` |
| Gateway | Rate Limit | `gateway:ratelimit:{ip}` | `gateway:ratelimit:192.168.1.1` |
| OAuth | Refresh Token | `auth:refresh:{userId}` | `auth:refresh:123` |
| AI (향후) | 캐시 | `ai:cache:{key}` | `ai:cache:model:result:123` |
| AI (향후) | 작업 상태 | `ai:job:{jobId}` | `ai:job:456` |

---

## 환경 변수 설정

### `.env` 파일 예시

```env
# Neon Database (PostgreSQL)
NEON_DB_HOST=your-neon-host.neon.tech
NEON_DB_NAME=neondb
NEON_DB_USER=your-username
NEON_DB_PASSWORD=your-password

# Upstash Redis
UPSTASH_REDIS_HOST=your-upstash-host.upstash.io
UPSTASH_REDIS_PORT=6379
UPSTASH_REDIS_PASSWORD=your-upstash-password

# JWT
JWT_SECRET=your-jwt-secret-key
JWT_EXPIRATION=86400000
JWT_REFRESH_EXPIRATION=604800000

# OAuth
KAKAO_REST_API_KEY=your-kakao-key
KAKAO_REDIRECT_URI=http://localhost:8080/oauth/kakao/callback
NAVER_CLIENT_ID=your-naver-id
NAVER_CLIENT_SECRET=your-naver-secret
NAVER_REDIRECT_URI=http://localhost:8080/oauth/naver/callback
GOOGLE_CLIENT_ID=your-google-id
GOOGLE_CLIENT_SECRET=your-google-secret
GOOGLE_REDIRECT_URI=http://localhost:8080/oauth/google/callback

# Frontend
FRONT_LOGIN_CALLBACK_URL=http://localhost:4000

# Service URLs
USER_SERVICE_URL=http://userservice:8092
```

---

## 서비스별 구현 상세

### User Service (Neon DB)

#### 의존성 (`build.gradle`)
```gradle
implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
implementation 'org.postgresql:postgresql'
```

#### Entity 구조
```java
@Entity
@Table(name = "users", uniqueConstraints = {
    @UniqueConstraint(columnNames = { "oauth_provider", "oauth_id" })
})
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, unique = true)
    private String email;
    
    @Column(name = "oauth_provider", nullable = false)
    @Enumerated(EnumType.STRING)
    private OAuthProvider oauthProvider;
    
    @Column(name = "oauth_id", nullable = false)
    private String oauthId;
    
    // ... 기타 필드
}
```

#### Repository 구조
- `UserRepository`: JPA 기본 메서드 + 커스텀 인터페이스
- `UserRepositoryCustom`: 커스텀 메서드 인터페이스
- `UserRepositoryImpl`: 커스텀 메서드 구현 (JPQL/QueryDSL)

### Gateway Service (Upstash Redis)

#### 의존성 (`build.gradle`)
```gradle
implementation 'org.springframework.boot:spring-boot-starter-data-redis-reactive'
implementation 'io.jsonwebtoken:jjwt-api:0.12.3'
runtimeOnly 'io.jsonwebtoken:jjwt-impl:0.12.3'
runtimeOnly 'io.jsonwebtoken:jjwt-jackson:0.12.3'
```

#### 주요 컴포넌트
- `GatewayJwtConfig`: JWT Secret Key 및 Reactive Redis Template 설정
- `JwtAuthenticationFilter`: JWT 검증 및 블랙리스트 체크
- `RateLimitFilter`: IP 기반 Rate Limit

### OAuth Service (Upstash Redis)

#### 의존성 (`build.gradle`)
```gradle
implementation 'org.springframework.boot:spring-boot-starter-data-redis'
```

#### 주요 컴포넌트
- `RedisConfig`: Redis Connection Factory 및 RedisTemplate 설정
- `RefreshTokenService`: Refresh Token 생성, 검증, 삭제
- `TokenBlacklistService`: Access Token 블랙리스트 관리

---

## 주의사항 및 베스트 프랙티스

### 1. SSL 설정
- **Upstash Redis는 SSL 필수**: `spring.data.redis.ssl.enabled: true` 설정 필수
- Spring Boot 3.x에서는 `ssl: true` 대신 `ssl.enabled: true` 사용

### 2. 환경 변수 관리
- `.env` 파일은 루트에 위치
- `.env` 파일은 Git에 커밋하지 않음 (`.gitignore`에 추가)
- 프로덕션 환경에서는 환경 변수를 직접 설정하거나 Secrets Manager 사용

### 3. 데이터 분리 원칙
- **Neon DB**: 영구 데이터만 저장 (사용자 정보, 계정, 권한)
- **Upstash Redis**: 임시 데이터만 저장 (토큰, 세션, 캐시)
- **절대 규칙**: Neon DB에 임시 데이터 저장 금지, Redis에 영구 데이터 저장 금지

### 4. 서비스 책임 분리
- **User Service**: Neon DB 접근 전담
- **OAuth Service**: Upstash Redis 접근 (Refresh Token, 세션)
- **Gateway Service**: Upstash Redis 접근 (JWT 블랙리스트, Rate Limit)
- 다른 서비스는 직접 DB/Redis 접근 금지, HTTP API를 통해서만 접근

### 5. Redis Key 네이밍
- **일관된 패턴 사용**: `{service}:{purpose}:{identifier}`
- **예시**: `auth:refresh:123`, `gateway:ratelimit:192.168.1.1`
- **TTL 설정**: 모든 Key에 적절한 TTL 설정 (메모리 누수 방지)

### 6. 연결 풀 설정
- **Lettuce Connection Pool**: 최대 연결 수 제한
  ```yaml
  lettuce:
    pool:
      max-active: 8
      max-idle: 8
      min-idle: 0
  ```

### 7. 에러 처리
- **Redis 연결 실패**: Fallback 메커니즘 구현 고려
- **Neon DB 연결 실패**: 재시도 로직 구현
- **타임아웃 설정**: `timeout: 2000ms` 설정으로 무한 대기 방지

### 8. 보안
- **비밀번호 관리**: 환경 변수로 관리, 코드에 하드코딩 금지
- **SSL/TLS**: Upstash Redis는 SSL 필수 사용
- **JWT Secret**: 강력한 Secret Key 사용, 주기적 변경

### 9. 모니터링
- **Redis 메모리 사용량**: Upstash 대시보드에서 모니터링
- **Neon DB 연결 수**: Neon 대시보드에서 모니터링
- **에러 로그**: 각 서비스의 로그에서 연결 에러 확인

### 10. 확장성 고려
- **새로운 서비스 추가 시**: 동일한 전략 적용
  - 영구 데이터 필요 → User Service API 호출
  - 임시 데이터 필요 → Upstash Redis 직접 접근 (해당 서비스에서)
- **서비스 간 통신**: HTTP API 사용, 직접 DB/Redis 접근 금지

---

## 트러블슈팅

### 문제 1: Gateway에서 `oauthservice` 호스트를 찾을 수 없음
**에러**: `java.net.UnknownHostException: Failed to resolve 'oauthservice'`

**해결**: `docker-compose.yaml`에서 서비스 이름과 Gateway의 `application.yaml` URI가 일치하는지 확인
- 서비스 이름: `oauthservice` (하이픈 없음)
- Gateway URI: `http://oauthservice:8091`

### 문제 2: Redis SSL 연결 실패
**에러**: `Failed to bind properties under 'spring.data.redis.ssl'`

**해결**: Spring Boot 3.x에서는 `ssl: true` 대신 `ssl.enabled: true` 사용
```yaml
spring:
  data:
    redis:
      ssl:
        enabled: true  # ✅ 올바른 형식
```

### 문제 3: Neon DB 연결 실패
**에러**: `Driver org.postgresql.Driver claims to not accept jdbcUrl`

**해결**: 환경 변수를 개별적으로 설정
```yaml
spring:
  datasource:
    url: jdbc:postgresql://${NEON_DB_HOST}/${NEON_DB_NAME}
    username: ${NEON_DB_USER}
    password: ${NEON_DB_PASSWORD}
```

---

## 참고 자료

- [Neon 공식 문서](https://neon.tech/docs)
- [Upstash Redis 문서](https://docs.upstash.com/redis)
- [Spring Data Redis 문서](https://spring.io/projects/spring-data-redis)
- [Spring Data JPA 문서](https://spring.io/projects/spring-data-jpa)

---

**작성일**: 2025-12-14  
**버전**: 1.0  
**작성자**: Development Team
