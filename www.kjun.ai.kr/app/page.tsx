"use client";

import Image from "next/image";
import { useSocialLogin } from "@/app/hooks/useSocialLogin";
import { SocialLoginButton } from "@/app/components/SocialLoginButton";

export default function Home() {
  const {
    handleKakaoLogin,
    handleNaverLogin,
    handleGoogleLogin,
    loading,
    error,
    isAnyLoading,
  } = useSocialLogin();

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
            <SocialLoginButton
              provider="google"
              onClick={handleGoogleLogin}
              disabled={isAnyLoading}
              loading={loading.google}
              defaultText="구글로 로그인"
              className="flex h-12 w-full items-center justify-center gap-3 rounded-lg bg-white px-5 text-base font-medium text-gray-700 shadow-sm transition-colors hover:bg-gray-50 border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-zinc-800 dark:text-zinc-200 dark:border-zinc-700 dark:hover:bg-zinc-700"
              icon={
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
              }
            />
            <SocialLoginButton
              provider="kakao"
              onClick={handleKakaoLogin}
              disabled={isAnyLoading}
              loading={loading.kakao}
              defaultText="카카오로 로그인"
              className="flex h-12 w-full items-center justify-center gap-3 rounded-lg bg-[#FEE500] px-5 text-base font-medium text-black transition-colors hover:bg-[#FDD835] disabled:opacity-50 disabled:cursor-not-allowed dark:bg-[#FEE500] dark:hover:bg-[#FDD835]"
              icon={
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
              }
            />
            {error && (
              <div className="mt-2 rounded-lg bg-red-50 p-3 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">
                {error}
              </div>
            )}
            <SocialLoginButton
              provider="naver"
              onClick={handleNaverLogin}
              disabled={isAnyLoading}
              loading={loading.naver}
              defaultText="네이버로 로그인"
              className="flex h-12 w-full items-center justify-center gap-3 rounded-lg bg-[#03C75A] px-5 text-base font-medium text-white transition-colors hover:bg-[#02B350] disabled:opacity-50 disabled:cursor-not-allowed dark:bg-[#03C75A] dark:hover:bg-[#02B350]"
              icon={
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
              }
            />
          </div>
        </div>
      </main>
    </div>
  );
}
