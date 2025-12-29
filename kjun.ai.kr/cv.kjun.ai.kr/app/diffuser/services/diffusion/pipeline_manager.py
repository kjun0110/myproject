# 모델을 서버 시작 후 1번만 로딩하고 재사용합니다.
# 6GB에서 필요한 옵션(슬라이싱/타일링) 기본 적용입니다.

import torch
from diffusers import AutoPipelineForText2Image

# 절대 임포트 시도, 실패하면 상대 임포트 사용
try:
    from core.config import MODEL_ID, DEVICE, DTYPE, HF_CACHE_DIR
except ImportError:
    from ...core.config import MODEL_ID, DEVICE, DTYPE, HF_CACHE_DIR

_PIPELINE = None


def _torch_dtype():
    if DTYPE.lower() == "float16":
        return torch.float16
    if DTYPE.lower() == "bfloat16":
        return torch.bfloat16
    return torch.float32


def get_pipeline():
    global _PIPELINE
    if _PIPELINE is not None:
        return _PIPELINE

    dtype = _torch_dtype()

    pipe = AutoPipelineForText2Image.from_pretrained(
        MODEL_ID,
        torch_dtype=dtype,
        cache_dir=str(HF_CACHE_DIR),
        variant="fp16" if dtype in (torch.float16, torch.bfloat16) else None,
        use_safetensors=True,
    )

    # RTX 3050 6GB 안정 옵션
    try:
        pipe.enable_attention_slicing()  # 메모리 절약(속도 약간 감소)
    except Exception:
        pass

    try:
        pipe.vae.enable_tiling()  # 고해상도/VRAM 부족 시 안정 (deprecated 경고 수정)
    except Exception:
        pass

    # VAE를 float32로 명시적 변환 (upcast_vae deprecated 경고 해결)
    try:
        pipe.vae.to(torch.float32)
    except Exception:
        pass

    # 가능하면 xformers (설치되어 있을 때만)
    try:
        pipe.enable_xformers_memory_efficient_attention()
    except Exception:
        pass

    if DEVICE == "cuda" and torch.cuda.is_available():
        pipe = pipe.to("cuda")
    else:
        pipe = pipe.to("cpu")

    _PIPELINE = pipe
    return _PIPELINE
