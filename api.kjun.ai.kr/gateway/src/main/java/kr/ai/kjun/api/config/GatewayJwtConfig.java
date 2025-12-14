package kr.ai.kjun.api.config;

import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.connection.ReactiveRedisConnectionFactory;
import org.springframework.data.redis.core.ReactiveStringRedisTemplate;
import org.springframework.data.redis.serializer.RedisSerializationContext;
import org.springframework.data.redis.serializer.StringRedisSerializer;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;

/**
 * Gateway JWT 및 Redis 설정
 */
@Configuration
public class GatewayJwtConfig {

    @Value("${spring.jwt.secret}")
    private String jwtSecret;

    /**
     * JWT Secret Key 생성
     */
    @Bean
    public SecretKey jwtSecretKey() {
        return Keys.hmacShaKeyFor(jwtSecret.getBytes(StandardCharsets.UTF_8));
    }

    /**
     * Reactive Redis Template (WebFlux용)
     * Spring Boot의 자동 설정을 사용하되, 명시적으로 Bean으로 등록
     */
    @Bean
    @SuppressWarnings("null")
    public ReactiveStringRedisTemplate reactiveStringRedisTemplate(ReactiveRedisConnectionFactory connectionFactory) {
        StringRedisSerializer serializer = new StringRedisSerializer();
        RedisSerializationContext<String, String> serializationContext = RedisSerializationContext
                .<String, String>newSerializationContext()
                .key(serializer)
                .value(serializer)
                .hashKey(serializer)
                .hashValue(serializer)
                .build();

        return new ReactiveStringRedisTemplate(connectionFactory, serializationContext);
    }
}
