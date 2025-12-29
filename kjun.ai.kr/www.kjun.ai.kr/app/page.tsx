"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Header } from "@/components/Header";
import { Sidebar } from "@/components/Sidebar";
import { AIChatPanel } from "@/components/AIChatPanel";
import { LoginModal } from "@/components/LoginModal";
import { getUserInfo, getAccessToken } from "@/lib/oauth";

export default function Home() {
  const router = useRouter();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isAIPanelOpen, setIsAIPanelOpen] = useState(false);
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const checkLoginStatus = () => {
      const token = getAccessToken();
      const userInfo = getUserInfo();
      setIsLoggedIn(!!(token && userInfo));
    };

    checkLoginStatus();
    const interval = setInterval(checkLoginStatus, 500);
    const handleFocus = () => checkLoginStatus();
    window.addEventListener('focus', handleFocus);

    return () => {
      clearInterval(interval);
      window.removeEventListener('focus', handleFocus);
    };
  }, []);

  const handleSidebarToggle = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const handleAIClick = () => {
    setIsAIPanelOpen(!isAIPanelOpen);
  };

  const handleLoginClick = () => {
    setIsLoginModalOpen(true);
  };

  const handleFileUploadClick = () => {
    router.push("/fileupload");
  };

  return (
    <div className="flex min-h-screen bg-zinc-50 font-sans dark:bg-black">
      {/* 헤더 */}
      <Header
        onLoginClick={handleLoginClick}
        onAIClick={handleAIClick}
        isSidebarOpen={isSidebarOpen}
        onSidebarToggle={handleSidebarToggle}
      />

      {/* 사이드바 */}
      <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />

      {/* 메인 콘텐츠 */}
      <main
        className={`flex-1 transition-all duration-300 ${isSidebarOpen ? "ml-64" : "ml-0"
          }`}
        style={{ paddingTop: "64px" }}
      >
        <div className="min-h-[calc(100vh-64px)] p-8">
          <div className="flex justify-end">
            {isLoggedIn && (
              <button
                onClick={handleFileUploadClick}
                className="px-6 py-3 rounded-lg bg-green-600 hover:bg-green-700 text-white font-medium transition-colors"
              >
                파일업로드
              </button>
            )}
          </div>
        </div>
      </main>

      {/* AI 챗봇 패널 */}
      <AIChatPanel isOpen={isAIPanelOpen} onClose={() => setIsAIPanelOpen(false)} />

      {/* 로그인 모달 */}
      <LoginModal
        isOpen={isLoginModalOpen}
        onClose={() => setIsLoginModalOpen(false)}
      />
    </div>
  );
}
