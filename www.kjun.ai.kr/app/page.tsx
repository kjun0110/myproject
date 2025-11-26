"use client";

import Image from "next/image";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function Home() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [isNaverLoading, setIsNaverLoading] = useState(false);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleKakaoLogin = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Gateway에 직접 fetch로 연결
      const apiGatewayUrl = "http://localhost:8080";
      const response = await fetch(`${apiGatewayUrl}/api/auth/kakao/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({}),  // 빈 객체라도 body 전송
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(
            "Gateway API 엔드포인트를 찾을 수 없습니다.\n" +
            "Gateway에 POST /api/auth/kakao/login 엔드포인트가 있는지 확인해주세요."
          );
        }

        // 400 에러인 경우 상세한 에러 정보 확인
        let errorMessage = `HTTP error! status: ${response.status}`;
        try {
          const errorText = await response.text();
          console.error("🔴 에러 응답 본문:", errorText);

          // JSON 형식이면 파싱
          try {
            const errorData = JSON.parse(errorText);
            errorMessage = errorData.message || errorData.error || errorText;
            console.error("🔴 에러 데이터:", errorData);
          } catch {
            // JSON이 아니면 텍스트 그대로 사용
            errorMessage = errorText || errorMessage;
          }
        } catch (e) {
          console.error("🔴 에러 응답 읽기 실패:", e);
        }

        throw new Error(errorMessage);
      }

      const data = await response.json();
      console.log("Gateway 응답:", data);

      // Gateway 응답 형식 처리
      // 옵션 1: 카카오 로그인 URL을 반환하는 경우
      if (data.loginUrl) {
        console.log("카카오 로그인 URL로 리다이렉트:", data.loginUrl);
        setIsLoading(false);
        // 카카오 로그인 페이지로 리다이렉트
        window.location.href = data.loginUrl;
        return;
      }

      // 옵션 2: 토큰을 직접 반환하는 경우 (테스트용)
      if (data.success === true && data.token) {
        // 토큰을 localStorage에 저장
        localStorage.setItem("access_token", data.token);

        // 사용자 정보도 저장 (선택사항)
        if (data.user) {
          localStorage.setItem("user_info", JSON.stringify(data.user));
        }

        // 로그인 제공자 정보 저장
        localStorage.setItem("login_provider", "kakao");

        console.log("카카오 로그인 성공:", data);
        setIsLoading(false);

        // 대시보드로 이동
        router.push("/dashboard");
      } else {
        throw new Error(data.message || "로그인에 실패했습니다.");
      }
    } catch (err) {
      console.error("카카오 로그인 에러:", err);
      setError(
        err instanceof Error
          ? err.message
          : "서버 연결에 실패했습니다. 서버가 실행 중인지 확인해주세요."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleNaverLogin = async () => {
    setIsNaverLoading(true);
    setError(null);

    try {
      // Gateway에 직접 fetch로 연결
      const apiGatewayUrl = "http://localhost:8080";
      const response = await fetch(`${apiGatewayUrl}/api/auth/naver`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({}),  // 빈 객체라도 body 전송
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(
            "Gateway API 엔드포인트를 찾을 수 없습니다.\n" +
            "Gateway에 POST /api/auth/naver 엔드포인트가 있는지 확인해주세요."
          );
        }

        // 400 에러인 경우 상세한 에러 정보 확인
        let errorMessage = `HTTP error! status: ${response.status}`;
        try {
          const errorText = await response.text();
          console.error("🔴 에러 응답 본문:", errorText);

          try {
            const errorData = JSON.parse(errorText);
            errorMessage = errorData.message || errorData.error || errorText;
          } catch {
            errorMessage = errorText || errorMessage;
          }
        } catch (e) {
          console.error("🔴 에러 응답 읽기 실패:", e);
        }

        throw new Error(errorMessage);
      }

      const data = await response.json();
      console.log("Gateway 응답:", data);

      // Gateway 응답 형식 처리
      // Gateway는 { success: true, token: "...", user: {...} } 형식으로 응답
      if (data.success === true && data.token) {
        // 토큰을 localStorage에 저장
        localStorage.setItem("access_token", data.token);

        // 사용자 정보도 저장 (선택사항)
        if (data.user) {
          localStorage.setItem("user_info", JSON.stringify(data.user));
        }

        // 로그인 제공자 정보 저장
        localStorage.setItem("login_provider", "naver");

        console.log("네이버 로그인 성공:", data);
        setIsNaverLoading(false);

        // 대시보드로 이동
        router.push("/dashboard");
      } else {
        throw new Error(data.message || "로그인에 실패했습니다.");
      }
    } catch (err) {
      console.error("네이버 로그인 에러:", err);
      setError(
        err instanceof Error
          ? err.message
          : "서버 연결에 실패했습니다. 서버가 실행 중인지 확인해주세요."
      );
    } finally {
      setIsNaverLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setIsGoogleLoading(true);
    setError(null);

    try {
      // Gateway에 직접 fetch로 연결
      const apiGatewayUrl = "http://localhost:8080";
      const response = await fetch(`${apiGatewayUrl}/api/auth/google`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({}),  // 빈 객체라도 body 전송
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(
            "Gateway API 엔드포인트를 찾을 수 없습니다.\n" +
            "Gateway에 POST /api/auth/google 엔드포인트가 있는지 확인해주세요."
          );
        }
        const errorData = await response.json().catch(() => ({ message: "로그인에 실패했습니다." }));
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log("Gateway 응답:", data);

      // Gateway 응답 형식 처리
      // Gateway는 { success: true, token: "...", user: {...} } 형식으로 응답
      if (data.success === true && data.token) {
        // 토큰을 localStorage에 저장
        localStorage.setItem("access_token", data.token);

        // 사용자 정보도 저장 (선택사항)
        if (data.user) {
          localStorage.setItem("user_info", JSON.stringify(data.user));
        }

        // 로그인 제공자 정보 저장
        localStorage.setItem("login_provider", "google");

        console.log("구글 로그인 성공:", data);
        setIsGoogleLoading(false);

        // 대시보드로 이동
        router.push("/dashboard");
      } else {
        throw new Error(data.message || "로그인에 실패했습니다.");
      }
    } catch (err) {
      console.error("구글 로그인 에러:", err);
      setError(
        err instanceof Error
          ? err.message
          : "서버 연결에 실패했습니다. 서버가 실행 중인지 확인해주세요."
      );
    } finally {
      setIsGoogleLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex w-full max-w-md flex-col items-center gap-8 py-16 px-6">
        <Image
          className="dark:invert"
          src="/next.svg"
          alt="Next.js logo"
          width={100}
          height={20}
          priority
        />
        <div className="flex w-full flex-col gap-6">
          <div className="flex flex-col gap-2 text-center">
            <h1 className="text-2xl font-semibold text-black dark:text-zinc-50">
              소셜 로그인
            </h1>
            <p className="text-sm text-zinc-600 dark:text-zinc-400">
              원하는 소셜 계정으로 로그인하세요
            </p>
          </div>
          <div className="flex w-full flex-col gap-3">
            <button
              className="flex h-12 w-full items-center justify-center gap-3 rounded-lg bg-white px-5 text-base font-medium text-gray-700 shadow-sm transition-colors hover:bg-gray-50 border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-zinc-800 dark:text-zinc-200 dark:border-zinc-700 dark:hover:bg-zinc-700"
              onClick={handleGoogleLogin}
              disabled={isGoogleLoading || isLoading || isNaverLoading}
            >
              <svg
                className="h-5 w-5"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  fill="#4285F4"
                />
                <path
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  fill="#34A853"
                />
                <path
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  fill="#FBBC05"
                />
                <path
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  fill="#EA4335"
                />
              </svg>
              {isGoogleLoading ? "로그인 중..." : "구글로 로그인"}
            </button>
            <button
              className="flex h-12 w-full items-center justify-center gap-3 rounded-lg bg-[#FEE500] px-5 text-base font-medium text-black transition-colors hover:bg-[#FDD835] disabled:opacity-50 disabled:cursor-not-allowed dark:bg-[#FEE500] dark:hover:bg-[#FDD835]"
              onClick={handleKakaoLogin}
              disabled={isLoading}
            >
              <svg
                className="h-5 w-5"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M12 3C6.48 3 2 6.14 2 10c0 2.38 1.91 4.5 4.84 5.73l-.88 3.17 3.4-2.24c.95.13 1.93.2 2.64.2 5.52 0 10-3.14 10-7s-4.48-7-10-7z"
                  fill="#000000"
                />
              </svg>
              {isLoading ? "로그인 중..." : "카카오로 로그인"}
            </button>
            {error && (
              <div className="mt-2 rounded-lg bg-red-50 p-3 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">
                {error}
              </div>
            )}
            <button
              className="flex h-12 w-full items-center justify-center gap-3 rounded-lg bg-[#03C75A] px-5 text-base font-medium text-white transition-colors hover:bg-[#02B350] disabled:opacity-50 disabled:cursor-not-allowed dark:bg-[#03C75A] dark:hover:bg-[#02B350]"
              onClick={handleNaverLogin}
              disabled={isNaverLoading || isLoading}
            >
              <svg
                className="h-5 w-5"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M16.273 12.845L7.376 0H0v24h7.726V11.156L16.624 24H24V0h-7.727v12.845z"
                  fill="#FFFFFF"
                />
              </svg>
              {isNaverLoading ? "로그인 중..." : "네이버로 로그인"}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
