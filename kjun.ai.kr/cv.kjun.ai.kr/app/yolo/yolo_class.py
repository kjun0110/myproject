# YOLO 이미지 분류 (Classification)
from ultralytics import YOLO
import cv2
import os
import sys


def classify_image(image_path: str) -> dict:
    """
    YOLOv8n-cls를 사용하여 이미지를 분류합니다.

    Args:
        image_path: 이미지 파일 경로

    Returns:
        dict: {
            'success': bool,
            'top_classes': list,  # [(class_name, confidence), ...]
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
                "top_classes": [],
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
                "top_classes": [],
                "output_path": "",
                "message": "",
                "error": f"지원하지 않는 파일 형식입니다: {file_ext}",
            }

        # 이미지 로드
        image = cv2.imread(image_path)
        if image is None:
            return {
                "success": False,
                "top_classes": [],
                "output_path": "",
                "message": "",
                "error": f"이미지를 읽을 수 없습니다: {image_path}",
            }

        # YOLOv8n-cls 모델 로드 (data/yolo/model 디렉토리에서 로드)
        model_dir = os.path.join(
            os.path.dirname(__file__), "..", "data", "yolo", "model"
        )
        model_path = os.path.join(model_dir, "yolov8n-cls.pt")

        # 모델 파일이 없으면 에러 반환
        if not os.path.exists(model_path):
            return {
                "success": False,
                "top_classes": [],
                "output_path": "",
                "message": "",
                "error": f"YOLOv8n-cls 모델 파일을 찾을 수 없습니다: {model_path}\n모델 파일을 해당 경로에 배치해주세요. (data/yolo/model 디렉토리)",
            }

        print(f"YOLOv8n-cls 모델 로드: {model_path}")
        model = YOLO(model_path)

        # 이미지 분류 수행
        results = model(image_path, verbose=False)

        # 결과 저장 디렉토리 생성
        output_dir = os.path.join(
            os.path.dirname(__file__), "..", "data", "yolo", "yolo_detection"
        )
        os.makedirs(output_dir, exist_ok=True)

        # 원본 파일명 가져오기 (확장자 제외)
        file_name_without_ext = os.path.splitext(os.path.basename(image_path))[0]
        file_ext = os.path.splitext(image_path)[1]

        # 결과 파일 경로 (원본 이미지 복사)
        output_filename = f"{file_name_without_ext}_classified{file_ext}"
        output_path = os.path.join(output_dir, output_filename)

        # 원본 이미지 복사 (결과 이미지 생성용)
        annotated_image = image.copy()
        height, width = annotated_image.shape[:2]

        # 분류 결과 추출 (상위 5개)
        top_classes = []
        if len(results) > 0:
            result = results[0]
            if hasattr(result, "probs") and result.probs is not None:
                # 상위 5개 클래스 추출
                probs = result.probs.data.cpu().numpy()
                top5_indices = probs.argsort()[-5:][::-1]  # 상위 5개 인덱스

                for idx in top5_indices:
                    class_name = (
                        result.names[idx] if hasattr(result, "names") else str(idx)
                    )
                    confidence = float(probs[idx])
                    top_classes.append((class_name, confidence))

        # 이미지에 분류 결과 텍스트 추가
        y_offset = 30
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        thickness = 2

        # 배경 영역 그리기
        text_height = 25
        bg_height = len(top_classes) * text_height + 20
        cv2.rectangle(
            annotated_image,
            (10, 10),
            (width - 10, bg_height),
            (0, 0, 0),  # 검은색 배경
            -1,  # 채우기
        )
        cv2.rectangle(
            annotated_image,
            (10, 10),
            (width - 10, bg_height),
            (255, 255, 255),  # 흰색 테두리
            2,
        )

        # 텍스트 그리기
        for i, (class_name, confidence) in enumerate(
            top_classes[:5]
        ):  # 상위 5개만 표시
            text = f"{i + 1}. {class_name}: {confidence:.2%}"
            y_pos = y_offset + i * text_height
            cv2.putText(
                annotated_image,
                text,
                (20, y_pos),
                font,
                font_scale,
                (255, 255, 255),  # 흰색 텍스트
                thickness,
            )

        print(f"YOLOv8n-cls: {len(top_classes)}개 클래스 분류 완료")

        # 결과 이미지 저장
        cv2.imwrite(output_path, annotated_image)

        # 메시지 생성
        if top_classes:
            top_class_name, top_confidence = top_classes[0]
            message = f"분류 완료: {top_class_name} ({top_confidence:.2%} 신뢰도)"
        else:
            message = "분류 결과를 찾을 수 없습니다."

        return {
            "success": True,
            "top_classes": top_classes[:5],  # 상위 5개만 반환
            "output_path": output_path,
            "message": message,
            "error": None,
        }

    except Exception as e:
        import traceback

        traceback.print_exc()
        return {
            "success": False,
            "top_classes": [],
            "output_path": "",
            "message": "",
            "error": str(e),
        }


if __name__ == "__main__":
    # 명령줄 인자에서 파일 경로 가져오기
    if len(sys.argv) < 2:
        print("오류: 파일 경로를 제공해야 합니다.")
        print("사용법: python yolo_class.py <파일경로>")
        exit(1)

    image_path = sys.argv[1]
    result = classify_image(image_path)

    if result["success"]:
        print(result["message"])
        print(f"결과 이미지가 저장되었습니다: {result['output_path']}")
        print("\n상위 분류 결과:")
        for i, (class_name, confidence) in enumerate(result["top_classes"][:5], 1):
            print(f"{i}. {class_name}: {confidence:.2%}")
        print("\n이미지 분류 완료!")
    else:
        print(f"오류 발생: {result['error']}")
        exit(1)
