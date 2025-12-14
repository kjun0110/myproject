package kr.ai.kjun.api.filter;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.data.redis.core.ReactiveStringRedisTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.http.server.reactive.ServerHttpResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.List;

/**
 * JWT 인증 필터
 * 모든 보호된 API 요청에 대해 JWT 검증 및 블랙리스트 확인
 * 
 * 인증이 필요 없는 경로:
 * - /api/oauth/** (OAuth 로그인, 토큰 갱신, 로그아웃)
 * - /oauth/** (OAuth 콜백)
 * - /docs (Swagger UI)
 * - /v3/api-docs (OpenAPI 문서)
 * - /api/ml/openapi.json (ML Service OpenAPI)
 */
@Component
public class JwtAuthenticationFilter implements GlobalFilter, Ordered {

    private static final String AUTHORIZATION_HEADER = "Authorization";
    private static final String BEARER_PREFIX = "Bearer ";
    private static final String BLACKLIST_PREFIX = "auth:blacklist:";

    // 인증이 필요 없는 경로
    private static final List<String> PUBLIC_PATHS = List.of(
            "/api/oauth/",
            "/oauth/",
            "/docs",
            "/v3/api-docs",
            "/api/ml/openapi.json");

    @Autowired
    private SecretKey jwtSecretKey;

    @Autowired
    private ReactiveStringRedisTemplate redisTemplate;

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        String path = request.getURI().getPath();

        // 공개 경로는 인증 생략
        if (isPublicPath(path)) {
            return chain.filter(exchange);
        }

        // Authorization 헤더에서 토큰 추출
        String token = extractToken(request);

        if (token == null) {
            return handleUnauthorized(exchange, "토큰이 없습니다");
        }

        // JWT 검증
        Claims claims = validateToken(token);
        if (claims == null) {
            return handleUnauthorized(exchange, "유효하지 않은 토큰입니다");
        }

        // Redis에서 블랙리스트 확인
        String jti = claims.getId();
        if (jti == null) {
            // JTI가 없으면 토큰의 subject를 사용
            jti = claims.getSubject();
        }

        String blacklistKey = BLACKLIST_PREFIX + jti;

        return redisTemplate.opsForValue().get(blacklistKey)
                .flatMap(value -> {
                    if (value != null && !value.isEmpty()) {
                        // 토큰이 블랙리스트에 있음
                        return handleUnauthorized(exchange, "로그아웃된 토큰입니다");
                    }

                    // 인증 성공 - 사용자 정보를 헤더에 추가하여 하위 서비스로 전달
                    ServerHttpRequest modifiedRequest = request.mutate()
                            .header("X-User-Id", String.valueOf(claims.get("userId", Long.class)))
                            .header("X-User-Email", claims.get("email", String.class))
                            .header("X-User-Nickname", claims.get("nickname", String.class))
                            .build();

                    return chain.filter(exchange.mutate().request(modifiedRequest).build());
                })
                .switchIfEmpty(
                        // 블랙리스트에 없으면 정상 처리
                        Mono.defer(() -> {
                            ServerHttpRequest modifiedRequest = request.mutate()
                                    .header("X-User-Id", String.valueOf(claims.get("userId", Long.class)))
                                    .header("X-User-Email", claims.get("email", String.class))
                                    .header("X-User-Nickname", claims.get("nickname", String.class))
                                    .build();

                            return chain.filter(exchange.mutate().request(modifiedRequest).build());
                        }));
    }

    /**
     * 공개 경로인지 확인
     */
    private boolean isPublicPath(String path) {
        return PUBLIC_PATHS.stream().anyMatch(path::startsWith);
    }

    /**
     * Authorization 헤더에서 토큰 추출
     */
    private String extractToken(ServerHttpRequest request) {
        List<String> authHeaders = request.getHeaders().get(AUTHORIZATION_HEADER);
        if (authHeaders == null || authHeaders.isEmpty()) {
            return null;
        }

        String authHeader = authHeaders.get(0);
        if (authHeader != null && authHeader.startsWith(BEARER_PREFIX)) {
            return authHeader.substring(BEARER_PREFIX.length());
        }

        return null;
    }

    /**
     * JWT 토큰 검증
     */
    private Claims validateToken(String token) {
        try {
            return Jwts.parser()
                    .verifyWith(jwtSecretKey)
                    .build()
                    .parseSignedClaims(token)
                    .getPayload();
        } catch (Exception e) {
            System.err.println("❌ [Gateway JWT 검증 실패] " + e.getMessage());
            return null;
        }
    }

    /**
     * 인증 실패 처리
     */
    private Mono<Void> handleUnauthorized(ServerWebExchange exchange, String message) {
        ServerHttpResponse response = exchange.getResponse();
        response.setStatusCode(HttpStatus.UNAUTHORIZED);
        response.getHeaders().add("Content-Type", "application/json;charset=UTF-8");

        String errorBody = String.format("{\"success\":false,\"message\":\"%s\"}", message);
        return response.writeWith(
                Mono.just(response.bufferFactory().wrap(errorBody.getBytes(StandardCharsets.UTF_8))));
    }

    @Override
    public int getOrder() {
        // 필터 실행 순서 (낮을수록 먼저 실행)
        return -100;
    }
}
