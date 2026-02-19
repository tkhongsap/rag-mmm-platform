"""
Generate mock campaign images and an asset manifest for RAG pipeline testing.

Produces ~50 branded PNG images organized by channel in data/assets/{channel}/,
plus a CSV manifest at data/assets/asset_manifest.csv.

Each image: 800x600 with brand gradient background, channel label,
vehicle model name, and creative type overlay.

Usage:
    .venv/bin/python -m data.generators.assets
"""

import csv
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from data.generators.config import (
    ALL_CHANNELS,
    AUDIENCE_SEGMENTS,
    CAMPAIGN_TEMPLATES,
    CREATIVE_IDS,
    DIGITAL_CHANNELS,
    PROJECT_ROOT,
    RANDOM_SEED,
    RNG,
    TRADITIONAL_CHANNELS,
    VEHICLE_MODELS,
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ASSETS_DIR = os.path.join(PROJECT_ROOT, "data", "assets")

# ---------------------------------------------------------------------------
# Brand colours
# ---------------------------------------------------------------------------
BRAND_BLUE = (0, 85, 255)       # #0055FF
BRAND_DARK = (0, 17, 51)        # #001133
TEXT_WHITE = (255, 255, 255)
TEXT_LIGHT = (200, 220, 255)

# ---------------------------------------------------------------------------
# Channel image specs: (count, list of creative_types)
# ---------------------------------------------------------------------------
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

IMG_WIDTH = 800
IMG_HEIGHT = 600

# Month names for description text
_MONTH_NAMES = {
    9: "September", 10: "October", 11: "November", 12: "December",
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_gradient(width: int, height: int) -> Image.Image:
    """Create a vertical gradient from BRAND_BLUE (top) to BRAND_DARK (bottom)."""
    img = Image.new("RGB", (width, height))
    pixels = img.load()
    for y in range(height):
        ratio = y / max(height - 1, 1)
        r = int(BRAND_BLUE[0] + (BRAND_DARK[0] - BRAND_BLUE[0]) * ratio)
        g = int(BRAND_BLUE[1] + (BRAND_DARK[1] - BRAND_BLUE[1]) * ratio)
        b = int(BRAND_BLUE[2] + (BRAND_DARK[2] - BRAND_BLUE[2]) * ratio)
        for x in range(width):
            pixels[x, y] = (r, g, b)
    return img


def _draw_text_centered(draw: ImageDraw.Draw, y: int, text: str,
                        font: ImageFont.ImageFont, fill: tuple,
                        img_width: int) -> None:
    """Draw text horizontally centered at a given y position."""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (img_width - tw) // 2
    draw.text((x, y), text, fill=fill, font=font)


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


def _build_description(channel: str, vehicle_display: str,
                       creative_type: str, audience: str) -> str:
    """Build a detailed text caption for the asset manifest."""
    channel_labels = {
        "meta": "Meta social campaigns",
        "google": "Google Ads network",
        "tv": "broadcast television spots",
        "ooh": "out-of-home placements",
        "youtube": "YouTube video campaigns",
        "tiktok": "TikTok short-form video",
        "linkedin": "LinkedIn B2B campaigns",
        "dv360": "DV360 programmatic display",
        "print": "print media publications",
        "radio": "radio and podcast channels",
    }
    ch_label = channel_labels.get(channel, f"{channel} campaigns")

    audience_labels = {
        "EV_INTENDERS": "EV intenders",
        "PREMIUM_AUTO": "premium auto buyers",
        "TECH_ENTHUSIASTS": "tech enthusiasts",
        "ECO_CONSCIOUS": "eco-conscious consumers",
        "LUXURY_LIFESTYLE": "luxury lifestyle audiences",
        "YOUNG_PROFESSIONALS": "young professionals",
        "FAMILY_BUYERS": "family buyers",
        "FLEET_MANAGERS": "fleet managers",
        "CONQUEST_TESLA": "Tesla conquest segment",
        "CONQUEST_BMW": "BMW conquest segment",
        "CONQUEST_AUDI": "Audi conquest segment",
        "LOOKALIKE_CONVERTERS": "lookalike converter audiences",
        "SITE_VISITORS": "website retargeting visitors",
        "CONFIGURATOR_USERS": "configurator users",
        "ENGAGED_VIEWERS": "engaged video viewers",
    }
    aud_label = audience_labels.get(audience, audience.replace("_", " ").lower())

    creative_labels = {
        "Social Post": "social post creative",
        "Story Ad": "story format ad",
        "Carousel": "carousel creative",
        "Reel Cover": "reel cover image",
        "Display Ad": "display banner",
        "Search Ad": "search ad creative",
        "Responsive Ad": "responsive display creative",
        "TV Still": "TV commercial still frame",
        "Bumper Frame": "bumper ad frame",
        "Sponsorship Slate": "sponsorship slate graphic",
        "Billboard Mockup": "billboard mockup",
        "Bus Shelter": "bus shelter poster",
        "Digital Screen": "digital OOH screen",
        "Thumbnail": "video thumbnail",
        "Masthead Banner": "masthead banner",
        "Vertical Still": "vertical video still",
        "TopView Frame": "TopView format frame",
        "Spark Ad": "Spark Ad creative",
        "Sponsored Content": "sponsored content image",
        "Message Ad": "message ad creative",
        "Programmatic Display": "programmatic display banner",
        "Native Ad": "native ad creative",
        "Rich Media": "rich media unit",
        "Magazine Full Page": "full-page magazine ad",
        "Magazine DPS": "double-page spread",
        "Advertorial": "advertorial layout",
        "Podcast Artwork": "podcast artwork tile",
        "Station Ident": "station ident graphic",
        "Audio Ad Cover": "audio ad cover image",
    }
    cr_label = creative_labels.get(creative_type, creative_type.lower())

    return (
        f"Hero launch {cr_label} for {vehicle_display} — "
        f"lifestyle shot targeting {aud_label}, "
        f"used in {ch_label}, "
        f"September 2025 UK launch"
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

def generate() -> None:
    """Generate ~50 branded campaign images and asset manifest CSV."""
    rng = np.random.default_rng(RANDOM_SEED + 99)

    # Ensure output directories
    os.makedirs(ASSETS_DIR, exist_ok=True)
    for ch in CHANNEL_SPECS:
        os.makedirs(os.path.join(ASSETS_DIR, ch), exist_ok=True)

    # Pre-render gradient background (reused for all images)
    gradient = _make_gradient(IMG_WIDTH, IMG_HEIGHT)

    # Load fonts
    font_large = _load_font(42)
    font_medium = _load_font(28)
    font_small = _load_font(20)
    font_tiny = _load_font(16)

    model_keys = list(VEHICLE_MODELS.keys())
    manifest_rows = []

    for channel, (count, creative_types) in CHANNEL_SPECS.items():
        for i in range(count):
            # Pick model, creative type, audience
            model_key = model_keys[rng.integers(0, len(model_keys))]
            vehicle = VEHICLE_MODELS[model_key]
            vehicle_display = vehicle["display_name"]
            creative_type = creative_types[i % len(creative_types)]
            audience = AUDIENCE_SEGMENTS[rng.integers(0, len(AUDIENCE_SEGMENTS))]

            # Build image from gradient copy
            img = gradient.copy()
            draw = ImageDraw.Draw(img)

            # Draw decorative line at top
            draw.rectangle([0, 0, IMG_WIDTH, 6], fill=TEXT_WHITE)

            # Channel label (top-left area)
            channel_tag = channel.upper()
            draw.text((30, 30), channel_tag, fill=TEXT_LIGHT, font=font_small)

            # Dimensions tag (top-right)
            dim_text = f"{IMG_WIDTH}x{IMG_HEIGHT}"
            dim_bbox = draw.textbbox((0, 0), dim_text, font=font_tiny)
            draw.text((IMG_WIDTH - (dim_bbox[2] - dim_bbox[0]) - 30, 30),
                      dim_text, fill=TEXT_LIGHT, font=font_tiny)

            # Vehicle model name (centered, large)
            _draw_text_centered(draw, 180, vehicle_display, font_large,
                                TEXT_WHITE, IMG_WIDTH)

            # Creative type (centered, medium)
            _draw_text_centered(draw, 260, creative_type, font_medium,
                                TEXT_LIGHT, IMG_WIDTH)

            # Audience segment (centered, small)
            audience_display = audience.replace("_", " ").title()
            _draw_text_centered(draw, 340, audience_display, font_small,
                                TEXT_LIGHT, IMG_WIDTH)

            # Brand footer
            draw.rectangle([0, IMG_HEIGHT - 60, IMG_WIDTH, IMG_HEIGHT],
                           fill=BRAND_DARK)
            _draw_text_centered(draw, IMG_HEIGHT - 48, "DEEPAL | AVATR  UK 2025",
                                font_small, TEXT_LIGHT, IMG_WIDTH)

            # Save image
            filename = (
                f"{channel}_{model_key.lower()}_{creative_type.lower().replace(' ', '_')}"
                f"_{i + 1:02d}.png"
            )
            filepath = os.path.join(ASSETS_DIR, channel, filename)
            img.save(filepath, "PNG")

            # File size after save
            file_size = os.path.getsize(filepath)

            # Campaign ID
            campaign_id = _generate_campaign_id(channel, model_key, i + 1, rng)

            # Description
            description = _build_description(channel, vehicle_display,
                                             creative_type, audience)

            # Relative path from project root
            rel_path = os.path.relpath(filepath, PROJECT_ROOT)

            manifest_rows.append({
                "image_path": rel_path,
                "description": description,
                "channel": channel,
                "vehicle_model": vehicle_display,
                "creative_type": creative_type,
                "audience_segment": audience,
                "campaign_id": campaign_id,
                "dimensions": f"{IMG_WIDTH}x{IMG_HEIGHT}",
                "file_size": file_size,
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
# Module self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("  ASSET GENERATOR")
    print("=" * 60)
    generate()
    print("\nDone.")
