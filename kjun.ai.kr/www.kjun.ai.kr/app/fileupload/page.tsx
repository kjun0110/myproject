"use client";

import { useState, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import { Header } from "@/components/Header";
import { Sidebar } from "@/components/Sidebar";
import { AIChatPanel } from "@/components/AIChatPanel";
import { LoginModal } from "@/components/LoginModal";

export default function FileUploadPage() {
  const router = useRouter();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isAIPanelOpen, setIsAIPanelOpen] = useState(false);
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [filePreviews, setFilePreviews] = useState<Map<number, string>>(new Map());
  const [isUploading, setIsUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const [resultModal, setResultModal] = useState<{
    isOpen: boolean;
    originalImage: string | null;
    detectedImage: string | null;
    detectedImagePath: string | null;
    filename: string;
    faceCount: number;
    objectCount: number;
    personCount: number;
    topClasses: Array<{ class: string, confidence: number }>;
    isDetecting: boolean;
    isDetectingObjects: boolean;
    isSegmenting: boolean;
    isPosing: boolean;
    isClassifying: boolean;
  }>({
    isOpen: false,
    originalImage: null,
    detectedImage: null,
    detectedImagePath: null,
    filename: "",
    faceCount: 0,
    objectCount: 0,
    personCount: 0,
    topClasses: [],
    isDetecting: false,
    isDetectingObjects: false,
    isSegmenting: false,
    isPosing: false,
    isClassifying: false,
  });
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const generatePreview = useCallback((file: File, index: number) => {
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const result = e.target?.result as string;
        setFilePreviews((prev) => {
          const newMap = new Map(prev);
          newMap.set(index, result);
          return newMap;
        });
      };
      reader.readAsDataURL(file);
    } else if (file.type.startsWith('text/') || file.name.endsWith('.txt') || file.name.endsWith('.md')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const text = e.target?.result as string;
        const preview = text.substring(0, 200) + (text.length > 200 ? '...' : '');
        setFilePreviews((prev) => {
          const newMap = new Map(prev);
          newMap.set(index, preview);
          return newMap;
        });
      };
      reader.readAsText(file);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    setSelectedFiles((prev) => {
      const newFiles = [...prev, ...files];
      files.forEach((file, i) => {
        generatePreview(file, prev.length + i);
      });
      return newFiles;
    });
  }, [generatePreview]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setSelectedFiles((prev) => {
      const newFiles = [...prev, ...files];
      files.forEach((file, i) => {
        generatePreview(file, prev.length + i);
      });
      return newFiles;
    });
  }, [generatePreview]);

  const handleRemoveFile = useCallback((index: number) => {
    setSelectedFiles((prev) => {
      const newFiles = prev.filter((_, i) => i !== index);
      // 미리보기 맵 재구성
      setFilePreviews((previews) => {
        const newMap = new Map<number, string>();
        newFiles.forEach((file, newIndex) => {
          const oldIndex = prev.findIndex((f) => f === file);
          if (previews.has(oldIndex)) {
            newMap.set(newIndex, previews.get(oldIndex)!);
          }
        });
        return newMap;
      });
      return newFiles;
    });
  }, []);

  const handleUpload = useCallback(async () => {
    if (selectedFiles.length === 0) return;

    setIsUploading(true);
    setUploadMessage(null);

    try {
      const formData = new FormData();
      selectedFiles.forEach((file) => {
        formData.append("files", file);
      });

      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (response.ok && data.success) {
        const successResults = data.results.filter((r: any) => r.success);
        const successCount = successResults.length;

        // 첫 번째 성공한 이미지 결과를 모달에 표시
        if (successResults.length > 0) {
          const firstResult = successResults[0];

          // 원본 이미지 URL 생성 (업로드된 파일의 미리보기 사용)
          const originalFile = selectedFiles.find(f => f.name === firstResult.filename);
          let originalImageUrl: string | null = null;
          if (originalFile && originalFile.type.startsWith('image/')) {
            originalImageUrl = URL.createObjectURL(originalFile);
          }

          // 업로드된 파일명 (서버에 저장된 파일명)
          const uploadedFilename = firstResult.target_file ?
            firstResult.target_file.split(/[/\\]/).pop() || firstResult.filename :
            firstResult.filename;

          setResultModal({
            isOpen: true,
            originalImage: originalImageUrl,
            detectedImage: null, // 초기에는 감지 결과 없음
            detectedImagePath: null,
            filename: uploadedFilename,
            faceCount: 0,
            objectCount: 0,
            personCount: 0,
            topClasses: [],
            isDetecting: false,
            isDetectingObjects: false,
            isSegmenting: false,
            isPosing: false,
            isClassifying: false,
          });
        }

        setSelectedFiles([]);
        setFilePreviews(new Map());
      } else {
        const errorMessages = data.results
          ?.filter((r: any) => !r.success)
          .map((r: any) => `${r.filename}: ${r.error || "알 수 없는 오류"}`)
          .join("\n");
        setUploadMessage(
          `업로드 실패:\n${errorMessages || data.error || "알 수 없는 오류가 발생했습니다."}`
        );
      }
    } catch (error: any) {
      console.error("파일 업로드 오류:", error);
      setUploadMessage(`업로드 중 오류가 발생했습니다: ${error.message}`);
    } finally {
      setIsUploading(false);
    }
  }, [selectedFiles, router]);

  const isImageFile = (file: File): boolean => {
    return file.type.startsWith('image/');
  };

  const isTextFile = (file: File): boolean => {
    return file.type.startsWith('text/') ||
      file.name.endsWith('.txt') ||
      file.name.endsWith('.md') ||
      file.name.endsWith('.json') ||
      file.name.endsWith('.js') ||
      file.name.endsWith('.ts') ||
      file.name.endsWith('.jsx') ||
      file.name.endsWith('.tsx') ||
      file.name.endsWith('.css') ||
      file.name.endsWith('.html');
  };

  const handleCancel = useCallback(() => {
    router.push("/");
  }, [router]);

  const handleDownload = useCallback(async () => {
    if (!resultModal.detectedImage) return;

    try {
      // 감지된 이미지 URL을 사용하여 다운로드
      const response = await fetch(resultModal.detectedImage);
      if (!response.ok) {
        throw new Error("파일을 다운로드할 수 없습니다.");
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      // 원본 파일명에 _detected 추가
      const baseName = resultModal.filename.split('.')[0];
      const extension = resultModal.filename.split('.').pop() || 'jpg';
      a.download = `${baseName}_detected.${extension}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error("다운로드 오류:", error);
      alert("다운로드 중 오류가 발생했습니다.");
    }
  }, [resultModal]);

  const handleCloseResultModal = useCallback(() => {
    // 원본 이미지 URL 정리
    if (resultModal.originalImage && resultModal.originalImage.startsWith('blob:')) {
      URL.revokeObjectURL(resultModal.originalImage);
    }
    setResultModal({
      isOpen: false,
      originalImage: null,
      detectedImage: null,
      detectedImagePath: null,
      filename: "",
      faceCount: 0,
      objectCount: 0,
      personCount: 0,
      topClasses: [],
      isDetecting: false,
      isDetectingObjects: false,
      isSegmenting: false,
      isPosing: false,
      isClassifying: false,
    });
  }, [resultModal]);

  const handleFaceDetection = useCallback(async () => {
    if (!resultModal.filename || resultModal.isDetecting) return;

    setResultModal((prev) => ({ ...prev, isDetecting: true }));

    try {
      const response = await fetch("/api/detect", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ filename: resultModal.filename }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        // 감지된 이미지 URL 생성
        const detectedImagePath = data.output_path;
        let detectedImageUrl: string;

        // 경로에서 yolo_detection 이후 부분만 추출
        const yoloDetectionIndex = detectedImagePath.indexOf('yolo_detection');
        if (yoloDetectionIndex !== -1) {
          const relativePath = detectedImagePath.substring(yoloDetectionIndex);
          detectedImageUrl = `/api/download?path=${encodeURIComponent(relativePath)}`;
        } else {
          // 백슬래시를 슬래시로 변환하고 yolo_detection 찾기
          const normalizedPath = detectedImagePath.replace(/\\/g, '/');
          const yoloIndex = normalizedPath.indexOf('yolo_detection');
          if (yoloIndex !== -1) {
            const relativePath = normalizedPath.substring(yoloIndex);
            detectedImageUrl = `/api/download?path=${encodeURIComponent(relativePath)}`;
          } else {
            // 파일명만 추출
            const filename = detectedImagePath.split(/[/\\]/).pop() || '';
            detectedImageUrl = `/api/download?path=${encodeURIComponent(`yolo_detection/${filename}`)}`;
          }
        }

        setResultModal((prev) => ({
          ...prev,
          detectedImage: detectedImageUrl,
          detectedImagePath: detectedImagePath,
          faceCount: data.face_count || 0,
          isDetecting: false,
        }));
      } else {
        alert(`얼굴 감지 실패: ${data.error || "알 수 없는 오류"}`);
        setResultModal((prev) => ({ ...prev, isDetecting: false }));
      }
    } catch (error: any) {
      console.error("얼굴 감지 오류:", error);
      alert(`얼굴 감지 중 오류가 발생했습니다: ${error.message}`);
      setResultModal((prev) => ({ ...prev, isDetecting: false }));
    }
  }, [resultModal]);

  const handleObjectDetection = useCallback(async () => {
    if (!resultModal.filename || resultModal.isDetectingObjects) return;

    setResultModal((prev) => ({ ...prev, isDetectingObjects: true }));

    try {
      const response = await fetch("/api/detect-objects", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ filename: resultModal.filename }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        // 감지된 이미지 URL 생성
        const detectedImagePath = data.output_path;
        let detectedImageUrl: string;

        // 경로에서 yolo_detection 이후 부분만 추출
        const yoloDetectionIndex = detectedImagePath.indexOf('yolo_detection');
        if (yoloDetectionIndex !== -1) {
          const relativePath = detectedImagePath.substring(yoloDetectionIndex);
          detectedImageUrl = `/api/download?path=${encodeURIComponent(relativePath)}`;
        } else {
          // 백슬래시를 슬래시로 변환하고 yolo_detection 찾기
          const normalizedPath = detectedImagePath.replace(/\\/g, '/');
          const yoloIndex = normalizedPath.indexOf('yolo_detection');
          if (yoloIndex !== -1) {
            const relativePath = normalizedPath.substring(yoloIndex);
            detectedImageUrl = `/api/download?path=${encodeURIComponent(relativePath)}`;
          } else {
            // 파일명만 추출
            const filename = detectedImagePath.split(/[/\\]/).pop() || '';
            detectedImageUrl = `/api/download?path=${encodeURIComponent(`yolo_detection/${filename}`)}`;
          }
        }

        setResultModal((prev) => ({
          ...prev,
          detectedImage: detectedImageUrl,
          detectedImagePath: detectedImagePath,
          objectCount: data.object_count || 0,
          isDetectingObjects: false,
        }));
      } else {
        alert(`객체 감지 실패: ${data.error || "알 수 없는 오류"}`);
        setResultModal((prev) => ({ ...prev, isDetectingObjects: false }));
      }
    } catch (error: any) {
      console.error("객체 감지 오류:", error);
      alert(`객체 감지 중 오류가 발생했습니다: ${error.message}`);
      setResultModal((prev) => ({ ...prev, isDetectingObjects: false }));
    }
  }, [resultModal]);

  const handleSegmentDetection = useCallback(async () => {
    if (!resultModal.filename || resultModal.isSegmenting) return;

    setResultModal((prev) => ({ ...prev, isSegmenting: true }));

    try {
      const response = await fetch("/api/detect-segment", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ filename: resultModal.filename }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        // 감지된 이미지 URL 생성
        const detectedImagePath = data.output_path;
        let detectedImageUrl: string;

        // 경로에서 yolo_detection 이후 부분만 추출
        const yoloDetectionIndex = detectedImagePath.indexOf('yolo_detection');
        if (yoloDetectionIndex !== -1) {
          const relativePath = detectedImagePath.substring(yoloDetectionIndex);
          detectedImageUrl = `/api/download?path=${encodeURIComponent(relativePath)}`;
        } else {
          // 백슬래시를 슬래시로 변환하고 yolo_detection 찾기
          const normalizedPath = detectedImagePath.replace(/\\/g, '/');
          const yoloIndex = normalizedPath.indexOf('yolo_detection');
          if (yoloIndex !== -1) {
            const relativePath = normalizedPath.substring(yoloIndex);
            detectedImageUrl = `/api/download?path=${encodeURIComponent(relativePath)}`;
          } else {
            // 파일명만 추출
            const filename = detectedImagePath.split(/[/\\]/).pop() || '';
            detectedImageUrl = `/api/download?path=${encodeURIComponent(`yolo_detection/${filename}`)}`;
          }
        }

        setResultModal((prev) => ({
          ...prev,
          detectedImage: detectedImageUrl,
          detectedImagePath: detectedImagePath,
          faceCount: data.face_count || 0,
          isSegmenting: false,
        }));
      } else {
        alert(`얼굴 세그멘테이션 실패: ${data.error || "알 수 없는 오류"}`);
        setResultModal((prev) => ({ ...prev, isSegmenting: false }));
      }
    } catch (error: any) {
      console.error("얼굴 세그멘테이션 오류:", error);
      alert(`얼굴 세그멘테이션 중 오류가 발생했습니다: ${error.message}`);
      setResultModal((prev) => ({ ...prev, isSegmenting: false }));
    }
  }, [resultModal]);

  const handlePoseDetection = useCallback(async () => {
    if (!resultModal.filename || resultModal.isPosing) return;

    setResultModal((prev) => ({ ...prev, isPosing: true }));

    try {
      const response = await fetch("/api/detect-pose", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ filename: resultModal.filename }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        // 감지된 이미지 URL 생성
        const detectedImagePath = data.output_path;
        let detectedImageUrl: string;

        // 경로에서 yolo_detection 이후 부분만 추출
        const yoloDetectionIndex = detectedImagePath.indexOf('yolo_detection');
        if (yoloDetectionIndex !== -1) {
          const relativePath = detectedImagePath.substring(yoloDetectionIndex);
          detectedImageUrl = `/api/download?path=${encodeURIComponent(relativePath)}`;
        } else {
          // 백슬래시를 슬래시로 변환하고 yolo_detection 찾기
          const normalizedPath = detectedImagePath.replace(/\\/g, '/');
          const yoloIndex = normalizedPath.indexOf('yolo_detection');
          if (yoloIndex !== -1) {
            const relativePath = normalizedPath.substring(yoloIndex);
            detectedImageUrl = `/api/download?path=${encodeURIComponent(relativePath)}`;
          } else {
            // 파일명만 추출
            const filename = detectedImagePath.split(/[/\\]/).pop() || '';
            detectedImageUrl = `/api/download?path=${encodeURIComponent(`yolo_detection/${filename}`)}`;
          }
        }

        setResultModal((prev) => ({
          ...prev,
          detectedImage: detectedImageUrl,
          detectedImagePath: detectedImagePath,
          personCount: data.person_count || 0,
          isPosing: false,
        }));
      } else {
        alert(`포즈 추정 실패: ${data.error || "알 수 없는 오류"}`);
        setResultModal((prev) => ({ ...prev, isPosing: false }));
      }
    } catch (error: any) {
      console.error("포즈 추정 오류:", error);
      alert(`포즈 추정 중 오류가 발생했습니다: ${error.message}`);
      setResultModal((prev) => ({ ...prev, isPosing: false }));
    }
  }, [resultModal]);

  const handleClassification = useCallback(async () => {
    if (!resultModal.filename || resultModal.isClassifying) return;

    setResultModal((prev) => ({ ...prev, isClassifying: true }));

    try {
      const response = await fetch("/api/detect-classify", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ filename: resultModal.filename }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        // 감지된 이미지 URL 생성
        const detectedImagePath = data.output_path;
        let detectedImageUrl: string;

        // 경로에서 yolo_detection 이후 부분만 추출
        const yoloDetectionIndex = detectedImagePath.indexOf('yolo_detection');
        if (yoloDetectionIndex !== -1) {
          const relativePath = detectedImagePath.substring(yoloDetectionIndex);
          detectedImageUrl = `/api/download?path=${encodeURIComponent(relativePath)}`;
        } else {
          // 백슬래시를 슬래시로 변환하고 yolo_detection 찾기
          const normalizedPath = detectedImagePath.replace(/\\/g, '/');
          const yoloIndex = normalizedPath.indexOf('yolo_detection');
          if (yoloIndex !== -1) {
            const relativePath = normalizedPath.substring(yoloIndex);
            detectedImageUrl = `/api/download?path=${encodeURIComponent(relativePath)}`;
          } else {
            // 파일명만 추출
            const filename = detectedImagePath.split(/[/\\]/).pop() || '';
            detectedImageUrl = `/api/download?path=${encodeURIComponent(`yolo_detection/${filename}`)}`;
          }
        }

        // top_classes를 배열로 변환 (튜플 형태일 수 있음)
        const topClasses = data.top_classes.map((item: any) => {
          if (Array.isArray(item)) {
            return { class: item[0], confidence: item[1] };
          }
          return item;
        });

        setResultModal((prev) => ({
          ...prev,
          detectedImage: detectedImageUrl,
          detectedImagePath: detectedImagePath,
          topClasses: topClasses,
          isClassifying: false,
        }));
      } else {
        alert(`이미지 분류 실패: ${data.error || "알 수 없는 오류"}`);
        setResultModal((prev) => ({ ...prev, isClassifying: false }));
      }
    } catch (error: any) {
      console.error("이미지 분류 오류:", error);
      alert(`이미지 분류 중 오류가 발생했습니다: ${error.message}`);
      setResultModal((prev) => ({ ...prev, isClassifying: false }));
    }
  }, [resultModal]);

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + " " + sizes[i];
  };

  const handleSidebarToggle = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const handleAIClick = () => {
    setIsAIPanelOpen(!isAIPanelOpen);
  };

  const handleLoginClick = () => {
    setIsLoginModalOpen(true);
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
        <div className="min-h-[calc(100vh-64px)] flex items-center justify-center p-8">
          <div className="w-full max-w-2xl bg-white dark:bg-zinc-900 rounded-xl shadow-2xl">
            {/* 헤더 */}
            <div className="flex items-center justify-between p-6 border-b border-zinc-200 dark:border-zinc-800">
              <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">
                파일 업로드
              </h2>
              <button
                onClick={handleCancel}
                className="p-2 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
                aria-label="닫기"
              >
                <svg
                  className="w-6 h-6 text-zinc-600 dark:text-zinc-400"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* 드래그 앤 드롭 영역 */}
            <div className="p-6">
              <div
                onDragEnter={handleDragEnter}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${isDragging
                  ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                  : "border-zinc-300 dark:border-zinc-700 hover:border-zinc-400 dark:hover:border-zinc-600"
                  }`}
              >
                <svg
                  className="w-16 h-16 mx-auto mb-4 text-zinc-400 dark:text-zinc-600"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p className="text-lg font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                  파일을 여기에 드래그하거나 클릭하여 선택하세요
                </p>
                <p className="text-sm text-zinc-500 dark:text-zinc-500 mb-4">
                  여러 파일을 선택할 수 있습니다
                </p>
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
                >
                  파일 선택
                </button>
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  onChange={handleFileSelect}
                  className="hidden"
                />
              </div>

              {/* 업로드 메시지 */}
              {uploadMessage && (
                <div className={`mt-6 p-4 rounded-lg ${uploadMessage.includes("성공")
                  ? "bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-200"
                  : "bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-200"
                  }`}>
                  <p className="text-sm whitespace-pre-line">{uploadMessage}</p>
                </div>
              )}

              {/* 선택된 파일 목록 */}
              {selectedFiles.length > 0 && (
                <div className="mt-6 space-y-4">
                  <h3 className="text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                    선택된 파일 ({selectedFiles.length})
                  </h3>
                  <div className="max-h-60 overflow-y-auto space-y-2">
                    {selectedFiles.map((file, index) => (
                      <div
                        key={index}
                        className="bg-zinc-50 dark:bg-zinc-800 rounded-lg overflow-hidden"
                      >
                        {/* 파일 정보 */}
                        <div className="flex items-center justify-between p-3">
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-zinc-900 dark:text-zinc-100 truncate">
                              {file.name}
                            </p>
                            <p className="text-xs text-zinc-500 dark:text-zinc-400">
                              {formatFileSize(file.size)}
                            </p>
                          </div>
                          <button
                            onClick={() => handleRemoveFile(index)}
                            className="ml-4 p-1 rounded hover:bg-zinc-200 dark:hover:bg-zinc-700 transition-colors"
                            aria-label="파일 제거"
                          >
                            <svg
                              className="w-5 h-5 text-zinc-600 dark:text-zinc-400"
                              fill="none"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth="2"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        </div>

                        {/* 미리보기 */}
                        {filePreviews.has(index) && (
                          <div className="px-3 pb-3 border-t border-zinc-200 dark:border-zinc-700">
                            {isImageFile(file) ? (
                              <div className="mt-3">
                                <img
                                  src={filePreviews.get(index)}
                                  alt={file.name}
                                  className="max-w-full h-auto max-h-32 rounded object-contain"
                                />
                              </div>
                            ) : isTextFile(file) ? (
                              <div className="mt-3 p-2 bg-white dark:bg-zinc-900 rounded text-xs text-zinc-700 dark:text-zinc-300 font-mono whitespace-pre-wrap break-words max-h-32 overflow-y-auto">
                                {filePreviews.get(index)}
                              </div>
                            ) : null}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* 푸터 버튼 */}
            <div className="flex items-center justify-end gap-3 p-6 border-t border-zinc-200 dark:border-zinc-800">
              <button
                onClick={handleCancel}
                className="px-4 py-2 text-zinc-700 dark:text-zinc-300 font-medium rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
              >
                취소
              </button>
              <button
                onClick={handleUpload}
                disabled={selectedFiles.length === 0 || isUploading}
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-zinc-300 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
              >
                {isUploading ? "업로드 중..." : "업로드"}
              </button>
            </div>
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

      {/* 결과 모달 */}
      {resultModal.isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-zinc-900 rounded-xl shadow-2xl max-w-6xl w-full mx-4 max-h-[90vh] overflow-auto">
            {/* 헤더 */}
            <div className="flex items-center justify-between p-6 border-b border-zinc-200 dark:border-zinc-800">
              <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">
                업로드 결과
              </h2>
              <div className="flex items-center gap-3">
                <button
                  onClick={handleFaceDetection}
                  disabled={resultModal.isDetecting || resultModal.isDetectingObjects || resultModal.isSegmenting || !resultModal.filename}
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-zinc-300 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
                >
                  {resultModal.isDetecting ? "감지 중..." : "face-detection"}
                </button>
                <button
                  onClick={handleObjectDetection}
                  disabled={resultModal.isDetecting || resultModal.isDetectingObjects || resultModal.isSegmenting || !resultModal.filename}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-zinc-300 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
                >
                  {resultModal.isDetectingObjects ? "감지 중..." : "detection"}
                </button>
                <button
                  onClick={handleSegmentDetection}
                  disabled={resultModal.isDetecting || resultModal.isDetectingObjects || resultModal.isSegmenting || resultModal.isPosing || !resultModal.filename}
                  className="px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-zinc-300 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
                >
                  {resultModal.isSegmenting ? "세그멘테이션 중..." : "segment"}
                </button>
                <button
                  onClick={handlePoseDetection}
                  disabled={resultModal.isDetecting || resultModal.isDetectingObjects || resultModal.isSegmenting || resultModal.isPosing || resultModal.isClassifying || !resultModal.filename}
                  className="px-4 py-2 bg-orange-600 hover:bg-orange-700 disabled:bg-zinc-300 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
                >
                  {resultModal.isPosing ? "포즈 추정 중..." : "pose"}
                </button>
                <button
                  onClick={handleClassification}
                  disabled={resultModal.isDetecting || resultModal.isDetectingObjects || resultModal.isSegmenting || resultModal.isPosing || resultModal.isClassifying || !resultModal.filename}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-zinc-300 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
                >
                  {resultModal.isClassifying ? "분류 중..." : "classification"}
                </button>
                <button
                  onClick={handleCloseResultModal}
                  className="p-2 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
                  aria-label="닫기"
                >
                  <svg
                    className="w-6 h-6 text-zinc-600 dark:text-zinc-400"
                    fill="none"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* 이미지 비교 영역 */}
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* 원본 이미지 */}
                <div className="space-y-2">
                  <h3 className="text-lg font-semibold text-zinc-700 dark:text-zinc-300">
                    원본 이미지
                  </h3>
                  {resultModal.originalImage ? (
                    <div className="border-2 border-zinc-200 dark:border-zinc-700 rounded-lg overflow-hidden">
                      <img
                        src={resultModal.originalImage}
                        alt="원본"
                        className="w-full h-auto max-h-[500px] object-contain"
                      />
                    </div>
                  ) : (
                    <div className="border-2 border-zinc-200 dark:border-zinc-700 rounded-lg p-12 text-center text-zinc-500">
                      이미지를 불러올 수 없습니다
                    </div>
                  )}
                </div>

                {/* 감지된 이미지 */}
                <div className="space-y-2">
                  <h3 className="text-lg font-semibold text-zinc-700 dark:text-zinc-300">
                    감지 결과
                    {resultModal.faceCount > 0 && (
                      <span className="ml-2 text-sm font-normal text-blue-600 dark:text-blue-400">
                        ({resultModal.faceCount}개 얼굴 감지)
                      </span>
                    )}
                  </h3>
                  {resultModal.isDetecting || resultModal.isDetectingObjects || resultModal.isSegmenting || resultModal.isPosing || resultModal.isClassifying ? (
                    <div className="border-2 border-zinc-200 dark:border-zinc-700 rounded-lg p-12 text-center">
                      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                      <p className="text-zinc-600 dark:text-zinc-400">
                        {resultModal.isDetecting ? "얼굴 감지 중..." : resultModal.isDetectingObjects ? "객체 감지 중..." : resultModal.isSegmenting ? "세그멘테이션 중..." : resultModal.isPosing ? "포즈 추정 중..." : "분류 중..."}
                      </p>
                    </div>
                  ) : resultModal.detectedImage ? (
                    <div className="border-2 border-zinc-200 dark:border-zinc-700 rounded-lg overflow-hidden">
                      <img
                        src={resultModal.detectedImage}
                        alt="감지 결과"
                        className="w-full h-auto max-h-[500px] object-contain"
                      />
                    </div>
                  ) : (
                    <div className="border-2 border-zinc-200 dark:border-zinc-700 rounded-lg p-12 text-center text-zinc-500">
                      <p className="mb-4">아직 감지되지 않았습니다</p>
                      <p className="text-sm">상단의 "face-detection" 버튼을 클릭하여 얼굴 감지를 시작하세요</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* 하단 버튼 */}
            <div className="flex items-center justify-end gap-3 p-6 border-t border-zinc-200 dark:border-zinc-800">
              <button
                onClick={handleCloseResultModal}
                className="px-4 py-2 text-zinc-700 dark:text-zinc-300 font-medium rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
              >
                닫기
              </button>
              <button
                onClick={handleDownload}
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
              >
                다운로드
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

