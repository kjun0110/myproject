package kr.ai.kjun.api.kakao;

import kr.ai.kjun.api.config.KakaoConfig;
import kr.ai.kjun.api.kakao.dto.KakaoTokenResponse;
import kr.ai.kjun.api.kakao.dto.KakaoUserInfo;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;

/**
 * 카카오 OAuth API 호출 서비스 (RestTemplate 사용, WebFlux 없음)
 */
@Service
public class KakaoService {

    private final RestTemplate restTemplate;
    private final KakaoConfig kakaoConfig;

    // 카카오 API URL
    private static final String KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token";
    private static final String KAKAO_USER_INFO_URL = "https://kapi.kakao.com/v2/user/me";

    public KakaoService(RestTemplate restTemplate, KakaoConfig kakaoConfig) {
        this.restTemplate = restTemplate;
        this.kakaoConfig = kakaoConfig;
    }

    /**
     * 카카오 로그인 URL 생성
     * 
     * @return 카카오 로그인 URL
     */
    public String getKakaoLoginUrl() {
        String baseUrl = "https://kauth.kakao.com/oauth/authorize";
        String clientId = kakaoConfig.getRestApiKey();
        String redirectUri = kakaoConfig.getRedirectUri();

        // 카카오 로그인 시 동의 항목 요청 (scope 파라미터 추가)
        // profile_nickname: 닉네임, profile_image: 프로필 이미지
        // account_email은 카카오 개발자 콘솔에서 설정되지 않아서 제외
        String scope = "profile_nickname,profile_image";

        try {
            // URL 인코딩 적용 (redirect_uri와 scope 모두 인코딩)
            String encodedRedirectUri = URLEncoder.encode(redirectUri, StandardCharsets.UTF_8.toString());
            String encodedScope = URLEncoder.encode(scope, StandardCharsets.UTF_8.toString());

            String kakaoAuthUrl = String.format("%s?client_id=%s&redirect_uri=%s&response_type=code&scope=%s",
                    baseUrl, clientId, encodedRedirectUri, encodedScope);

            System.out.println("🔗 [카카오 로그인 URL 생성]");
            System.out.println("  - 원본 redirect_uri: " + redirectUri);
            System.out.println("  - 인코딩된 redirect_uri: " + encodedRedirectUri);
            System.out.println("  - 최종 URL: " + kakaoAuthUrl);
            System.out.flush();

            return kakaoAuthUrl;
        } catch (Exception e) {
            System.err.println("❌ [카카오 로그인 URL 생성 실패] " + e.getMessage());
            System.err.flush();
            throw new RuntimeException("카카오 로그인 URL 생성 실패", e);
        }
    }

    /**
     * 1. Authorization Code로 Access Token 받기
     * 
     * @param code 카카오 인가 코드
     * @return 카카오 토큰 응답
     */
    public KakaoTokenResponse getAccessToken(String code) {
        System.out.println("🔑 [카카오 API] Access Token 요청 시작 - code: " + code);
        System.out.flush();

        // 요청 헤더 설정
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_FORM_URLENCODED);

        // 요청 파라미터 설정
        MultiValueMap<String, String> params = new LinkedMultiValueMap<>();
        params.add("grant_type", "authorization_code");
        params.add("client_id", kakaoConfig.getRestApiKey());
        params.add("redirect_uri", kakaoConfig.getRedirectUri());
        params.add("code", code);

        HttpEntity<MultiValueMap<String, String>> request = new HttpEntity<>(params, headers);

        try {
            ResponseEntity<KakaoTokenResponse> response = restTemplate.postForEntity(
                    KAKAO_TOKEN_URL,
                    request,
                    KakaoTokenResponse.class);

            KakaoTokenResponse tokenResponse = response.getBody();
            if (tokenResponse != null) {
                System.out.println("✅ [카카오 API] Access Token 받기 성공");
                System.out.flush();
                return tokenResponse;
            } else {
                throw new RuntimeException("카카오 토큰 응답이 null입니다");
            }
        } catch (org.springframework.web.client.HttpClientErrorException e) {
            System.err.println("❌ [카카오 API] Access Token 받기 실패: " + e.getStatusCode() + " - " + e.getMessage());
            System.err.println("❌ [카카오 API] 응답 본문: " + e.getResponseBodyAsString());
            System.err.println("❌ [카카오 API] 사용된 설정 - client_id: " + kakaoConfig.getRestApiKey() + ", redirect_uri: "
                    + kakaoConfig.getRedirectUri());
            System.err.flush();
            throw new RuntimeException(
                    "카카오 Access Token 발급 실패: " + e.getStatusCode() + " - " + e.getResponseBodyAsString(), e);
        } catch (Exception e) {
            System.err.println("❌ [카카오 API] Access Token 받기 실패: " + e.getMessage());
            System.err.flush();
            throw new RuntimeException("카카오 Access Token 발급 실패", e);
        }
    }

    /**
     * 2. Access Token으로 사용자 정보 받기
     * 
     * @param accessToken 카카오 액세스 토큰
     * @return 카카오 사용자 정보
     */
    public KakaoUserInfo getUserInfo(String accessToken) {
        System.out.println("👤 [카카오 API] 사용자 정보 요청 시작");
        System.out.flush();

        // 요청 헤더 설정
        HttpHeaders headers = new HttpHeaders();
        headers.set("Authorization", "Bearer " + accessToken);
        headers.setContentType(MediaType.APPLICATION_FORM_URLENCODED);

        HttpEntity<String> request = new HttpEntity<>(headers);

        try {
            // 카카오 API 호출 (property_keys 없이 전체 정보 요청)
            ResponseEntity<String> rawResponse = restTemplate.exchange(
                    KAKAO_USER_INFO_URL,
                    HttpMethod.GET,
                    request,
                    String.class);

            System.out.println("🔍 [디버깅] 카카오 API Raw 응답: " + rawResponse.getBody());
            System.out.flush();

            ResponseEntity<KakaoUserInfo> response = restTemplate.exchange(
                    KAKAO_USER_INFO_URL,
                    HttpMethod.GET,
                    request,
                    KakaoUserInfo.class);

            KakaoUserInfo userInfo = response.getBody();
            if (userInfo != null) {
                System.out.println("✅ [카카오 API] 사용자 정보 받기 성공 - ID: " + userInfo.getId());
                System.out.flush();
                return userInfo;
            } else {
                throw new RuntimeException("카카오 사용자 정보 응답이 null입니다");
            }
        } catch (Exception e) {
            System.err.println("❌ [카카오 API] 사용자 정보 받기 실패: " + e.getMessage());
            System.err.flush();
            throw new RuntimeException("카카오 사용자 정보 조회 실패", e);
        }
    }

    /**
     * 카카오 인증 및 사용자 정보 추출 (공통 로직)
     * 
     * @param code 카카오 인가 코드
     * @return 카카오 사용자 정보 (KakaoUserInfo)
     */
    public KakaoUserInfo authenticateAndExtractUser(String code) {
        // 1. Access Token 받기
        KakaoTokenResponse tokenResponse = getAccessToken(code);

        // 2. 사용자 정보 받기
        KakaoUserInfo userInfo = getUserInfo(tokenResponse.getAccessToken());

        // 3. 디버깅: 받아온 정보 로그 출력
        System.out.println("🔍 [디버깅] 받아온 카카오 사용자 정보:");
        System.out.println("  - ID: " + userInfo.getId());
        if (userInfo.getKakaoAccount() != null) {
            System.out.println("  - hasEmail: " + userInfo.getKakaoAccount().getHasEmail());
            System.out.println("  - emailNeedsAgreement: " + userInfo.getKakaoAccount().getEmailNeedsAgreement());
            System.out.println("  - email: " + userInfo.getKakaoAccount().getEmail());
            if (userInfo.getKakaoAccount().getProfile() != null) {
                System.out.println("  - nickname: " + userInfo.getKakaoAccount().getProfile().getNickname());
                System.out.println(
                        "  - profileImageUrl: " + userInfo.getKakaoAccount().getProfile().getProfileImageUrl());
            } else {
                System.out.println("  - profile: null");
            }
        } else {
            System.out.println("  - kakao_account: null");
        }
        System.out.flush();

        return userInfo;
    }
}
