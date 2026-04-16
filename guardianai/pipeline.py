from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from guardianai.embedder import ClipEmbedder
from guardianai.instagram_fetch import collect_images_recursive, download_public_profile_images, safe_rmtree
from guardianai.similarity import best_match_score
from guardianai.video import extract_frames


VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".webm", ".mkv"}


@dataclass
class CheckResult:
    violation: bool
    best_score: float
    query_idx: int
    candidate_idx: int
    candidate_path: Optional[Path]
    query_is_video: bool
    num_queries: int
    num_candidates: int


def run_check(
    *,
    media_path: Path,
    threshold: float,
    ig_username: Optional[str],
    offline_images_dir: Optional[Path],
    max_posts: int,
    max_frames: int,
    embedder: ClipEmbedder,
) -> CheckResult:
    media_path = media_path.expanduser().resolve()
    if not media_path.is_file():
        raise FileNotFoundError(media_path)

    is_video = media_path.suffix.lower() in VIDEO_EXTENSIONS

    if is_video:
        frames = extract_frames(media_path, max_frames=max_frames)
        query_embs = embedder.embed_pil_images(frames)
    else:
        query_embs = embedder.embed_image_paths([media_path])

    ig_dir: Optional[Path] = None
    try:
        if offline_images_dir is not None:
            cand_root = offline_images_dir.expanduser().resolve()
            if not cand_root.is_dir():
                raise NotADirectoryError(cand_root)
        else:
            if not ig_username:
                raise ValueError("Provide --ig-user or --offline-images.")
            ig_dir = download_public_profile_images(ig_username.strip().lstrip("@"), max_posts, dest=None)
            cand_root = ig_dir

        cand_paths = collect_images_recursive(cand_root)
        if not cand_paths:
            raise RuntimeError(
                "No candidate images found. For Instagram: profile may be private, blocked, "
                "or rate-limited — try --offline-images with a folder of test images."
            )

        cand_embs = embedder.embed_image_paths(cand_paths)
        score, qi, ci = best_match_score(query_embs, cand_embs)
        cand_path = cand_paths[ci] if ci >= 0 else None

        return CheckResult(
            violation=score >= threshold,
            best_score=score,
            query_idx=qi,
            candidate_idx=ci,
            candidate_path=cand_path,
            query_is_video=is_video,
            num_queries=int(query_embs.shape[0]),
            num_candidates=int(cand_embs.shape[0]),
        )
    finally:
        if ig_dir is not None:
            safe_rmtree(ig_dir)


def format_result_lines(
    result: CheckResult,
    threshold: float,
    media_path: Path,
    ig_username: Optional[str],
    report: Optional[str],
) -> List[str]:
    lines: List[str] = [
        "",
        "=== GuardianAI prototype result ===",
        f"Official media: {media_path}",
        f"Mode: {'video (frames)' if result.query_is_video else 'image'} — query vectors: {result.num_queries}",
        f"Candidates compared: {result.num_candidates}",
        f"Best cosine similarity: {result.best_score:.4f} (threshold: {threshold:.4f})",
    ]
    if result.candidate_path:
        lines.append(f"Closest candidate file: {result.candidate_path}")
    lines.append(f"Flag as potential misuse (prototype): {'YES' if result.violation else 'NO'}")
    if ig_username:
        lines.append(f"Instagram profile sampled: @{ig_username.lstrip('@')}")
    if report:
        lines.extend(["", "--- Gemini summary (optional) ---", report])
    lines.append("")
    return lines
