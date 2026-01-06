"use client";

import { useRouter } from "next/navigation";
import { useState, useRef, useEffect } from "react";
import { useIsLoggedIn } from "@/hooks/dashboard/useAuth";
import { handleLogout } from "@/services/dashboard/dashboardService";

interface HeaderProps {
  onLoginClick: () => void;
  onAIClick: () => void;
  isSidebarOpen: boolean;
  onSidebarToggle: () => void;
}

export function Header({ onLoginClick, onAIClick, isSidebarOpen, onSidebarToggle }: HeaderProps) {
  const router = useRouter();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  
  // Hook을 통해 로그인 상태 가져오기
  const isLoggedIn = useIsLoggedIn();

  // 외부 클릭 시 드롭다운 닫기
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };

    if (isDropdownOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isDropdownOpen]);

  const handleAccountClick = () => {
    if (isLoggedIn) {
      setIsDropdownOpen(!isDropdownOpen);
    } else {
      onLoginClick();
    }
  };

  const handleMyInfoClick = () => {
    setIsDropdownOpen(false);
    router.push("/dashboard");
  };

  const handleLogoutClick = async () => {
    setIsDropdownOpen(false);
    await handleLogout();
    router.push("/");
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

        {/* 우측: AI 버튼 + 로그인/내계정 버튼 */}
        <div className="flex items-center gap-3 relative" ref={dropdownRef}>
          <button
            onClick={onAIClick}
            className="px-4 py-2 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 text-white font-medium hover:from-blue-600 hover:to-purple-700 transition-all shadow-sm"
          >
            AI
          </button>
          <div className="relative">
            <button
              onClick={handleAccountClick}
              className="px-4 py-2 rounded-lg bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 font-medium hover:bg-zinc-200 dark:hover:bg-zinc-700 transition-colors flex items-center gap-2"
            >
              {isLoggedIn ? "내계정" : "로그인"}
              {isLoggedIn && (
                <svg
                  className={`w-4 h-4 transition-transform ${isDropdownOpen ? "rotate-180" : ""}`}
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path d="M19 9l-7 7-7-7" />
                </svg>
              )}
            </button>

            {/* 드롭다운 메뉴 */}
            {isLoggedIn && isDropdownOpen && (
              <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-zinc-800 rounded-lg shadow-lg border border-zinc-200 dark:border-zinc-700 overflow-hidden z-50">
                <button
                  onClick={() => setIsDropdownOpen(false)}
                  className="w-full px-4 py-3 text-left text-sm text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-700 transition-colors border-b border-zinc-200 dark:border-zinc-700"
                >
                  내계정
                </button>
                <button
                  onClick={handleMyInfoClick}
                  className="w-full px-4 py-3 text-left text-sm text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-700 transition-colors border-b border-zinc-200 dark:border-zinc-700"
                >
                  내정보
                </button>
                <button
                  onClick={handleLogoutClick}
                  className="w-full px-4 py-3 text-left text-sm text-red-600 dark:text-red-400 hover:bg-zinc-100 dark:hover:bg-zinc-700 transition-colors"
                >
                  로그아웃
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}

