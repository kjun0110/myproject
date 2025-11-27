package kr.ai.kjun.api.google;

import kr.ai.kjun.api.jwt.JwtTokenProvider;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/google")
public class GoogleController {

    private final GoogleService googleService;
    private final JwtTokenProvider jwtTokenProvider;

    @Value("${FRONT_LOGIN_CALLBACK_URL}")
    private String frontendLoginCallbackUrl;

    public GoogleController(GoogleService googleService, JwtTokenProvider jwtTokenProvider) {
        this.googleService = googleService;
        this.jwtTokenProvider = jwtTokenProvider;
    }

    // 구글 로그인 URL 반환
    @PostMapping("/login")
    public ResponseEntity<Map<String, Object>> getGoogleLoginUrl() {
        String loginUrl = googleService.getGoogleLoginUrl();

        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("loginUrl", loginUrl);

        System.out.println("🔗 [구글 로그인] 로그인 URL 생성: " + loginUrl);
        return ResponseEntity.ok(response);
    }

    // 구글 OAuth 콜백 처리
    @GetMapping("/callback")
    public ResponseEntity<?> googleCallback(
            @RequestParam(required = false) String code,
            @RequestParam(required = false) String error) {
        return handleGoogleCallback(code, error);
    }

    private ResponseEntity<?> handleGoogleCallback(String code, String error) {
        System.out.println("🔄 [구글 콜백] code: " + code + ", error: " + error);

        if (error != null) {
            System.err.println("❌ [구글 콜백] 에러: " + error);
            return redirectToError(error);
        }

        if (code == null || code.trim().isEmpty()) {
            System.err.println("❌ [구글 콜백] code 없음");
            return redirectToError("no_code");
        }

        try {
            kr.ai.kjun.api.google.dto.GoogleUserInfo userInfo = googleService.authenticateAndExtractUser(code);
            String jwtToken = generateJwtToken(userInfo);

            System.out.println("✅ [구글 콜백] 로그인 성공 - ID: " + userInfo.getId());
            return redirectToSuccess(userInfo, jwtToken);

        } catch (Exception e) {
            System.err.println("❌ [구글 콜백] 로그인 실패: " + e.getMessage());
            e.printStackTrace();
            return redirectToError(e.getMessage());
        }
    }

    // 구글 로그인 처리 (code 없으면 URL 반환, 있으면 인증 후 JWT 토큰 반환)
    @PostMapping
    public ResponseEntity<Map<String, Object>> googleLogin(@RequestBody(required = false) Map<String, String> request) {
        String code = request != null ? request.get("code") : null;

        if (code == null || code.trim().isEmpty()) {
            try {
                String loginUrl = googleService.getGoogleLoginUrl();
                Map<String, Object> response = new HashMap<>();
                response.put("loginUrl", loginUrl);

                System.out.println("🔗 [구글 로그인] 로그인 URL 생성: " + loginUrl);
                return ResponseEntity.ok(response);
            } catch (Exception e) {
                System.err.println("❌ [구글 로그인] URL 생성 실패: " + e.getMessage());
                return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                        .body(buildErrorResponse("구글 로그인 URL 생성 실패: " + e.getMessage()));
            }
        }

        System.out.println("🔵 [구글 로그인] 진입 - code: " + code);

        try {
            kr.ai.kjun.api.google.dto.GoogleUserInfo userInfo = googleService.authenticateAndExtractUser(code);
            String jwtToken = generateJwtToken(userInfo);

            System.out.println("✅ [구글 로그인] 성공 - ID: " + userInfo.getId());
            return ResponseEntity.ok(buildSuccessResponse(userInfo, jwtToken));

        } catch (Exception e) {
            System.err.println("❌ [구글 로그인] 실패: " + e.getMessage());
            e.printStackTrace();
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(buildErrorResponse("구글 로그인 실패: " + e.getMessage()));
        }
    }

    // JWT 토큰 생성
    private String generateJwtToken(kr.ai.kjun.api.google.dto.GoogleUserInfo userInfo) {
        return jwtTokenProvider.generateToken(
                userInfo.getExtractedIdAsLong(),
                userInfo.getExtractedEmail(),
                userInfo.getExtractedNickname());
    }

    // 성공 응답 생성
    private Map<String, Object> buildSuccessResponse(kr.ai.kjun.api.google.dto.GoogleUserInfo userInfo,
            String jwtToken) {
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("token", jwtToken);

        Map<String, Object> user = new HashMap<>();
        user.put("id", userInfo.getExtractedIdAsLong());
        user.put("email", userInfo.getExtractedEmail());
        user.put("nickname", userInfo.getExtractedNickname());
        user.put("profileImage", userInfo.getExtractedProfileImage());
        response.put("user", user);

        return response;
    }

    // 에러 응답 생성
    private Map<String, Object> buildErrorResponse(String message) {
        Map<String, Object> errorResponse = new HashMap<>();
        errorResponse.put("success", false);
        errorResponse.put("message", message);
        return errorResponse;
    }

    // 성공 리다이렉트
    private ResponseEntity<?> redirectToSuccess(kr.ai.kjun.api.google.dto.GoogleUserInfo userInfo, String jwtToken) {
        String encodedToken = URLEncoder.encode(jwtToken, StandardCharsets.UTF_8);
        String encodedEmail = URLEncoder.encode(userInfo.getExtractedEmail(), StandardCharsets.UTF_8);
        String encodedNickname = URLEncoder.encode(userInfo.getExtractedNickname(), StandardCharsets.UTF_8);

        String redirectUrl = String.format(
                "%s/auth/google/success?token=%s&id=%s&email=%s&nickname=%s",
                frontendLoginCallbackUrl, encodedToken, userInfo.getId(), encodedEmail, encodedNickname);

        return ResponseEntity.status(HttpStatus.FOUND)
                .header("Location", redirectUrl)
                .build();
    }

    // 에러 리다이렉트
    private ResponseEntity<?> redirectToError(String error) {
        String encodedError = URLEncoder.encode(error, StandardCharsets.UTF_8);
        String errorUrl = frontendLoginCallbackUrl + "/auth/google/error?error=" + encodedError;
        return ResponseEntity.status(HttpStatus.FOUND)
                .header("Location", errorUrl)
                .build();
    }
}
