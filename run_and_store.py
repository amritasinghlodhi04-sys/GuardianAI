from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from guardianai.embedder import ClipEmbedder
from guardianai.gemini_report import try_generate_report
from guardianai.pipeline import CheckResult, run_check


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="run_and_store",
        description="Run GuardianAI check and store structured output for backend use.",
    )
    p.add_argument("-i", "--input", required=True, type=Path, help="Official image/video path.")
    p.add_argument("--ig-user", type=str, default=None, help="Public Instagram username.")
    p.add_argument("--offline-images", type=Path, default=None, help="Local candidate images directory.")
    p.add_argument("--max-posts", type=int, default=8, help="Max IG posts to scan.")
    p.add_argument("--max-frames", type=int, default=8, help="Max video frames to sample.")
    p.add_argument("--threshold", type=float, default=0.88, help="Similarity threshold.")
    p.add_argument("--report", action="store_true", help="Generate optional Gemini narrative.")
    p.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs"),
        help="Directory for saved JSON results (default: outputs).",
    )
    return p


def _build_payload(args: argparse.Namespace, result: CheckResult, report: str | None) -> dict[str, Any]:
    mode = "offline-images" if args.offline_images is not None else "instagram"
    payload: dict[str, Any] = {
        "run_id": _run_id(),
        "created_at": _utc_now_iso(),
        "input": str(args.input),
        "mode": mode,
        "candidate_source": str(args.offline_images) if args.offline_images else (args.ig_user or ""),
        "threshold": float(args.threshold),
        "query_is_video": bool(result.query_is_video),
        "num_queries": int(result.num_queries),
        "num_candidates": int(result.num_candidates),
        "best_similarity": float(result.best_score),
        "closest_candidate_file": str(result.candidate_path) if result.candidate_path else None,
        "query_idx": int(result.query_idx),
        "candidate_idx": int(result.candidate_idx),
        "potential_misuse": bool(result.violation),
        "instagram_user": args.ig_user,
        "gemini_summary": report,
    }
    return payload


def _write_outputs(output_dir: Path, payload: dict[str, Any]) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    latest_path = output_dir / "latest.json"
    history_path = output_dir / "results.jsonl"

    latest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    with history_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")

    return latest_path, history_path


def main() -> int:
    load_dotenv()
    args = build_parser().parse_args()

    if args.offline_images is None and not args.ig_user:
        raise SystemExit("Error: provide --ig-user or --offline-images.")

    embedder = ClipEmbedder.create()
    result = run_check(
        media_path=args.input,
        threshold=args.threshold,
        ig_username=args.ig_user,
        offline_images_dir=args.offline_images,
        max_posts=args.max_posts,
        max_frames=args.max_frames,
        embedder=embedder,
    )

    report: str | None = None
    if args.report:
        desc = f"{'video' if result.query_is_video else 'image'}:{Path(args.input).name}"
        match_ref = str(result.candidate_path) if result.candidate_path else "unknown"
        report = try_generate_report(
            official_description=desc,
            match_path=match_ref,
            similarity=result.best_score,
            ig_username=args.ig_user,
        )

    payload = _build_payload(args, result, report)
    latest_path, history_path = _write_outputs(args.output_dir, payload)

    print(f"Saved latest result: {latest_path}")
    print(f"Appended history: {history_path}")
    print(f"Potential misuse: {'YES' if result.violation else 'NO'}")
    print(f"Best similarity: {result.best_score:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

