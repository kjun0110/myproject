# YOLO 얼굴 감지 및 결과 저장
from ultralytics import YOLO
import cv2
import os
import sys


def detect_faces(image_path: str) -> dict:
    """
    YOLO를 사용하여 이미지에서 얼굴을 감지하고 결과를 저장합니다.

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

        # YOLOv8n-face 모델 로드 (data/yolo/model 디렉토리에서 로드)
        model_dir = os.path.join(
            os.path.dirname(__file__), "..", "data", "yolo", "model"
        )
        model_path = os.path.join(model_dir, "yolov8n-face.pt")

        # 모델 파일이 없으면 에러 반환
        if not os.path.exists(model_path):
            return {
                "success": False,
                "face_count": 0,
                "output_path": "",
                "message": "",
                "error": f"YOLOv8n-face 모델 파일을 찾을 수 없습니다: {model_path}\n모델 파일을 해당 경로에 배치해주세요. (data/yolo/model 디렉토리)",
            }

        print(f"YOLOv8n-face 모델 로드: {model_path}")
        model = YOLO(model_path)

        # 얼굴 감지 수행 (confidence threshold 설정)
        results = model(image_path, conf=0.25, verbose=False)

        # 결과 저장 디렉토리 생성
        output_dir = os.path.join(
            os.path.dirname(__file__), "..", "data", "yolo", "yolo_detection"
        )
        os.makedirs(output_dir, exist_ok=True)

        # 원본 파일명 가져오기 (확장자 제외)
        file_name_without_ext = os.path.splitext(os.path.basename(image_path))[0]
        file_ext = os.path.splitext(image_path)[1]

        # 결과 파일 경로
        output_filename = f"{file_name_without_ext}_detected{file_ext}"
        output_path = os.path.join(output_dir, output_filename)

        # YOLOv8n-face를 사용하여 얼굴 직접 감지
        annotated_image = image.copy()
        face_count = 0

        # YOLOv8n-face는 모든 감지 결과가 얼굴 (person 클래스 필터링 불필요)
        face_boxes = []
        for result in results:
            for box in result.boxes:
                conf = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                face_boxes.append((conf, int(x1), int(y1), int(x2), int(y2)))

        # 신뢰도가 높은 순으로 정렬
        face_boxes.sort(reverse=True, key=lambda x: x[0])

        print(f"YOLOv8n-face: {len(face_boxes)}개의 얼굴 감지됨")

        # 얼굴 박스 그리기 (얼굴 영역 추정 불필요 - 이미 얼굴 박스)
        for conf, x1, y1, x2, y2 in face_boxes:
            # 얼굴 영역이 너무 작으면 건너뛰기
            face_width = x2 - x1
            face_height = y2 - y1
            if face_width < 30 or face_height < 30:
                continue

            # 얼굴 영역 표시 (초록색, 정확도 포함)
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

        # 결과 이미지 저장
        cv2.imwrite(output_path, annotated_image)

        message = (
            f"총 {face_count}개의 얼굴이 감지되었습니다."
            if face_count > 0
            else "감지된 얼굴이 없습니다."
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


def detect_objects(image_path: str) -> dict:
    """
    YOLO를 사용하여 이미지에서 모든 객체를 감지하고 결과를 저장합니다.
    (yolov8n.pt 모델 사용)

    Args:
        image_path: 이미지 파일 경로

    Returns:
        dict: {
            'success': bool,
            'object_count': int,
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
                "object_count": 0,
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
                "object_count": 0,
                "output_path": "",
                "message": "",
                "error": f"지원하지 않는 파일 형식입니다: {file_ext}",
            }

        # 이미지 로드
        image = cv2.imread(image_path)
        if image is None:
            return {
                "success": False,
                "object_count": 0,
                "output_path": "",
                "message": "",
                "error": f"이미지를 읽을 수 없습니다: {image_path}",
            }

        # YOLOv8n 모델 로드 (data/yolo/model 디렉토리에서 로드)
        model_dir = os.path.join(
            os.path.dirname(__file__), "..", "data", "yolo", "model"
        )
        model_path = os.path.join(model_dir, "yolov8n.pt")

        # 모델 파일이 없으면 에러 반환
        if not os.path.exists(model_path):
            return {
                "success": False,
                "object_count": 0,
                "output_path": "",
                "message": "",
                "error": f"YOLOv8n 모델 파일을 찾을 수 없습니다: {model_path}\n모델 파일을 해당 경로에 배치해주세요. (data/yolo/model 디렉토리)",
            }

        print(f"YOLOv8n 모델 로드: {model_path}")
        model = YOLO(model_path)

        # 객체 감지 수행 (confidence threshold 설정)
        results = model(image_path, conf=0.25, verbose=False)

        # 결과 저장 디렉토리 생성
        output_dir = os.path.join(
            os.path.dirname(__file__), "..", "data", "yolo", "yolo_detection"
        )
        os.makedirs(output_dir, exist_ok=True)

        # 원본 파일명 가져오기 (확장자 제외)
        file_name_without_ext = os.path.splitext(os.path.basename(image_path))[0]
        file_ext = os.path.splitext(image_path)[1]

        # 결과 파일 경로
        output_filename = f"{file_name_without_ext}_objects_detected{file_ext}"
        output_path = os.path.join(output_dir, output_filename)

        # 이미지에 객체 감지 결과 그리기
        annotated_image = image.copy()
        object_count = 0
        detected_objects = []

        # 모든 감지된 객체 처리
        for result in results:
            for box in result.boxes:
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                class_name = model.names[cls]
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                detected_objects.append(
                    {
                        "class": class_name,
                        "confidence": conf,
                        "bbox": (int(x1), int(y1), int(x2), int(y2)),
                    }
                )

                # 객체 박스 그리기 (파란색)
                cv2.rectangle(
                    annotated_image,
                    (int(x1), int(y1)),
                    (int(x2), int(y2)),
                    (255, 0, 0),  # 파란색
                    3,  # 선 두께
                )

                # 레이블에 클래스명과 정확도 표시
                label = f"{class_name} {conf:.2f}"
                (text_width, text_height), baseline = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2
                )
                # 텍스트 배경 그리기
                cv2.rectangle(
                    annotated_image,
                    (int(x1), int(y1) - text_height - 15),
                    (int(x1) + text_width + 10, int(y1)),
                    (255, 0, 0),  # 파란색 배경
                    -1,
                )
                # 텍스트 그리기
                cv2.putText(
                    annotated_image,
                    label,
                    (int(x1) + 5, int(y1) - 8),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (255, 255, 255),  # 흰색 텍스트
                    2,
                )
                object_count += 1

        print(f"YOLOv8n: {object_count}개의 객체 감지됨")

        # 결과 이미지 저장
        cv2.imwrite(output_path, annotated_image)

        # 감지된 객체 클래스별 카운트
        class_counts = {}
        for obj in detected_objects:
            class_name = obj["class"]
            class_counts[class_name] = class_counts.get(class_name, 0) + 1

        message = (
            f"총 {object_count}개의 객체가 감지되었습니다. "
            f"({', '.join([f'{name}: {count}' for name, count in class_counts.items()])})"
            if object_count > 0
            else "감지된 객체가 없습니다."
        )

        return {
            "success": True,
            "object_count": object_count,
            "output_path": output_path,
            "message": message,
            "error": None,
        }

    except Exception as e:
        import traceback

        traceback.print_exc()
        return {
            "success": False,
            "object_count": 0,
            "output_path": "",
            "message": "",
            "error": str(e),
        }


if __name__ == "__main__":
    # 명령줄 인자에서 파일 경로 가져오기
    if len(sys.argv) < 2:
        print("오류: 파일 경로를 제공해야 합니다.")
        print("사용법: python yolo_detection.py <파일경로>")
        exit(1)

    image_path = sys.argv[1]
    result = detect_faces(image_path)

    if result["success"]:
        print(result["message"])
        print(f"결과 이미지가 저장되었습니다: {result['output_path']}")
        print("\n얼굴 감지 완료!")
    else:
        print(f"오류 발생: {result['error']}")
        exit(1)
