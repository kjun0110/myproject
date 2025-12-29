"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getUserInfo, getAccessToken } from "@/lib/oauth";

interface HeaderProps {
  onLoginClick: () => void;
  onAIClick: () => void;
  isSidebarOpen: boolean;
  onSidebarToggle: () => void;
}

export function Header({ onLoginClick, onAIClick, isSidebarOpen, onSidebarToggle }: HeaderProps) {
  const router = useRouter();
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const checkLoginStatus = () => {
    const token = getAccessToken();
    const userInfo = getUserInfo();
    setIsLoggedIn(!!(token && userInfo));
  };

  useEffect(() => {
    // 로그인 상태 확인
    checkLoginStatus();

    // 로그인 상태를 주기적으로 확인 (로컬스토리지 변경 감지)
    const interval = setInterval(checkLoginStatus, 500);

    // 페이지 포커스 시에도 확인
    const handleFocus = () => checkLoginStatus();
    window.addEventListener('focus', handleFocus);

    return () => {
      clearInterval(interval);
      window.removeEventListener('focus', handleFocus);
    };
  }, []);

  const handleAccountClick = () => {
    if (isLoggedIn) {
      router.push("/dashboard");
    } else {
      onLoginClick();
    }
  };
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white dark:bg-zinc-900 border-b border-zinc-200 dark:border-zinc-800">
      <div className="flex items-center justify-between h-16 px-4 md:px-6">
        {/* 좌측: 메뉴 토글 버튼 + 로고 */}
        <div className="flex items-center gap-4">
          <button
            onClick={onSidebarToggle}
            className="p-2 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
            aria-label="사이드바 토글"
          >
            <svg
              className="w-6 h-6 text-zinc-700 dark:text-zinc-300"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              {isSidebarOpen ? (
                <path d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <span className="text-white font-bold text-lg">K</span>
            </div>
            <h1 className="text-xl font-bold text-zinc-900 dark:text-zinc-100">
              Kjun's Log
            </h1>
          </div>
        </div>

        {/* 우측: AI 버튼 + 로그인 버튼 */}
        <div className="flex items-center gap-3">
          <button
            onClick={onAIClick}
            className="px-4 py-2 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 text-white font-medium hover:from-blue-600 hover:to-purple-700 transition-all shadow-sm"
          >
            AI
          </button>
          <button
            onClick={handleAccountClick}
            className="px-4 py-2 rounded-lg bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 font-medium hover:bg-zinc-200 dark:hover:bg-zinc-700 transition-colors"
          >
            {isLoggedIn ? "내계정" : "로그인"}
          </button>
        </div>
      </div>
    </header>
  );
}

