package kr.ai.kjun.api.kakao;

import kr.ai.kjun.api.jwt.JwtTokenProvider;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/kakao")
// CORS는 Gateway에서 처리하므로 제거
public class KakaoController {

    private final KakaoService kakaoService;
    private final JwtTokenProvider jwtTokenProvider;

    public KakaoController(KakaoService kakaoService, JwtTokenProvider jwtTokenProvider) {
        this.kakaoService = kakaoService;
        this.jwtTokenProvider = jwtTokenProvider;
    }

    /**
     * 카카오 로그인 URL 반환
     * POST /api/auth/kakao/login
     * 
     * 응답: {
     * "success": true,
     * "loginUrl": "https://kauth.kakao.com/oauth/authorize?..."
     * }
     */
    @PostMapping("/login")
    public ResponseEntity<Map<String, Object>> getKakaoLoginUrl() {
        String loginUrl = kakaoService.getKakaoLoginUrl();

        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("loginUrl", loginUrl);

        System.out.println("🔗 [카카오 로그인] 로그인 URL 생성: " + loginUrl);
        System.out.flush();

        return ResponseEntity.ok(response);
    }

    /**
     * 카카오 OAuth2 콜백 처리
     * GET /auth/kakao/callback?code=...
     * 
     * 카카오 로그인 후 리다이렉트되는 콜백 URL
     * code를 받아서 실제 로그인 처리 후 프론트엔드로 리다이렉트
     */
    @GetMapping("/callback")
    public ResponseEntity<?> kakaoCallback(
            @RequestParam(required = false) String code,
            @RequestParam(required = false) String error) {
        return handleKakaoCallback(code, error);
    }

    /**
     * 카카오 콜백 처리 (내부 메서드)
     */
    private ResponseEntity<?> handleKakaoCallback(String code, String error) {
        System.out.println("🔄 [카카오 콜백] 콜백 진입 - code: " + code + ", error: " + error);
        System.out.flush();

        // 에러가 있는 경우
        if (error != null) {
            System.err.println("❌ [카카오 콜백] 에러 발생: " + error);
            System.err.flush();

            String encodedError = URLEncoder.encode(error, StandardCharsets.UTF_8);
            return ResponseEntity.status(HttpStatus.FOUND)
                    .header("Location", "http://localhost:3000/auth/kakao/error?error=" + encodedError)
                    .build();
        }

        // code가 없는 경우
        if (code == null || code.trim().isEmpty()) {
            System.err.println("❌ [카카오 콜백] code가 없습니다");
            System.err.flush();

            return ResponseEntity.status(HttpStatus.FOUND)
                    .header("Location", "http://localhost:3000/auth/kakao/error?error=no_code")
                    .build();
        }

        try {
            // 공통 인증 로직 사용
            kr.ai.kjun.api.kakao.dto.KakaoUserInfo userInfo = kakaoService.authenticateAndExtractUser(code);

            // JWT 토큰 생성
            String jwtToken = jwtTokenProvider.generateToken(
                    userInfo.getId(),
                    userInfo.getExtractedEmail(),
                    userInfo.getExtractedNickname());

            System.out.println(
                    "✅ [카카오 콜백] 로그인 성공 - ID: " + userInfo.getId() + ", Email: " + userInfo.getExtractedEmail());
            System.out.flush();

            // 프론트엔드로 리다이렉트 (URL 인코딩 필수)
            String encodedToken = URLEncoder.encode(jwtToken, StandardCharsets.UTF_8);
            String encodedEmail = URLEncoder.encode(userInfo.getExtractedEmail(), StandardCharsets.UTF_8);
            String encodedNickname = URLEncoder.encode(userInfo.getExtractedNickname(), StandardCharsets.UTF_8);

            String redirectUrl = String.format(
                    "http://localhost:3000/auth/kakao/success?token=%s&id=%d&email=%s&nickname=%s",
                    encodedToken, userInfo.getId(), encodedEmail, encodedNickname);

            return ResponseEntity.status(HttpStatus.FOUND)
                    .header("Location", redirectUrl)
                    .build();

        } catch (Exception e) {
            System.err.println("❌ [카카오 콜백] 로그인 실패: " + e.getMessage());
            e.printStackTrace();
            System.err.flush();

            String encodedError = URLEncoder.encode(e.getMessage(), StandardCharsets.UTF_8);
            return ResponseEntity.status(HttpStatus.FOUND)
                    .header("Location", "http://localhost:3000/auth/kakao/error?error=" + encodedError)
                    .build();
        }
    }

    /**
     * 카카오 로그인 처리 (실제 인증 + JWT 생성, DB 저장 X)
     * POST /api/auth/kakao
     * 
     * 요청 body: { "code": "카카오 인가 코드" }
     * 응답: {
     * "success": true,
     * "token": "JWT_TOKEN",
     * "user": { "id": 123456, "email": "test@example.com", "nickname": "테스트 사용자" }
     * }
     */
    @PostMapping
    public ResponseEntity<Map<String, Object>> kakaoLogin(@RequestBody Map<String, String> request) {
        String code = request != null ? request.get("code") : null;

        if (code == null || code.trim().isEmpty()) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("message", "카카오 인가 코드(code)가 필요합니다");
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(errorResponse);
        }

        System.out.println("🔵 [카카오 로그인] 진입 - code: " + code);
        System.out.flush();

        try {
            // 공통 인증 로직 사용
            kr.ai.kjun.api.kakao.dto.KakaoUserInfo userInfo = kakaoService.authenticateAndExtractUser(code);

            // JWT 토큰 생성
            String jwtToken = jwtTokenProvider.generateToken(
                    userInfo.getId(),
                    userInfo.getExtractedEmail(),
                    userInfo.getExtractedNickname());

            // 응답 생성
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("token", jwtToken);

            Map<String, Object> user = new HashMap<>();
            user.put("id", userInfo.getId());
            user.put("email", userInfo.getExtractedEmail());
            user.put("nickname", userInfo.getExtractedNickname());
            user.put("profileImage", userInfo.getExtractedProfileImage());
            response.put("user", user);

            System.out.println("✅ [카카오 로그인] 성공 - ID: " + userInfo.getId() + ", Email: " + userInfo.getExtractedEmail());
            System.out.flush();

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            System.err.println("❌ [카카오 로그인] 실패: " + e.getMessage());
            e.printStackTrace();
            System.err.flush();

            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("message", "카카오 로그인 실패: " + e.getMessage());

            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

}
