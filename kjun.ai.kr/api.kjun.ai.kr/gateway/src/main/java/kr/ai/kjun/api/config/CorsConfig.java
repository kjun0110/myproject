package kr.ai.kjun.api.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.reactive.CorsWebFilter;
import org.springframework.web.cors.reactive.UrlBasedCorsConfigurationSource;

import java.util.Arrays;
import java.util.List;

/**
 * CORS 설정
 * 프론트엔드(localhost:4000)에서의 요청 허용
 */
@Configuration
public class CorsConfig {

    @Bean
    public CorsWebFilter corsWebFilter() {
        CorsConfiguration corsConfig = new CorsConfiguration();

        // 허용할 Origin
        corsConfig.setAllowedOrigins(List.of("http://localhost:4000"));

        // 허용할 HTTP 메서드
        corsConfig.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"));

        // 허용할 헤더
        corsConfig.setAllowedHeaders(List.of("*"));

        // 인증 정보 포함 허용
        corsConfig.setAllowCredentials(true);

        // Preflight 요청 캐시 시간
        corsConfig.setMaxAge(3600L);

        // 모든 경로에 적용
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", corsConfig);

        return new CorsWebFilter(source);
    }
}
