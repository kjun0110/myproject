# 이미지 파일을 app/data/yolo 디렉토리에 저장 후 YOLO 감지 수행
# FastAPI 서버 기능 포함
import os
import sys
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from yolo_detection import detect_faces, detect_objects
from yolo_segment import detect_face_segment
from yolo_pose import detect_pose
from yolo_class import classify_image


class DetectRequest(BaseModel):
    filename: str


app = FastAPI(title="YOLO Face Detection API", version="1.0.0")


@app.get("/")
async def root():
    return {"message": "YOLO Face Detection API is running"}


@app.post("/detect")
async def detect_faces_endpoint(request: DetectRequest = Body(...)):
    """
    업로드된 이미지 파일에 대해 얼굴 감지를 수행합니다.

    Args:
        request: JSON body ({"filename": "파일명"})
    """
    try:
        filename = request.filename

        # 원본 파일 경로
        original_dir = os.path.join(
            os.path.dirname(__file__), "..", "data", "yolo", "yolo_original"
        )
        original_dir = os.path.abspath(os.path.normpath(original_dir))
        image_path = os.path.join(original_dir, filename)
        image_path = os.path.abspath(os.path.normpath(image_path))

        # 파일 존재 확인
        if not os.path.exists(image_path):
            raise HTTPException(
                status_code=404, detail=f"파일을 찾을 수 없습니다: {filename}"
            )

        # YOLO 감지 수행
        detection_result = detect_faces(image_path)

        if not detection_result["success"]:
            raise HTTPException(
                status_code=500, detail=detection_result.get("error", "얼굴 감지 실패")
            )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "filename": filename,
                "face_count": detection_result["face_count"],
                "output_path": detection_result["output_path"],
                "message": detection_result["message"],
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/detect-objects")
async def detect_objects_endpoint(request: DetectRequest = Body(...)):
    """
    업로드된 이미지 파일에 대해 일반 객체 감지를 수행합니다.
    (yolov8n.pt 모델 사용)

    Args:
        request: JSON body ({"filename": "파일명"})
    """
    try:
        filename = request.filename

        # 원본 파일 경로
        original_dir = os.path.join(
            os.path.dirname(__file__), "..", "data", "yolo", "yolo_original"
        )
        image_path = os.path.join(original_dir, filename)

        # 파일 존재 확인
        if not os.path.exists(image_path):
            raise HTTPException(
                status_code=404, detail=f"파일을 찾을 수 없습니다: {filename}"
            )

        # YOLO 객체 감지 수행
        detection_result = detect_objects(image_path)

        if not detection_result["success"]:
            raise HTTPException(
                status_code=500, detail=detection_result.get("error", "객체 감지 실패")
            )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "filename": filename,
                "object_count": detection_result["object_count"],
                "output_path": detection_result["output_path"],
                "message": detection_result["message"],
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/detect-segment")
async def detect_segment_endpoint(request: DetectRequest = Body(...)):
    """
    업로드된 이미지 파일에 대해 얼굴 세그멘테이션을 수행합니다.
    (yolov8n-seg.pt 모델 사용)

    Args:
        request: JSON body ({"filename": "파일명"})
    """
    try:
        filename = request.filename

        # 원본 파일 경로
        original_dir = os.path.join(
            os.path.dirname(__file__), "..", "data", "yolo", "yolo_original"
        )
        original_dir = os.path.abspath(os.path.normpath(original_dir))
        image_path = os.path.join(original_dir, filename)
        image_path = os.path.abspath(os.path.normpath(image_path))

        # 파일 존재 확인
        if not os.path.exists(image_path):
            raise HTTPException(
                status_code=404, detail=f"파일을 찾을 수 없습니다: {filename}"
            )

        # YOLO 얼굴 세그멘테이션 수행
        detection_result = detect_face_segment(image_path)

        if not detection_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=detection_result.get("error", "얼굴 세그멘테이션 실패"),
            )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "filename": filename,
                "face_count": detection_result["face_count"],
                "output_path": detection_result["output_path"],
                "message": detection_result["message"],
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/detect-pose")
async def detect_pose_endpoint(request: DetectRequest = Body(...)):
    """
    업로드된 이미지 파일에 대해 포즈 추정을 수행합니다.
    (yolov8n-pose.pt 모델 사용)

    Args:
        request: JSON body ({"filename": "파일명"})
    """
    try:
        filename = request.filename

        # 원본 파일 경로
        original_dir = os.path.join(
            os.path.dirname(__file__), "..", "data", "yolo", "yolo_original"
        )
        original_dir = os.path.abspath(os.path.normpath(original_dir))
        image_path = os.path.join(original_dir, filename)
        image_path = os.path.abspath(os.path.normpath(image_path))

        # 파일 존재 확인
        if not os.path.exists(image_path):
            raise HTTPException(
                status_code=404, detail=f"파일을 찾을 수 없습니다: {filename}"
            )

        # YOLO 포즈 추정 수행
        detection_result = detect_pose(image_path)

        if not detection_result["success"]:
            raise HTTPException(
                status_code=500, detail=detection_result.get("error", "포즈 추정 실패")
            )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "filename": filename,
                "person_count": detection_result["person_count"],
                "output_path": detection_result["output_path"],
                "message": detection_result["message"],
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/detect-classify")
async def classify_image_endpoint(request: DetectRequest = Body(...)):
    """
    업로드된 이미지 파일에 대해 이미지 분류를 수행합니다.
    (yolov8n-cls.pt 모델 사용)

    Args:
        request: JSON body ({"filename": "파일명"})
    """
    try:
        filename = request.filename

        # 원본 파일 경로
        original_dir = os.path.join(
            os.path.dirname(__file__), "..", "data", "yolo", "yolo_original"
        )
        original_dir = os.path.abspath(os.path.normpath(original_dir))
        image_path = os.path.join(original_dir, filename)
        image_path = os.path.abspath(os.path.normpath(image_path))

        # 파일 존재 확인
        if not os.path.exists(image_path):
            raise HTTPException(
                status_code=404, detail=f"파일을 찾을 수 없습니다: {filename}"
            )

        # YOLO 이미지 분류 수행
        classification_result = classify_image(image_path)

        if not classification_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=classification_result.get("error", "이미지 분류 실패"),
            )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "filename": filename,
                "top_classes": classification_result["top_classes"],
                "output_path": classification_result["output_path"],
                "message": classification_result["message"],
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download")
async def download_file(path: str):
    """
    감지된 이미지 파일을 다운로드합니다.
    """
    from fastapi.responses import FileResponse

    # 파일 경로 검증 및 보안 확인
    import pathlib

    base_dir = pathlib.Path(__file__).parent.parent / "data" / "yolo"

    # 경로에서 파일명만 추출하여 보안 강화
    # path는 "yolo_detection/filename.jpg" 형태로 들어올 수 있음
    path_parts = pathlib.Path(path).parts
    file_path = base_dir
    for part in path_parts:
        if part in ("..", "."):
            from fastapi import HTTPException

            raise HTTPException(status_code=403, detail="접근이 거부되었습니다.")
        file_path = file_path / part

    # 경로 탐색 공격 방지 (base_dir 내부인지 확인)
    try:
        file_path.resolve().relative_to(base_dir.resolve())
    except ValueError:
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="접근이 거부되었습니다.")

    if not file_path.exists():
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")

    return FileResponse(
        str(file_path), media_type="image/jpeg", filename=file_path.name
    )


@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    파일을 업로드합니다. (얼굴 감지는 별도 /detect 엔드포인트에서 수행)
    """
    if not files or len(files) == 0:
        raise HTTPException(status_code=400, detail="파일이 제공되지 않았습니다.")

    results = []

    for file in files:
        try:
            # 대상 디렉토리 경로 (data/yolo/yolo_original)
            target_dir = os.path.join(
                os.path.dirname(__file__), "..", "data", "yolo", "yolo_original"
            )
            os.makedirs(target_dir, exist_ok=True)

            # 원본 파일명으로 대상 파일 경로 생성
            original_filename = file.filename
            target_file_path = os.path.join(target_dir, original_filename)

            # 같은 이름의 파일이 이미 존재하면 숫자를 추가하여 충돌 방지
            base_name, ext = os.path.splitext(original_filename)
            counter = 1
            while os.path.exists(target_file_path):
                new_filename = f"{base_name}_{counter}{ext}"
                target_file_path = os.path.join(target_dir, new_filename)
                counter += 1

            # 업로드된 파일 내용을 직접 대상 경로에 저장
            contents = await file.read()
            with open(target_file_path, "wb") as target_file:
                target_file.write(contents)

            # 파일 저장 성공 (YOLO 감지는 별도 엔드포인트에서 수행)
            results.append(
                {
                    "filename": file.filename,
                    "success": True,
                    "target_file": target_file_path,
                    "message": "파일이 성공적으로 업로드되었습니다.",
                }
            )

        except Exception as e:
            results.append(
                {"filename": file.filename, "success": False, "error": str(e)}
            )

    # 성공한 파일이 하나라도 있으면 성공 응답
    has_success = any(r["success"] for r in results)

    return JSONResponse(
        status_code=200 if has_success else 500,
        content={"success": has_success, "results": results},
    )


def process_file(source_file: str) -> dict:
    """
    파일에 대해 YOLO 감지를 수행합니다.
    파일이 이미 data/yolo/yolo_original 디렉토리에 있다고 가정합니다.

    Args:
        source_file: 파일 경로 (이미 data/yolo/yolo_original에 있는 파일)

    Returns:
        dict: {
            'success': bool,
            'target_file': str,
            'detection_result': dict,
            'error': str (optional)
        }
    """
    try:
        # 파일이 존재하는지 확인
        if not os.path.exists(source_file):
            return {
                "success": False,
                "target_file": "",
                "detection_result": None,
                "error": f"파일을 찾을 수 없습니다: {source_file}",
            }

        # YOLO 감지 수행 (파일 이동 없이 바로 감지)
        detection_result = detect_faces(source_file)

        if not detection_result["success"]:
            return {
                "success": False,
                "target_file": source_file,
                "detection_result": detection_result,
                "error": detection_result.get("error", "YOLO 감지 실패"),
            }

        return {
            "success": True,
            "target_file": source_file,
            "detection_result": detection_result,
            "error": None,
        }

    except Exception as e:
        import traceback

        traceback.print_exc()
        return {
            "success": False,
            "target_file": "",
            "detection_result": None,
            "error": str(e),
        }


if __name__ == "__main__":
    # 명령줄 인자가 없으면 FastAPI 서버 실행
    if len(sys.argv) < 2:
        import uvicorn

        print("FastAPI 서버를 시작합니다...")
        print("서버 주소: http://0.0.0.0:9100")
        uvicorn.run(app, host="0.0.0.0", port=9100)
    else:
        # 명령줄 인자가 있으면 파일 처리 모드
        source_file = sys.argv[1]
        result = process_file(source_file)

        if result["success"]:
            print(f"파일 처리 완료!")
            print(f"파일: {source_file}")
            print(f"\n{result['detection_result']['message']}")
            if result["detection_result"]["output_path"]:
                print(f"결과 이미지: {result['detection_result']['output_path']}")
            print("처리 완료!")
        else:
            print(f"오류 발생: {result['error']}")
            exit(1)
