package kr.ai.kjun.api.naver;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/naver")
// CORS는 Gateway에서 처리하므로 제거
public class NaverController {

    /**
     * 네이버 로그인 처리 (모의 데이터)
     * POST /api/auth/naver
     * 
     * 요청 body: { "code": "네이버 인가 코드" } (선택사항)
     * 응답: { "success": true, "token": "mock_jwt_token_12345", "user": { "id":
     * 123456, "email": "test@example.com", "nickname": "테스트 사용자" } }
     */
    @PostMapping
    public ResponseEntity<Map<String, Object>> naverLogin(
            @RequestBody(required = false) Map<String, String> request) {
        System.out.println(
                "🟢🟢🟢🟢🟢🟢🟢🟢🟢 [네이버 로그인] 로그인 진입 - 요청 코드: " + (request != null ? request.get("code") : "없음"));
        System.out.flush();

        // 네이버 API 호출 없이 바로 성공 응답 반환
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("token", "mock_jwt_token_" + System.currentTimeMillis());

        Map<String, Object> user = new HashMap<>();
        user.put("id", 123458L);
        user.put("email", "naver@example.com");
        user.put("nickname", "네이버 사용자");
        response.put("user", user);

        System.out.println("✅✅✅✅✅✅✅ [네이버 로그인] 로그인 성공 - 사용자 ID: " + user.get("id") + ", 이메일: " + user.get("email"));
        System.out.flush();
        return ResponseEntity.ok(response);
    }
}
