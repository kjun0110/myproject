package kr.ai.kjun.api.naver;

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
@RequestMapping("/naver")
public class NaverController {

    private final NaverService naverService;
    private final JwtTokenProvider jwtTokenProvider;

    @Value("${FRONT_LOGIN_CALLBACK_URL}")
    private String frontendLoginCallbackUrl;

    public NaverController(NaverService naverService, JwtTokenProvider jwtTokenProvider) {
        this.naverService = naverService;
        this.jwtTokenProvider = jwtTokenProvider;
    }

    // 네이버 로그인 URL 반환
    @PostMapping("/login")
    public ResponseEntity<Map<String, Object>> getNaverLoginUrl() {
        String loginUrl = naverService.getNaverLoginUrl();

        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("loginUrl", loginUrl);

        System.out.println("🔗 [네이버 로그인] 로그인 URL 생성: " + loginUrl);
        return ResponseEntity.ok(response);
    }

    // 네이버 OAuth 콜백 처리
    @GetMapping("/callback")
    public ResponseEntity<?> naverCallback(
            @RequestParam(required = false) String code,
            @RequestParam(required = false) String state,
            @RequestParam(required = false) String error) {
        return handleNaverCallback(code, state, error);
    }

    private ResponseEntity<?> handleNaverCallback(String code, String state, String error) {
        System.out.println("🔄 [네이버 콜백] code: " + code + ", state: " + state + ", error: " + error);

        if (error != null) {
            System.err.println("❌ [네이버 콜백] 에러: " + error);
            return redirectToError(error);
        }

        if (code == null || code.trim().isEmpty()) {
            System.err.println("❌ [네이버 콜백] code 없음");
            return redirectToError("no_code");
        }

        try {
            kr.ai.kjun.api.naver.dto.NaverUserInfo userInfo = naverService.authenticateAndExtractUser(code, state);
            String jwtToken = generateJwtToken(userInfo);

            System.out.println("✅ [네이버 콜백] 로그인 성공 - ID: " + userInfo.getExtractedId());
            return redirectToSuccess(userInfo, jwtToken);

        } catch (Exception e) {
            System.err.println("❌ [네이버 콜백] 로그인 실패: " + e.getMessage());
            e.printStackTrace();
            return redirectToError(e.getMessage());
        }
    }

    // 네이버 로그인 처리 (code 없으면 URL 반환, 있으면 인증 후 JWT 토큰 반환)
    @PostMapping
    public ResponseEntity<Map<String, Object>> naverLogin(@RequestBody(required = false) Map<String, String> request) {
        String code = request != null ? request.get("code") : null;
        String state = request != null ? request.get("state") : null;

        if (code == null || code.trim().isEmpty()) {
            try {
                String loginUrl = naverService.getNaverLoginUrl();
                Map<String, Object> response = new HashMap<>();
                response.put("loginUrl", loginUrl);

                System.out.println("🔗 [네이버 로그인] 로그인 URL 생성: " + loginUrl);
                return ResponseEntity.ok(response);
            } catch (Exception e) {
                System.err.println("❌ [네이버 로그인] URL 생성 실패: " + e.getMessage());
                return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                        .body(buildErrorResponse("네이버 로그인 URL 생성 실패: " + e.getMessage()));
            }
        }

        System.out.println("🟢 [네이버 로그인] 진입 - code: " + code);

        try {
            kr.ai.kjun.api.naver.dto.NaverUserInfo userInfo = naverService.authenticateAndExtractUser(code, state);
            String jwtToken = generateJwtToken(userInfo);

            System.out.println("✅ [네이버 로그인] 성공 - ID: " + userInfo.getExtractedId());
            return ResponseEntity.ok(buildSuccessResponse(userInfo, jwtToken));

        } catch (Exception e) {
            System.err.println("❌ [네이버 로그인] 실패: " + e.getMessage());
            e.printStackTrace();
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(buildErrorResponse("네이버 로그인 실패: " + e.getMessage()));
        }
    }

    // JWT 토큰 생성 (네이버 ID는 String이므로 해시코드로 변환)
    private String generateJwtToken(kr.ai.kjun.api.naver.dto.NaverUserInfo userInfo) {
        Long userId = Long.valueOf(userInfo.getExtractedId().hashCode());
        return jwtTokenProvider.generateToken(
                userId,
                userInfo.getExtractedEmail(),
                userInfo.getExtractedNickname());
    }

    // 성공 응답 생성
    private Map<String, Object> buildSuccessResponse(kr.ai.kjun.api.naver.dto.NaverUserInfo userInfo, String jwtToken) {
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("token", jwtToken);

        Map<String, Object> user = new HashMap<>();
        user.put("id", userInfo.getExtractedId());
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
    private ResponseEntity<?> redirectToSuccess(kr.ai.kjun.api.naver.dto.NaverUserInfo userInfo, String jwtToken) {
        String encodedToken = URLEncoder.encode(jwtToken, StandardCharsets.UTF_8);
        String encodedEmail = URLEncoder.encode(userInfo.getExtractedEmail(), StandardCharsets.UTF_8);
        String encodedNickname = URLEncoder.encode(userInfo.getExtractedNickname(), StandardCharsets.UTF_8);
        String encodedId = URLEncoder.encode(userInfo.getExtractedId(), StandardCharsets.UTF_8);

        String redirectUrl = String.format(
                "%s/auth/naver/success?token=%s&id=%s&email=%s&nickname=%s",
                frontendLoginCallbackUrl, encodedToken, encodedId, encodedEmail, encodedNickname);

        return ResponseEntity.status(HttpStatus.FOUND)
                .header("Location", redirectUrl)
                .build();
    }

    // 에러 리다이렉트
    private ResponseEntity<?> redirectToError(String error) {
        String encodedError = URLEncoder.encode(error, StandardCharsets.UTF_8);
        String errorUrl = frontendLoginCallbackUrl + "/auth/naver/error?error=" + encodedError;
        return ResponseEntity.status(HttpStatus.FOUND)
                .header("Location", errorUrl)
                .build();
    }
}
