"""
Generate campaign images and an asset manifest for RAG pipeline testing.

Produces ~50 branded PNG images organized by channel in data/assets/{channel}/,
plus a CSV manifest at data/assets/asset_manifest.csv.

Default mode: Pillow gradient backgrounds (free, offline).
AI mode:      Photorealistic images via OpenAI gpt-image-1.5 (opt-in).

Usage:
    .venv/bin/python -m data.generators.assets           # Pillow (default)
    .venv/bin/python -m data.generators.assets --ai      # AI mode
    ASSET_GEN_AI=1 .venv/bin/python -m data.generators.assets  # AI via env
"""

import argparse
import base64
import csv
import io
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from data.generators.config import (
    AUDIENCE_SEGMENTS,
    PROJECT_ROOT,
    RANDOM_SEED,
    VEHICLE_MODELS,
)

# ---------------------------------------------------------------------------
# Paths & constants
# ---------------------------------------------------------------------------
ASSETS_DIR = os.path.join(PROJECT_ROOT, "data", "assets")

ASSET_GEN_AI_ENV = "ASSET_GEN_AI"
_AI_MODEL = "gpt-image-1.5"
_AI_MAX_FAILURES = 3

# Brand colours (Pillow fallback)
BRAND_BLUE = (0, 85, 255)
BRAND_DARK = (0, 17, 51)
TEXT_WHITE = (255, 255, 255)
TEXT_LIGHT = (200, 220, 255)

# Channel image specs: (count, list of creative_types)
CHANNEL_SPECS = {
    "meta":     (8, ["Social Post", "Story Ad", "Carousel", "Reel Cover"]),
    "google":   (6, ["Display Ad", "Search Ad", "Responsive Ad"]),
    "tv":       (6, ["TV Still", "Bumper Frame", "Sponsorship Slate"]),
    "ooh":      (6, ["Billboard Mockup", "Bus Shelter", "Digital Screen"]),
    "youtube":  (5, ["Thumbnail", "Bumper Frame", "Masthead Banner"]),
    "tiktok":   (5, ["Vertical Still", "TopView Frame", "Spark Ad"]),
    "linkedin": (4, ["Sponsored Content", "Message Ad", "Carousel"]),
    "dv360":    (4, ["Programmatic Display", "Native Ad", "Rich Media"]),
    "print":    (3, ["Magazine Full Page", "Magazine DPS", "Advertorial"]),
    "radio":    (3, ["Podcast Artwork", "Station Ident", "Audio Ad Cover"]),
}

PILLOW_WIDTH = 800
PILLOW_HEIGHT = 600


# ---------------------------------------------------------------------------
# OpenAI client (lazy init)
# ---------------------------------------------------------------------------
_openai_client = None


def _init_openai_client():
    """Lazily initialise and return the OpenAI client."""
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI
        _openai_client = OpenAI()  # reads OPENAI_API_KEY from env
    return _openai_client


# ---------------------------------------------------------------------------
# AI image generation
# ---------------------------------------------------------------------------

def _generate_ai_image(prompt: str, size: str) -> Image.Image:
    """Call OpenAI gpt-image-1.5 and return a PIL Image."""
    client = _init_openai_client()
    response = client.images.generate(
        model=_AI_MODEL,
        prompt=prompt,
        n=1,
        size=size,
        response_format="b64_json",
    )
    b64_data = response.data[0].b64_json
    img_bytes = base64.b64decode(b64_data)
    return Image.open(io.BytesIO(img_bytes)).convert("RGB")


# ---------------------------------------------------------------------------
# Pillow fallback image generation
# ---------------------------------------------------------------------------

def _make_gradient(width: int, height: int) -> Image.Image:
    """Create a vertical gradient from BRAND_BLUE (top) to BRAND_DARK (bottom)."""
    t = np.linspace(0, 1, height).reshape(-1, 1)
    top = np.array(BRAND_BLUE, dtype=np.float64)
    bot = np.array(BRAND_DARK, dtype=np.float64)
    gradient = ((1 - t) * top + t * bot).astype(np.uint8)
    arr = np.broadcast_to(gradient[:, np.newaxis, :], (height, width, 3)).copy()
    return Image.fromarray(arr, "RGB")


def _load_font(size: int) -> ImageFont.ImageFont:
    """Load a TrueType font, falling back to default if unavailable."""
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    ]:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _draw_text_centered(draw: ImageDraw.Draw, y: int, text: str,
                        font: ImageFont.ImageFont, fill: tuple,
                        img_width: int) -> None:
    """Draw text horizontally centred at a given y position."""
    bbox = draw.textbbox((0, 0), text, font=font)
    x = (img_width - (bbox[2] - bbox[0])) // 2
    draw.text((x, y), text, fill=fill, font=font)


def _generate_pillow_image(channel: str, vehicle_display: str,
                           creative_type: str, audience: str,
                           gradient: Image.Image, fonts: dict) -> Image.Image:
    """Render a branded Pillow placeholder image."""
    img = gradient.copy()
    draw = ImageDraw.Draw(img)
    w, h = PILLOW_WIDTH, PILLOW_HEIGHT

    draw.rectangle([0, 0, w, 6], fill=TEXT_WHITE)
    draw.text((30, 30), channel.upper(), fill=TEXT_LIGHT, font=fonts["small"])

    dim_text = f"{w}x{h}"
    dim_bbox = draw.textbbox((0, 0), dim_text, font=fonts["tiny"])
    draw.text((w - (dim_bbox[2] - dim_bbox[0]) - 30, 30),
              dim_text, fill=TEXT_LIGHT, font=fonts["tiny"])

    _draw_text_centered(draw, 180, vehicle_display, fonts["large"], TEXT_WHITE, w)
    _draw_text_centered(draw, 260, creative_type, fonts["medium"], TEXT_LIGHT, w)
    _draw_text_centered(draw, 340, audience.replace("_", " ").title(),
                        fonts["small"], TEXT_LIGHT, w)

    draw.rectangle([0, h - 60, w, h], fill=BRAND_DARK)
    _draw_text_centered(draw, h - 48, "DEEPAL | AVATR  UK 2025",
                        fonts["small"], TEXT_LIGHT, w)
    return img


# ---------------------------------------------------------------------------
# Description builder
# ---------------------------------------------------------------------------

_CHANNEL_LABELS = {
    "meta": "Meta social campaigns", "google": "Google Ads network",
    "tv": "broadcast television spots", "ooh": "out-of-home placements",
    "youtube": "YouTube video campaigns", "tiktok": "TikTok short-form video",
    "linkedin": "LinkedIn B2B campaigns", "dv360": "DV360 programmatic display",
    "print": "print media publications", "radio": "radio and podcast channels",
}

_AUDIENCE_LABELS = {
    "EV_INTENDERS": "EV intenders", "PREMIUM_AUTO": "premium auto buyers",
    "TECH_ENTHUSIASTS": "tech enthusiasts", "ECO_CONSCIOUS": "eco-conscious consumers",
    "LUXURY_LIFESTYLE": "luxury lifestyle audiences", "YOUNG_PROFESSIONALS": "young professionals",
    "FAMILY_BUYERS": "family buyers", "FLEET_MANAGERS": "fleet managers",
    "CONQUEST_TESLA": "Tesla conquest segment", "CONQUEST_BMW": "BMW conquest segment",
    "CONQUEST_AUDI": "Audi conquest segment", "LOOKALIKE_CONVERTERS": "lookalike converter audiences",
    "SITE_VISITORS": "website retargeting visitors", "CONFIGURATOR_USERS": "configurator users",
    "ENGAGED_VIEWERS": "engaged video viewers",
}

_CREATIVE_LABELS = {
    "Social Post": "social post creative", "Story Ad": "story format ad",
    "Carousel": "carousel creative", "Reel Cover": "reel cover image",
    "Display Ad": "display banner", "Search Ad": "search ad creative",
    "Responsive Ad": "responsive display creative", "TV Still": "TV commercial still frame",
    "Bumper Frame": "bumper ad frame", "Sponsorship Slate": "sponsorship slate graphic",
    "Billboard Mockup": "billboard mockup", "Bus Shelter": "bus shelter poster",
    "Digital Screen": "digital OOH screen", "Thumbnail": "video thumbnail",
    "Masthead Banner": "masthead banner", "Vertical Still": "vertical video still",
    "TopView Frame": "TopView format frame", "Spark Ad": "Spark Ad creative",
    "Sponsored Content": "sponsored content image", "Message Ad": "message ad creative",
    "Programmatic Display": "programmatic display banner", "Native Ad": "native ad creative",
    "Rich Media": "rich media unit", "Magazine Full Page": "full-page magazine ad",
    "Magazine DPS": "double-page spread", "Advertorial": "advertorial layout",
    "Podcast Artwork": "podcast artwork tile", "Station Ident": "station ident graphic",
    "Audio Ad Cover": "audio ad cover image",
}


def _build_description(channel: str, vehicle_display: str,
                       creative_type: str, audience: str) -> str:
    """Build a detailed text caption for the asset manifest."""
    ch = _CHANNEL_LABELS.get(channel, f"{channel} campaigns")
    aud = _AUDIENCE_LABELS.get(audience, audience.replace("_", " ").lower())
    cr = _CREATIVE_LABELS.get(creative_type, creative_type.lower())
    return (
        f"Hero launch {cr} for {vehicle_display} — "
        f"lifestyle shot targeting {aud}, "
        f"used in {ch}, September 2025 UK launch"
    )


def _generate_campaign_id(channel: str, model_key: str, idx: int,
                          rng: np.random.Generator) -> str:
    """Generate a plausible campaign ID string."""
    model_short = model_key.replace("DEEPAL_", "").replace("AVATR_", "A")
    suffix = rng.integers(1000, 9999)
    return f"{channel.upper()}_GB_{model_short}_{idx:02d}_{suffix}"


# ---------------------------------------------------------------------------
# Main generation
# ---------------------------------------------------------------------------

def generate(*, use_ai: bool | None = None) -> None:
    """Generate ~50 campaign images and asset manifest CSV.

    Args:
        use_ai: True to use OpenAI gpt-image-1.5, False for Pillow.
                None (default) checks the ASSET_GEN_AI env var.
    """
    if use_ai is None:
        use_ai = os.environ.get(ASSET_GEN_AI_ENV, "0").strip() in ("1", "true", "yes")

    rng = np.random.default_rng(RANDOM_SEED + 99)

    # Ensure output directories
    os.makedirs(ASSETS_DIR, exist_ok=True)
    for ch in CHANNEL_SPECS:
        os.makedirs(os.path.join(ASSETS_DIR, ch), exist_ok=True)

    # Pillow resources (always needed for fallback)
    gradient = _make_gradient(PILLOW_WIDTH, PILLOW_HEIGHT)
    fonts = {
        "large": _load_font(42), "medium": _load_font(28),
        "small": _load_font(20), "tiny": _load_font(16),
    }

    # AI prompt data (loaded only when needed)
    ai_prompts = None
    if use_ai:
        from data.generators._asset_prompts import AI_SIZES, build_ai_prompt
        ai_prompts = (AI_SIZES, build_ai_prompt)
        print("    Mode: AI (gpt-image-1.5)")
    else:
        print("    Mode: Pillow (offline)")

    ai_failures = 0
    model_keys = list(VEHICLE_MODELS.keys())
    manifest_rows = []

    for channel, (count, creative_types) in CHANNEL_SPECS.items():
        for i in range(count):
            model_key = model_keys[rng.integers(0, len(model_keys))]
            vehicle = VEHICLE_MODELS[model_key]
            vehicle_display = vehicle["display_name"]
            creative_type = creative_types[i % len(creative_types)]
            audience = AUDIENCE_SEGMENTS[rng.integers(0, len(AUDIENCE_SEGMENTS))]

            filename = (
                f"{channel}_{model_key.lower()}_{creative_type.lower().replace(' ', '_')}"
                f"_{i + 1:02d}.png"
            )
            filepath = os.path.join(ASSETS_DIR, channel, filename)

            # Determine dimensions and attempt generation
            used_ai = False

            if use_ai and ai_failures < _AI_MAX_FAILURES:
                ai_sizes, prompt_builder = ai_prompts
                size_str = ai_sizes.get(channel, "1024x1024")

                # Cache check: skip if file already exists
                if os.path.exists(filepath):
                    print(f"    [cached] {channel}/{filename}")
                    img = Image.open(filepath)
                    w, h = img.size
                    used_ai = True
                else:
                    prompt = prompt_builder(
                        channel, model_key, creative_type, audience, vehicle_display,
                    )
                    try:
                        img = _generate_ai_image(prompt, size_str)
                        img.save(filepath, "PNG")
                        w, h = img.size
                        used_ai = True
                        ai_failures = 0  # reset on success
                        print(f"    [AI] {channel}/{filename} ({w}x{h})")
                    except Exception as exc:
                        ai_failures += 1
                        print(f"    [AI error {ai_failures}/{_AI_MAX_FAILURES}] {exc}")
                        if ai_failures >= _AI_MAX_FAILURES:
                            print("    Circuit breaker tripped — falling back to Pillow")

            if not used_ai:
                img = _generate_pillow_image(
                    channel, vehicle_display, creative_type, audience, gradient, fonts,
                )
                img.save(filepath, "PNG")
                w, h = PILLOW_WIDTH, PILLOW_HEIGHT

            campaign_id = _generate_campaign_id(channel, model_key, i + 1, rng)
            description = _build_description(channel, vehicle_display, creative_type, audience)
            rel_path = os.path.relpath(filepath, PROJECT_ROOT)

            manifest_rows.append({
                "image_path": rel_path,
                "description": description,
                "channel": channel,
                "vehicle_model": vehicle_display,
                "creative_type": creative_type,
                "audience_segment": audience,
                "campaign_id": campaign_id,
                "dimensions": f"{w}x{h}",
                "file_size": os.path.getsize(filepath),
            })

    # Write manifest CSV
    manifest_path = os.path.join(ASSETS_DIR, "asset_manifest.csv")
    fieldnames = [
        "image_path", "description", "channel", "vehicle_model",
        "creative_type", "audience_segment", "campaign_id",
        "dimensions", "file_size",
    ]
    with open(manifest_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(manifest_rows)

    print(f"    Generated {len(manifest_rows)} images across {len(CHANNEL_SPECS)} channels")
    print(f"    Manifest: {os.path.relpath(manifest_path, PROJECT_ROOT)}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate campaign asset images")
    parser.add_argument(
        "--ai", action="store_true",
        help="Use OpenAI gpt-image-1.5 for photorealistic images (default: Pillow)",
    )
    cli_args = parser.parse_args()

    print("=" * 60)
    print("  ASSET GENERATOR")
    print("=" * 60)
    generate(use_ai=cli_args.ai or None)
    print("\nDone.")
