/**
 * 에러 처리 유틸리티
 */

import { ERROR_MESSAGES } from "@/constants/oauth";
import type { OAuthError } from "@/store/auth.index";

/**
 * 에러 응답을 파싱하여 에러 메시지를 추출
 */
export async function parseErrorResponse(
    response: Response,
    endpoint: string
): Promise<string> {
    if (response.status === 404) {
        return `${ERROR_MESSAGES.ENDPOINT_NOT_FOUND}\nGateway에 POST ${endpoint} 엔드포인트가 있는지 확인해주세요.`;
    }

    let errorMessage = `HTTP error! status: ${response.status}`;

    try {
        const errorText = await response.text();
        console.error("🔴 에러 응답 본문:", errorText);

        try {
            const errorData: OAuthError = JSON.parse(errorText);
            errorMessage = errorData.message || errorData.error || errorText;
            console.error("🔴 에러 데이터:", errorData);
        } catch {
            errorMessage = errorText || errorMessage;
        }
    } catch (e) {
        console.error("🔴 에러 응답 읽기 실패:", e);
    }

    return errorMessage;
}

