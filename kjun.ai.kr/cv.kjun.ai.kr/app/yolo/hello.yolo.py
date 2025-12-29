# YOLO11 기본 예제 - 객체 감지 및 결과 이미지 생성
from ultralytics import YOLO
import os

if __name__ == "__main__":
    # YOLO 사전 학습된 모델 로드 (nano 버전 - 가장 빠름)
    # app/data/yolo/model 디렉토리에서 모델 로드
    # YOLOv8 모델 사용 (YOLO11과 호환 가능)
    # 다른 모델 옵션: yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt
    print("YOLO 모델 로딩 중...")

    # 모델 파일 경로 설정 (app/data/yolo/model/yolov8n.pt)
    model_dir = os.path.join(os.path.dirname(__file__), "..", "data", "yolo", "model")
    model_path = os.path.join(model_dir, "yolov8n.pt")

    # 모델 파일이 없으면 기본 위치에서 찾기
    if not os.path.exists(model_path):
        print(f"경고: {model_path}에 모델 파일이 없습니다. 기본 위치에서 찾습니다.")
        model_path = "yolov8n.pt"

    model = YOLO(model_path)  # app/data/yolo/model/yolov8n.pt 사용

    # YOLO 기본 이미지 URL 사용 (로컬 데이터 사용 안 함)
    test_image = "https://ultralytics.com/images/bus.jpg"
    print(f"YOLO 기본 이미지 사용: {test_image}")

    # 객체 감지 수행
    print("YOLO11 객체 감지 시작...")
    results = model(test_image)

    # 결과 이미지 저장
    output_dir = os.path.join(os.path.dirname(__file__), "..", "..")
    output_path = os.path.join(output_dir, "yolo_result.jpg")

    # 결과 이미지 저장 (감지된 객체에 바운딩 박스와 레이블 표시)
    for result in results:
        # 이미지에 바운딩 박스와 레이블이 그려진 결과 저장
        result.save(output_path)
        print(f"결과 이미지가 저장되었습니다: {output_path}")

        # 감지된 객체 정보 출력
        print(f"\n감지된 객체 수: {len(result.boxes)}")
        for i, box in enumerate(result.boxes):
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            name = model.names[cls]
            print(f"  {i + 1}. {name}: {conf:.2%} 신뢰도")

    print("\nYOLO11 객체 감지 완료!")
