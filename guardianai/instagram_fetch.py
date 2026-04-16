from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import List

_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def download_public_profile_images(username: str, max_posts: int, dest: Path | None = None) -> Path:
    """
    Download images from a *public* Instagram profile using Instaloader (free, no official API).
    Returns a directory tree containing downloaded image files.
    """
    import instaloader

    dest = dest or Path(tempfile.mkdtemp(prefix="guardianai_ig_"))
    dest.mkdir(parents=True, exist_ok=True)

    loader = instaloader.Instaloader(
        download_pictures=True,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
    )

    profile = instaloader.Profile.from_username(loader.context, username)
    count = 0
    for post in profile.get_posts():
        if count >= max_posts:
            break
        loader.download_post(post, target=str(dest))
        count += 1

    return dest


def collect_images_recursive(root: Path) -> List[Path]:
    """Collect image paths under root (recursive)."""
    out: List[Path] = []
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() in _IMAGE_SUFFIXES:
            out.append(p)
    return out


def safe_rmtree(path: Path) -> None:
    if path.exists() and path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
