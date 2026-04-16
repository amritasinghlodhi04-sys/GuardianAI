from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, List, Sequence

import numpy as np
import torch
from PIL import Image


@dataclass
class ClipEmbedder:
    """Loads CLIP once and produces L2-normalized image embeddings (cosine = dot)."""

    model: torch.nn.Module
    preprocess: Any
    device: torch.device

    @classmethod
    def create(cls, model_name: str = "ViT-B/32") -> "ClipEmbedder":
        import clip

        device = torch.device(
            "cuda"
            if torch.cuda.is_available()
            else ("mps" if torch.backends.mps.is_available() else "cpu")
        )
        model, preprocess = clip.load(model_name, device=device)
        model.eval()
        return cls(model=model, preprocess=preprocess, device=device)

    def embed_image_paths(self, paths: Sequence[Path], batch_size: int = 8) -> np.ndarray:
        """Returns float32 array shape (N, D), L2-normalized rows."""
        if not paths:
            return np.zeros((0, 512), dtype=np.float32)
        out: List[np.ndarray] = []
        for i in range(0, len(paths), batch_size):
            batch = paths[i : i + batch_size]
            tensors = torch.stack([self.preprocess(Image.open(p).convert("RGB")) for p in batch]).to(
                self.device
            )
            with torch.no_grad():
                feats = self.model.encode_image(tensors).float()
                feats = feats / feats.norm(dim=-1, keepdim=True)
            out.append(feats.cpu().numpy())
        return np.vstack(out)

    def embed_pil_images(self, images: Iterable[Image.Image]) -> np.ndarray:
        ims = list(images)
        if not ims:
            return np.zeros((0, 512), dtype=np.float32)
        tensors = torch.stack([self.preprocess(im.convert("RGB")) for im in ims]).to(self.device)
        with torch.no_grad():
            feats = self.model.encode_image(tensors).float()
            feats = feats / feats.norm(dim=-1, keepdim=True)
        return feats.cpu().numpy()
