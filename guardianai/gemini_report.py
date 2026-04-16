from __future__ import annotations

import os
from typing import Optional


def try_generate_report(
    *,
    official_description: str,
    match_path: str,
    similarity: float,
    ig_username: Optional[str],
) -> Optional[str]:
    """
    Uses Google Gemini (free tier via AI Studio API key). Returns None if unavailable.
    """
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        return None

    import google.generativeai as genai

    genai.configure(api_key=key)
    requested_model = os.environ.get("GEMINI_MODEL", "").strip()
    # Try user-selected model first, then sensible fallbacks for newer accounts.
    candidates = [m for m in [requested_model, "gemini-2.0-flash", "gemini-flash-latest"] if m]

    prompt = f"""You are assisting with a prototype "digital media protection" demo for a hackathon.
A similarity match was found between user-provided official media and content discovered online.

Context:
- User media: {official_description}
- Suspected match file/path or URL context: {match_path}
- Cosine similarity (CLIP ViT-B/32, higher is more similar): {similarity:.4f}
- Instagram profile checked (if any): {ig_username or "N/A"}

Write a short, professional summary (bullet points) with:
1) What the match might mean (possible misuse vs coincidental similarity — be cautious).
2) Suggested next verification steps (human review, takedown process disclaimer: legal review required).
3) Urgency: Low / Medium / High with one-line rationale.

Keep under 180 words. Do not claim legal certainty."""

    last_error: Optional[Exception] = None
    for model_name in candidates:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            text = getattr(response, "text", None) or ""
            cleaned = text.strip()
            if cleaned:
                return cleaned
        except Exception as e:
            last_error = e
            continue

    if last_error is not None:
        return f"(Gemini failed: {last_error})"
    return None
