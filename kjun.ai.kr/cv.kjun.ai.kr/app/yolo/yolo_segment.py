# YOLO 얼굴 세그멘테이션 (yolov8n-face + yolov8n-seg 사용)
from ultralytics import YOLO
import cv2
import numpy as np
import os
import sys


def detect_face_segment(image_path: str) -> dict:
    """
    yolov8n-face로 얼굴 범위를 찾고, 그 범위 내에서 yolov8n-seg로 얼굴을 세그멘테이션합니다.

    과정:
    1. yolov8n-face 모델로 얼굴 바운딩 박스 감지
    2. 각 얼굴 영역에 대해 yolov8n-seg 모델로 세그멘테이션 수행
    3. 세그멘테이션 마스크를 원본 이미지에 오버레이

    Args:
        image_path: 이미지 파일 경로

    Returns:
        dict: {
            'success': bool,
            'face_count': int,
            'output_path': str,
            'message': str,
            'error': str (optional)
        }
    """
    try:
        # 경로 정규화 (절대 경로로 변환)
        image_path = os.path.abspath(os.path.normpath(image_path))

        # 파일이 존재하는지 확인
        if not os.path.exists(image_path):
            return {
                "success": False,
                "face_count": 0,
                "output_path": "",
                "message": "",
                "error": f"파일을 찾을 수 없습니다: {image_path}",
            }

        # 이미지 파일인지 확인 (확장자 체크)
        valid_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"]
        file_ext = os.path.splitext(image_path)[1].lower()

        if file_ext not in valid_extensions:
            return {
                "success": False,
                "face_count": 0,
                "output_path": "",
                "message": "",
                "error": f"지원하지 않는 파일 형식입니다: {file_ext}",
            }

        # 이미지 로드
        image = cv2.imread(image_path)
        if image is None:
            return {
                "success": False,
                "face_count": 0,
                "output_path": "",
                "message": "",
                "error": f"이미지를 읽을 수 없습니다: {image_path}",
            }

        # 모델 디렉토리 경로
        model_dir = os.path.join(
            os.path.dirname(__file__), "..", "data", "yolo", "model"
        )

        # 1단계: yolov8n-face 모델로 얼굴 감지
        face_model_path = os.path.join(model_dir, "yolov8n-face.pt")
        if not os.path.exists(face_model_path):
            return {
                "success": False,
                "face_count": 0,
                "output_path": "",
                "message": "",
                "error": f"YOLOv8n-face 모델 파일을 찾을 수 없습니다: {face_model_path}\n모델 파일을 해당 경로에 배치해주세요. (data/yolo/model 디렉토리)",
            }

        print(f"YOLOv8n-face 모델 로드: {face_model_path}")
        face_model = YOLO(face_model_path)

        # 얼굴 감지 수행
        face_results = face_model(image_path, conf=0.25, verbose=False)

        # 얼굴 바운딩 박스 추출
        face_boxes = []
        for result in face_results:
            for box in result.boxes:
                conf = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                face_boxes.append((conf, int(x1), int(y1), int(x2), int(y2)))

        # 신뢰도가 높은 순으로 정렬
        face_boxes.sort(reverse=True, key=lambda x: x[0])

        if len(face_boxes) == 0:
            return {
                "success": True,
                "face_count": 0,
                "output_path": "",
                "message": "감지된 얼굴이 없습니다.",
                "error": None,
            }

        print(f"YOLOv8n-face: {len(face_boxes)}개의 얼굴 감지됨")

        # 2단계: yolov8n-seg 모델 로드
        seg_model_path = os.path.join(model_dir, "yolov8n-seg.pt")
        if not os.path.exists(seg_model_path):
            return {
                "success": False,
                "face_count": 0,
                "output_path": "",
                "message": "",
                "error": f"YOLOv8n-seg 모델 파일을 찾을 수 없습니다: {seg_model_path}\n모델 파일을 해당 경로에 배치해주세요. (data/yolo/model 디렉토리)",
            }

        print(f"YOLOv8n-seg 모델 로드: {seg_model_path}")
        seg_model = YOLO(seg_model_path)

        # 결과 저장 디렉토리 생성
        output_dir = os.path.join(
            os.path.dirname(__file__), "..", "data", "yolo", "yolo_detection"
        )
        os.makedirs(output_dir, exist_ok=True)

        # 원본 파일명 가져오기 (확장자 제외)
        file_name_without_ext = os.path.splitext(os.path.basename(image_path))[0]
        file_ext = os.path.splitext(image_path)[1]

        # 결과 파일 경로
        output_filename = f"{file_name_without_ext}_segment{file_ext}"
        output_path = os.path.join(output_dir, output_filename)

        # 원본 이미지 복사 (결과 이미지 생성용)
        annotated_image = image.copy()
        face_count = 0

        # 각 얼굴 바운딩 박스에 대해 세그멘테이션 수행
        for conf, x1, y1, x2, y2 in face_boxes:
            # 얼굴 영역이 너무 작으면 건너뛰기
            face_width = x2 - x1
            face_height = y2 - y1
            if face_width < 30 or face_height < 30:
                continue

            # yolov8n-face가 인식한 정확한 얼굴 범위 내에서만 crop
            face_left = max(0, x1)
            face_top = max(0, y1)
            face_right = min(image.shape[1], x2)
            face_bottom = min(image.shape[0], y2)

            # 얼굴 영역 crop
            face_roi = image[face_top:face_bottom, face_left:face_right]

            if face_roi.size == 0:
                continue

            # 얼굴 ROI에 대해 세그멘테이션 수행
            seg_results = seg_model(face_roi, conf=0.25, verbose=False)

            # 세그멘테이션 결과에서 person 클래스 찾기
            person_class_id = 0
            found_segmentation = False

            for seg_result in seg_results:
                if seg_result.masks is not None:
                    for i, box in enumerate(seg_result.boxes):
                        cls = int(box.cls[0])

                        # person 클래스만 처리
                        if cls == person_class_id:
                            # 마스크 가져오기
                            mask = seg_result.masks.data[i].cpu().numpy()

                            # 마스크를 ROI 크기로 변환
                            if mask.shape != (face_roi.shape[0], face_roi.shape[1]):
                                mask_resized = cv2.resize(
                                    mask, (face_roi.shape[1], face_roi.shape[0])
                                )
                            else:
                                mask_resized = mask

                            mask_binary = (mask_resized > 0.5).astype(np.uint8) * 255

                            # 얼굴 마스크가 있는지 확인 (전체 ROI 범위 사용)
                            if np.any(mask_binary > 0):
                                # 전체 이미지 크기의 마스크 생성
                                full_mask = np.zeros(
                                    (image.shape[0], image.shape[1]), dtype=np.uint8
                                )
                                # yolov8n-face가 인식한 범위 내에만 마스크 적용
                                full_mask[
                                    face_top:face_bottom, face_left:face_right
                                ] = mask_binary

                                # 컬러 마스크 생성 (초록색)
                                color_mask = np.zeros_like(image)
                                color_mask[full_mask > 0] = [0, 255, 0]  # 초록색

                                # 원본 이미지와 마스크 오버레이 (투명도 적용)
                                annotated_image = cv2.addWeighted(
                                    annotated_image, 0.7, color_mask, 0.3, 0
                                )

                                found_segmentation = True
                                break

                    if found_segmentation:
                        break

            # 얼굴 영역 바운딩 박스 그리기 (세그멘테이션 성공 여부와 관계없이)
            cv2.rectangle(
                annotated_image,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),  # 초록색
                3,  # 선 두께
            )

            # 레이블에 정확도 표시
            label = f"face {conf:.2f}"
            (text_width, text_height), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2
            )
            # 텍스트 배경 그리기
            cv2.rectangle(
                annotated_image,
                (x1, y1 - text_height - 15),
                (x1 + text_width + 10, y1),
                (0, 255, 0),
                -1,
            )
            # 텍스트 그리기
            cv2.putText(
                annotated_image,
                label,
                (x1 + 5, y1 - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 0, 0),  # 검은색 텍스트
                2,
            )
            face_count += 1

        print(f"YOLOv8n-seg: {face_count}개의 얼굴 세그멘테이션 완료")

        # 결과 이미지 저장
        cv2.imwrite(output_path, annotated_image)

        message = (
            f"총 {face_count}개의 얼굴이 세그멘테이션되었습니다."
            if face_count > 0
            else "세그멘테이션된 얼굴이 없습니다."
        )

        return {
            "success": True,
            "face_count": face_count,
            "output_path": output_path,
            "message": message,
            "error": None,
        }

    except Exception as e:
        import traceback

        traceback.print_exc()
        return {
            "success": False,
            "face_count": 0,
            "output_path": "",
            "message": "",
            "error": str(e),
        }


if __name__ == "__main__":
    # 명령줄 인자에서 파일 경로 가져오기
    if len(sys.argv) < 2:
        print("오류: 파일 경로를 제공해야 합니다.")
        print("사용법: python yolo_segment.py <파일경로>")
        exit(1)

    image_path = sys.argv[1]
    result = detect_face_segment(image_path)

    if result["success"]:
        print(result["message"])
        print(f"결과 이미지가 저장되었습니다: {result['output_path']}")
        print("\n얼굴 세그멘테이션 완료!")
    else:
        print(f"오류 발생: {result['error']}")
        exit(1)
