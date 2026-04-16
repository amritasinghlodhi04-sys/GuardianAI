from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from guardianai.embedder import ClipEmbedder
from guardianai.gemini_report import try_generate_report
from guardianai.pipeline import format_result_lines, run_check


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="guardianai",
        description=(
            "Prototype: compare your image/video against a public Instagram profile's recent posts "
            "using CLIP similarity (free local model). Optional Gemini report (free API key)."
        ),
    )
    p.add_argument(
        "-i",
        "--input",
        required=True,
        type=Path,
        help="Path to official image (.jpg/.png/…) or video (.mp4/.mov/…).",
    )
    p.add_argument(
        "--ig-user",
        type=str,
        default=None,
        help="Public Instagram username (no @). Not used if --offline-images is set.",
    )
    p.add_argument(
        "--offline-images",
        type=Path,
        default=None,
        help="Folder of images to compare against (skips Instagram; best for reliable demos).",
    )
    p.add_argument(
        "--max-posts",
        type=int,
        default=8,
        help="Max Instagram posts to download from the top of the profile grid (default: 8).",
    )
    p.add_argument(
        "--max-frames",
        type=int,
        default=8,
        help="Max video frames to sample for embedding (default: 8).",
    )
    p.add_argument(
        "--threshold",
        type=float,
        default=0.88,
        help="Cosine similarity threshold for flagging (default: 0.88). Tune per dataset.",
    )
    p.add_argument(
        "--report",
        action="store_true",
        help="If GEMINI_API_KEY is set, ask Gemini for a short summary (free tier).",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    args = build_parser().parse_args(argv)
    if args.offline_images is None and not args.ig_user:
        print("Error: provide --ig-user or --offline-images.", file=sys.stderr)
        return 2

    print("Loading CLIP (first run downloads weights)…", flush=True)
    embedder = ClipEmbedder.create()

    try:
        result = run_check(
            media_path=args.input,
            threshold=args.threshold,
            ig_username=args.ig_user,
            offline_images_dir=args.offline_images,
            max_posts=args.max_posts,
            max_frames=args.max_frames,
            embedder=embedder,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    report = None
    if args.report:
        desc = f"{'video' if result.query_is_video else 'image'}:{args.input.name}"
        match_ref = str(result.candidate_path) if result.candidate_path else "unknown"
        report = try_generate_report(
            official_description=desc,
            match_path=match_ref,
            similarity=result.best_score,
            ig_username=args.ig_user,
        )
        if report is None:
            report = "(Gemini skipped: set GEMINI_API_KEY in environment or .env)"

    for line in format_result_lines(
        result,
        threshold=args.threshold,
        media_path=args.input,
        ig_username=args.ig_user,
        report=report,
    ):
        print(line)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
