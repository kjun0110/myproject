# YOLO 포즈 추정 (스켈레톤)
from ultralytics import YOLO
import cv2
import numpy as np
import os
import sys


def detect_pose(image_path: str) -> dict:
    """
    YOLOv8n-pose를 사용하여 이미지에서 사람의 포즈를 스켈레톤으로 추정합니다.

    Args:
        image_path: 이미지 파일 경로

    Returns:
        dict: {
            'success': bool,
            'person_count': int,
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
                "person_count": 0,
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
                "person_count": 0,
                "output_path": "",
                "message": "",
                "error": f"지원하지 않는 파일 형식입니다: {file_ext}",
            }

        # 이미지 로드
        image = cv2.imread(image_path)
        if image is None:
            return {
                "success": False,
                "person_count": 0,
                "output_path": "",
                "message": "",
                "error": f"이미지를 읽을 수 없습니다: {image_path}",
            }

        # YOLOv8n-pose 모델 로드 (data/yolo/model 디렉토리에서 로드)
        model_dir = os.path.join(
            os.path.dirname(__file__), "..", "data", "yolo", "model"
        )
        model_path = os.path.join(model_dir, "yolov8n-pose.pt")

        # 모델 파일이 없으면 에러 반환
        if not os.path.exists(model_path):
            return {
                "success": False,
                "person_count": 0,
                "output_path": "",
                "message": "",
                "error": f"YOLOv8n-pose 모델 파일을 찾을 수 없습니다: {model_path}\n모델 파일을 해당 경로에 배치해주세요. (data/yolo/model 디렉토리)",
            }

        print(f"YOLOv8n-pose 모델 로드: {model_path}")
        model = YOLO(model_path)

        # 포즈 추정 수행 (confidence threshold 설정)
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
        output_filename = f"{file_name_without_ext}_pose{file_ext}"
        output_path = os.path.join(output_dir, output_filename)

        # 원본 이미지 복사 (결과 이미지 생성용)
        annotated_image = image.copy()
        person_count = 0

        # COCO 포즈 키포인트 연결 정보 (스켈레톤 그리기용)
        # 키포인트 인덱스: 0:코, 1:왼쪽눈, 2:오른쪽눈, 3:왼쪽귀, 4:오른쪽귀,
        # 5:왼쪽어깨, 6:오른쪽어깨, 7:왼쪽팔꿈치, 8:오른쪽팔꿈치,
        # 9:왼쪽손목, 10:오른쪽손목, 11:왼쪽엉덩이, 12:오른쪽엉덩이,
        # 13:왼쪽무릎, 14:오른쪽무릎, 15:왼쪽발목, 16:오른쪽발목
        skeleton = [
            [0, 1],
            [0, 2],
            [1, 3],
            [2, 4],  # 머리
            [5, 6],  # 어깨
            [5, 7],
            [7, 9],  # 왼쪽 팔
            [6, 8],
            [8, 10],  # 오른쪽 팔
            [5, 11],
            [6, 12],  # 몸통 상단
            [11, 12],  # 엉덩이
            [11, 13],
            [13, 15],  # 왼쪽 다리
            [12, 14],
            [14, 16],  # 오른쪽 다리
        ]

        # 포즈 추정 결과 처리
        for result in results:
            if result.keypoints is not None:
                for i, box in enumerate(result.boxes):
                    conf = float(box.conf[0])
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                    # 키포인트 가져오기
                    keypoints = (
                        result.keypoints.data[i].cpu().numpy()
                    )  # shape: (17, 3) [x, y, confidence]

                    # 키포인트가 있는지 확인
                    if keypoints.shape[0] > 0:
                        # 스켈레톤 그리기 (키포인트 연결)
                        for connection in skeleton:
                            pt1_idx, pt2_idx = connection
                            if pt1_idx < len(keypoints) and pt2_idx < len(keypoints):
                                pt1 = keypoints[pt1_idx]
                                pt2 = keypoints[pt2_idx]

                                # 키포인트가 유효한 경우에만 그리기 (confidence > 0.5)
                                if pt1[2] > 0.5 and pt2[2] > 0.5:
                                    pt1_coords = (int(pt1[0]), int(pt1[1]))
                                    pt2_coords = (int(pt2[0]), int(pt2[1]))

                                    # 스켈레톤 선 그리기 (파란색)
                                    cv2.line(
                                        annotated_image,
                                        pt1_coords,
                                        pt2_coords,
                                        (255, 0, 0),  # 파란색
                                        3,  # 선 두께
                                    )

                        # 키포인트 점 그리기
                        for j, kpt in enumerate(keypoints):
                            x, y, conf_kpt = kpt
                            if conf_kpt > 0.5:  # 키포인트 신뢰도 체크
                                center = (int(x), int(y))
                                # 키포인트 점 그리기 (빨간색)
                                cv2.circle(
                                    annotated_image,
                                    center,
                                    5,  # 반지름
                                    (0, 0, 255),  # 빨간색
                                    -1,  # 채우기
                                )

                        person_count += 1

                        # 바운딩 박스 그리기 (선택사항)
                        cv2.rectangle(
                            annotated_image,
                            (x1, y1),
                            (x2, y2),
                            (0, 255, 0),  # 초록색
                            2,  # 선 두께
                        )

        print(f"YOLOv8n-pose: {person_count}명의 포즈 추정 완료")

        # 결과 이미지 저장
        cv2.imwrite(output_path, annotated_image)

        message = (
            f"총 {person_count}명의 포즈가 추정되었습니다."
            if person_count > 0
            else "추정된 포즈가 없습니다."
        )

        return {
            "success": True,
            "person_count": person_count,
            "output_path": output_path,
            "message": message,
            "error": None,
        }

    except Exception as e:
        import traceback

        traceback.print_exc()
        return {
            "success": False,
            "person_count": 0,
            "output_path": "",
            "message": "",
            "error": str(e),
        }


if __name__ == "__main__":
    # 명령줄 인자에서 파일 경로 가져오기
    if len(sys.argv) < 2:
        print("오류: 파일 경로를 제공해야 합니다.")
        print("사용법: python yolo_pose.py <파일경로>")
        exit(1)

    image_path = sys.argv[1]
    result = detect_pose(image_path)

    if result["success"]:
        print(result["message"])
        print(f"결과 이미지가 저장되었습니다: {result['output_path']}")
        print("\n포즈 추정 완료!")
    else:
        print(f"오류 발생: {result['error']}")
        exit(1)
