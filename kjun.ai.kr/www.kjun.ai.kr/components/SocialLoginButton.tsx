"use client";

import { type AuthProvider } from "@/lib/auth";
import { type ReactNode } from "react";

interface SocialLoginButtonProps {
  provider: AuthProvider;
  onClick: () => void;
  disabled?: boolean;
  loading?: boolean;
  icon: ReactNode;
  className?: string;
  loadingText?: string;
  defaultText: string;
}

export function SocialLoginButton({
  provider,
  onClick,
  disabled = false,
  loading = false,
  icon,
  className = "",
  loadingText = "로그인 중...",
  defaultText,
}: SocialLoginButtonProps) {
  return (
    <button
      className={className}
      onClick={onClick}
      disabled={disabled}
    >
      {icon}
      {loading ? loadingText : defaultText}
    </button>
  );
}

