"use client";

import { useState } from "react";

interface MenuItem {
  id: string;
  label: string;
  onClick?: () => void;
}

interface SidebarSection {
  id: string;
  label: string;
  items: MenuItem[];
}

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(["code"]));

  // 예시 데이터 구조 - 실제로는 props나 상태 관리로 받아올 수 있음
  const sections: SidebarSection[] = [
    {
      id: "code",
      label: "코드정리",
      items: [
        { id: "code-1", label: "정리 항목 1" },
        { id: "code-2", label: "정리 항목 2" },
        { id: "code-3", label: "정리 항목 3" },
      ],
    },
    {
      id: "project",
      label: "프로젝트",
      items: [
        { id: "project-1", label: "프로젝트 1" },
        { id: "project-2", label: "프로젝트 2" },
        { id: "project-3", label: "프로젝트 3" },
      ],
    },
  ];

  const toggleSection = (sectionId: string) => {
    setExpandedSections((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(sectionId)) {
        newSet.delete(sectionId);
      } else {
        newSet.add(sectionId);
      }
      return newSet;
    });
  };

  const handleItemClick = (item: MenuItem) => {
    if (item.onClick) {
      item.onClick();
    }
    // 여기에 아이템 클릭 시 처리 로직 추가
    console.log("Item clicked:", item);
  };

  return (
    <>
      {/* 배경 오버레이 - 모바일에서만 */}
      {isOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/20 backdrop-blur-sm lg:hidden"
          onClick={onClose}
        />
      )}

      {/* 사이드바 */}
      <aside
        className={`fixed top-16 left-0 bottom-0 w-64 bg-white dark:bg-zinc-900 border-r border-zinc-200 dark:border-zinc-800 z-40 transform transition-transform duration-300 ease-out ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex flex-col h-full">
          {/* 사이드바 내용 */}
          <div className="flex-1 overflow-y-auto p-2">
            {sections.map((section) => {
              const isExpanded = expandedSections.has(section.id);
              return (
                <div key={section.id} className="mb-1">
                  {/* 섹션 헤더 (토글 버튼) */}
                  <button
                    onClick={() => toggleSection(section.id)}
                    className="w-full flex items-center gap-3 px-4 py-3 text-sm font-medium text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-lg transition-colors"
                  >
                    <svg
                      className={`w-4 h-4 transition-transform duration-200 ${
                        isExpanded ? "rotate-180" : ""
                      }`}
                      fill="none"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path d="M19 9l-7 7-7-7" />
                    </svg>
                    <span className="flex-1 text-left">{section.label}</span>
                  </button>

                  {/* 하위 메뉴 아이템들 */}
                  {isExpanded && (
                    <div className="mt-1 space-y-1 pl-4">
                      {section.items.map((item) => (
                        <button
                          key={item.id}
                          onClick={() => handleItemClick(item)}
                          className="w-full text-left px-4 py-2 text-sm text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800 hover:text-zinc-900 dark:hover:text-zinc-100 rounded-lg transition-colors"
                        >
                          {item.label}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </aside>
    </>
  );
}
