package kr.ai.kjun.api.filter;

import org.springframework.beans.factory.annotation.Autowired;
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

import java.nio.charset.StandardCharsets;
import java.time.Duration;

/**
 * Rate Limit 필터
 * IP 주소별로 요청 횟수를 제한
 * Redis Key: gateway:ratelimit:{ip}
 * 
 * 기본 제한: 1분에 100회
 */
@Component
public class RateLimitFilter implements GlobalFilter, Ordered {

    private static final String RATE_LIMIT_PREFIX = "gateway:ratelimit:";
    private static final int MAX_REQUESTS = 100; // 1분당 최대 요청 수
    private static final Duration TIME_WINDOW = Duration.ofMinutes(1);

    @Autowired
    private ReactiveStringRedisTemplate redisTemplate;

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        String clientIp = getClientIp(request);
        String rateLimitKey = RATE_LIMIT_PREFIX + clientIp;

        // 현재 요청 횟수 조회 및 증가
        return redisTemplate.opsForValue().increment(rateLimitKey)
                .flatMap(count -> {
                    // 첫 요청이면 TTL 설정
                    if (count == 1) {
                        return redisTemplate.expire(rateLimitKey, TIME_WINDOW)
                                .then(Mono.just(count));
                    }
                    return Mono.just(count);
                })
                .flatMap(count -> {
                    if (count > MAX_REQUESTS) {
                        // Rate Limit 초과
                        return handleRateLimitExceeded(exchange);
                    }
                    // 정상 처리
                    return chain.filter(exchange);
                });
    }

    /**
     * 클라이언트 IP 주소 추출
     */
    private String getClientIp(ServerHttpRequest request) {
        String xForwardedFor = request.getHeaders().getFirst("X-Forwarded-For");
        if (xForwardedFor != null && !xForwardedFor.isEmpty()) {
            return xForwardedFor.split(",")[0].trim();
        }

        String xRealIp = request.getHeaders().getFirst("X-Real-IP");
        if (xRealIp != null && !xRealIp.isEmpty()) {
            return xRealIp;
        }

        return request.getRemoteAddress() != null
                ? request.getRemoteAddress().getAddress().getHostAddress()
                : "unknown";
    }

    /**
     * Rate Limit 초과 처리
     */
    private Mono<Void> handleRateLimitExceeded(ServerWebExchange exchange) {
        ServerHttpResponse response = exchange.getResponse();
        response.setStatusCode(HttpStatus.TOO_MANY_REQUESTS);
        response.getHeaders().add("Content-Type", "application/json;charset=UTF-8");
        response.getHeaders().add("Retry-After", String.valueOf(TIME_WINDOW.getSeconds()));

        String errorBody = "{\"success\":false,\"message\":\"요청 횟수가 초과되었습니다. 잠시 후 다시 시도해주세요.\"}";
        return response.writeWith(
                Mono.just(response.bufferFactory().wrap(errorBody.getBytes(StandardCharsets.UTF_8))));
    }

    @Override
    public int getOrder() {
        // JWT 필터보다 먼저 실행 (Rate Limit이 우선)
        return -200;
    }
}
