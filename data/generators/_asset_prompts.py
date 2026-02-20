"""
Prompt data and builder for AI-powered campaign asset image generation.

Separated from assets.py to keep the main module lean.
Used only when AI mode is enabled (ASSET_GEN_AI=1 or --ai flag).
"""

# ---------------------------------------------------------------------------
# Vehicle visual descriptions
# ---------------------------------------------------------------------------
VEHICLE_PROMPTS = {
    "DEEPAL_S07": (
        "DEEPAL S07, a sleek modern electric SUV with flowing aerodynamic lines, "
        "pearl-white body, panoramic glass roof, slim LED headlights, and 21-inch alloy wheels, "
        "positioned as a premium mid-size electric SUV"
    ),
    "DEEPAL_S05": (
        "DEEPAL S05, a compact electric SUV-coupe with a dramatic fastback silhouette, "
        "matte graphite body, flush door handles, illuminated front grille accent, "
        "sporty and youthful design language"
    ),
    "AVATR_12": (
        "AVATR 12, a flagship luxury electric SUV with bold sculpted bodywork, "
        "deep midnight-blue metallic paint, signature split headlamps, massive 22-inch wheels, "
        "commanding road presence and premium detailing"
    ),
    "AVATR_11": (
        "AVATR 11, an executive electric sedan with a long wheelbase, "
        "champagne-gold metallic finish, sweeping roofline, full-width LED light bar, "
        "elegant and refined premium saloon proportions"
    ),
}

# ---------------------------------------------------------------------------
# Channel visual style directives
# ---------------------------------------------------------------------------
CHANNEL_STYLES = {
    "meta":     "Polished social-media ad photograph, vibrant colours, lifestyle setting, scroll-stopping composition",
    "google":   "Clean digital display banner photograph, bright studio or outdoor backdrop, high contrast",
    "tv":       "Cinematic widescreen still frame, dramatic lighting, motion blur on wheels, broadcast quality",
    "ooh":      "Large-format outdoor billboard visual, high-impact, UK urban streetscape background",
    "youtube":  "Widescreen video thumbnail, bold composition, dramatic angle, cinematic colour grading",
    "tiktok":   "Vertical mobile-first photograph, trendy and energetic, bright neon accent lighting",
    "linkedin": "Professional corporate photography, clean background, sophisticated and business-oriented",
    "dv360":    "Programmatic display creative, clean product-on-background studio shot, editorial quality",
    "print":    "High-resolution magazine editorial photograph, rich detail, print-quality colour depth",
    "radio":    "Square podcast artwork style, atmospheric mood shot, album-cover composition",
}

# ---------------------------------------------------------------------------
# Creative-type modifiers (one per creative type across all channels)
# ---------------------------------------------------------------------------
CREATIVE_MODIFIERS = {
    # meta
    "Social Post":          "casual lifestyle scene, vehicle parked outside a trendy UK café",
    "Story Ad":             "vertical close-up detail shot of the vehicle front fascia",
    "Carousel":             "three-quarter front angle, vehicle on a scenic coastal road",
    "Reel Cover":           "dynamic low-angle shot, vehicle turning on a wet city street at dusk",
    # google
    "Display Ad":           "clean white-background studio product shot, three-quarter view",
    "Search Ad":            "minimal hero shot, vehicle centred on neutral gradient backdrop",
    "Responsive Ad":        "vehicle in front of modern glass architecture, urban daylight",
    # tv
    "TV Still":             "cinematic wide shot, vehicle driving through the Scottish Highlands at golden hour",
    "Bumper Frame":         "extreme close-up of LED headlight and grille, dramatic studio lighting",
    "Sponsorship Slate":    "vehicle parked at a prestigious UK motorsport venue, evening ambience",
    # ooh
    "Billboard Mockup":     "vehicle speeding past Tower Bridge at blue hour, motion streak lighting",
    "Bus Shelter":          "vehicle parked on a tree-lined London mews, autumn leaves, soft light",
    "Digital Screen":       "neon-lit vehicle in a futuristic urban tunnel, reflections on wet tarmac",
    # youtube
    "Thumbnail":            "dramatic front-on hero shot, headlights illuminated, dark moody backdrop",
    "Masthead Banner":      "panoramic aerial view of vehicle crossing a suspension bridge, epic scale",
    # tiktok
    "Vertical Still":       "street-level vertical shot, vehicle under colourful market lights at night",
    "TopView Frame":        "bird's-eye vertical shot looking down at vehicle on rain-slicked street",
    "Spark Ad":             "casual handheld-style photo, vehicle in a vibrant street market setting",
    # linkedin
    "Sponsored Content":    "vehicle outside a modern corporate HQ building, professional morning light",
    "Message Ad":           "interior cabin detail shot, premium leather and digital dashboard",
    # dv360
    "Programmatic Display": "studio product shot on dark gradient, accent rim lighting",
    "Native Ad":            "editorial-style image, vehicle on a countryside estate driveway",
    "Rich Media":           "split-composition showing exterior and interior in one frame",
    # print
    "Magazine Full Page":   "high-resolution studio shot, dramatic single-source lighting, black background",
    "Magazine DPS":         "panoramic landscape, vehicle traversing the Lake District, cinematic crop",
    "Advertorial":          "lifestyle scene, couple loading luggage into the boot at a boutique hotel",
    # radio
    "Podcast Artwork":      "moody atmospheric shot, vehicle silhouette against sunset sky",
    "Station Ident":        "abstract macro detail of bodywork curves and reflections",
    "Audio Ad Cover":       "vehicle at night with ambient interior glow, minimalist composition",
}

# ---------------------------------------------------------------------------
# Channel → image size (width x height)
# ---------------------------------------------------------------------------
AI_SIZES = {
    "meta":     "1024x1024",
    "google":   "1024x1024",
    "linkedin": "1024x1024",
    "dv360":    "1024x1024",
    "radio":    "1024x1024",
    "tv":       "1536x1024",
    "ooh":      "1536x1024",
    "youtube":  "1536x1024",
    "tiktok":   "1024x1536",
    "print":    "1024x1536",
}


def build_ai_prompt(
    channel: str,
    model_key: str,
    creative_type: str,
    audience: str,
    vehicle_display: str,
) -> str:
    """Assemble the full image-generation prompt for a single campaign asset."""
    vehicle_desc = VEHICLE_PROMPTS.get(model_key, f"a premium electric vehicle called {vehicle_display}")
    style = CHANNEL_STYLES.get(channel, "professional automotive marketing photograph")
    modifier = CREATIVE_MODIFIERS.get(creative_type, "hero product shot in a premium UK setting")
    audience_phrase = audience.replace("_", " ").lower()

    return (
        f"Photorealistic automotive marketing image: {vehicle_desc}. "
        f"Scene: {modifier}. "
        f"Style: {style}. "
        f"Target audience feel: {audience_phrase}. "
        f"UK market, 2025 launch campaign. "
        f"No text overlays or watermarks."
    )
