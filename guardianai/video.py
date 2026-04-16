from __future__ import annotations

from pathlib import Path
from typing import List

import cv2
import numpy as np
from PIL import Image


def extract_frames(path: Path, max_frames: int = 8) -> List[Image.Image]:
    """Sample up to `max_frames` evenly spaced RGB frames from a video file."""
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {path}")

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    if total <= 0:
        ret, frame = cap.read()
        cap.release()
        if not ret or frame is None:
            raise RuntimeError(f"No frames readable from video: {path}")
        return [_bgr_to_pil(frame)]

    indices = _even_indices(total, max_frames)
    frames: List[Image.Image] = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret and frame is not None:
            frames.append(_bgr_to_pil(frame))
    cap.release()
    if not frames:
        raise RuntimeError(f"Could not decode frames from: {path}")
    return frames


def _even_indices(total: int, max_frames: int) -> List[int]:
    if max_frames <= 0:
        return []
    if total <= max_frames:
        return list(range(total))
    if max_frames == 1:
        return [total // 2]
    return [int(round(i * (total - 1) / (max_frames - 1))) for i in range(max_frames)]


def _bgr_to_pil(bgr: np.ndarray) -> Image.Image:
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)
