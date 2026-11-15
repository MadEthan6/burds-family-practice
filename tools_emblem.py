#!/usr/bin/env python3
"""Generate Burds Family Practice SVG emblems, hero banner SVG, and transparent brand lockup."""
import math
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent / "src/assets/img"
FB_COVER_SOURCE = Path("/tmp/fb/cover.png")


def _compass_star_outer():
    """Smooth concave 4-point main star + 4 diagonal points matching fb-logo.jpg."""
    # Main cardinal tips at (50, 24), (76, 50), (50, 76), (24, 50)
    # Curved concave arms meeting near radius 10 at 45-degree corners
    return (
        "M 50 23 "
        "Q 51.5 43 57 43 "
        "Q 57 48.5 77 50 "
        "Q 57 51.5 57 57 "
        "Q 51.5 57 50 77 "
        "Q 48.5 57 43 57 "
        "Q 43 51.5 23 50 "
        "Q 43 48.5 43 43 "
        "Q 48.5 43 50 23 Z"
    )


def _diagonal_rays():
    """Four small diagonal rays between the main compass points."""
    rays = []
    for angle in (45, 135, 225, 315):
        rays.append(
            f'<g transform="translate(50 50) rotate({angle})">'
            '<path d="M -5.5 -6.5 L 0 -17 L 5.5 -6.5 Z"/>'
            "</g>"
        )
    return "".join(rays)


def emblem(line, leaf, bg=None, cut_fill="none"):
    """Build an SVG emblem in the requested line, botanical leaf/root, and optional badge bg colors."""
    vein = bg if bg else cut_fill if cut_fill != "none" else "#003C42"
    leaf_shape = "M 0 0 C -4.6 -4.4 -4.6 -11.2 0 -16 C 4.6 -11.2 4.6 -4.4 0 0 Z"
    leaves = "".join(
        f'<g transform="translate(50 50) rotate({ang}) translate(0 -{rad})">'
        f'<path d="{leaf_shape}" fill="{leaf}"/>'
        f'<path d="M 0 -3 L 0 -12" stroke="{vein}" stroke-width="1.35" stroke-linecap="round"/>'
        "</g>"
        for ang, rad in ((-20, 18.5), (20, 18.5), (-58, 19.5), (58, 19.5))
    )

    roots = (
        f'<g fill="none" stroke="{leaf}" stroke-width="2.4" stroke-linecap="round">'
        '<path d="M 46 57 Q 33 58 21 63"/>'
        '<path d="M 54 57 Q 67 58 79 63"/>'
        '<path d="M 47 61 Q 36 69 27 72"/>'
        '<path d="M 53 61 Q 64 69 73 72"/>'
        '<path d="M 48 64 Q 42 74 37 80"/>'
        '<path d="M 52 64 Q 58 74 63 80"/>'
        '<path d="M 50 64 L 50 83"/>'
        "</g>"
    )

    ring = (
        f'<g fill="none" stroke="{line}" stroke-width="2.4" stroke-linecap="round">'
        '<circle cx="50" cy="50" r="43"/>'
        '<circle cx="50" cy="50" r="37.5"/>'
        '<path d="M 50 7 L 50 18 M 50 82 L 50 93 M 7 50 L 18 50 M 82 50 L 93 50"/>'
        "</g>"
    )

    star_fill = bg if bg else cut_fill
    star = (
        f'<g fill="{star_fill}" stroke="{line}" stroke-width="2.5" stroke-linejoin="round">'
        f"{_diagonal_rays()}"
        f'<path d="{_compass_star_outer()}"/>'
        "</g>"
    )

    back = f'<rect width="100" height="100" rx="22" fill="{bg}"/>' if bg else ""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" '
        'role="img" aria-label="Burds Family Practice emblem">'
        f"{back}{ring}{leaves}{roots}{star}</svg>\n"
    )


def hero_banner_bg():
    """Atmospheric Deep Green (#003C42) full-bleed banner SVG using only official palette tones."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 720" '
        'preserveAspectRatio="xMidYMid slice" aria-hidden="true">'
        "<defs>"
        '<radialGradient id="centerGlow" cx="50%" cy="44%" r="52%">'
        '<stop offset="0%" stop-color="#0a5159" stop-opacity="0.92"/>'
        '<stop offset="55%" stop-color="#003C42" stop-opacity="0.45"/>'
        '<stop offset="100%" stop-color="#00282c" stop-opacity="0.85"/>'
        "</radialGradient>"
        '<radialGradient id="aquaGlow" cx="16%" cy="20%" r="42%">'
        '<stop offset="0%" stop-color="#98BEAE" stop-opacity="0.16"/>'
        '<stop offset="100%" stop-color="#98BEAE" stop-opacity="0"/>'
        "</radialGradient>"
        '<radialGradient id="warmGlow" cx="84%" cy="76%" r="42%">'
        '<stop offset="0%" stop-color="#D6A379" stop-opacity="0.15"/>'
        '<stop offset="100%" stop-color="#D6A379" stop-opacity="0"/>'
        "</radialGradient>"
        '<linearGradient id="waveShade" x1="0%" y1="0%" x2="100%" y2="0%">'
        '<stop offset="0%" stop-color="#00282c" stop-opacity="0.72"/>'
        '<stop offset="50%" stop-color="#003237" stop-opacity="0.48"/>'
        '<stop offset="100%" stop-color="#00282c" stop-opacity="0.78"/>'
        "</linearGradient>"
        "</defs>"
        '<rect width="1600" height="720" fill="#003C42"/>'
        '<rect width="1600" height="720" fill="url(#centerGlow)"/>'
        '<rect width="1600" height="720" fill="url(#aquaGlow)"/>'
        '<rect width="1600" height="720" fill="url(#warmGlow)"/>'
        '<g fill="none" stroke="#98BEAE" stroke-opacity="0.08" stroke-width="1.5">'
        '<circle cx="800" cy="245" r="245"/>'
        '<circle cx="800" cy="245" r="325" stroke-dasharray="6 10"/>'
        '<circle cx="800" cy="245" r="410" stroke-opacity="0.05"/>'
        "</g>"
        '<path d="M 0 548 C 280 500 540 600 840 558 C 1140 516 1380 590 1600 544 L 1600 720 L 0 720 Z" fill="url(#waveShade)"/>'
        '<path d="M 0 606 C 320 648 640 562 980 612 C 1260 652 1460 584 1600 604 L 1600 720 L 0 720 Z" fill="#002226" fill-opacity="0.62"/>'
        '<path d="M 0 548 C 280 500 540 600 840 558 C 1140 516 1380 590 1600 544" fill="none" stroke="#98BEAE" stroke-opacity="0.16" stroke-width="1.5"/>'
        '<path d="M 0 606 C 320 648 640 562 980 612 C 1260 652 1460 584 1600 604" fill="none" stroke="#D6A379" stroke-opacity="0.18" stroke-width="1.2"/>'
        '<path d="M 0 116 C 340 162 660 66 1020 112 C 1300 148 1480 96 1600 118" fill="none" stroke="#98BEAE" stroke-opacity="0.10" stroke-width="1.2"/>'
        "</svg>\n"
    )


def _decode_rgb(path, vf=None):
    cmd = ["ffmpeg", "-v", "error", "-i", str(path)]
    if vf:
        cmd += ["-vf", vf]
    cmd += ["-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    return subprocess.check_output(cmd)


def _encode_png(raw_bytes, pix_fmt, width, height, out_path):
    cmd = [
        "ffmpeg", "-v", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", pix_fmt, "-s", f"{width}x{height}", "-i", "-",
        str(out_path),
    ]
    subprocess.run(cmd, input=raw_bytes, check=True)


def _smoothstep(edge0, edge1, x):
    t = max(0.0, min(1.0, (x - edge0) / (edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)


def build_banner_assets():
    """Unmix the centered brand lockup from the Facebook cover into a transparent PNG and true #003C42 banner."""
    if not FB_COVER_SOURCE.exists():
        print("skip PNG banner generation: /tmp/fb/cover.png not present")
        return

    src_w, src_h = 953, 355
    src_rgb = _decode_rgb(FB_COVER_SOURCE, f"crop={src_w}:{src_h}:0:0")

    # Centered crop enclosing bbox x=334..625, y=23..325 with clean margins
    x0, y0, lw, lh = 322, 12, 316, 324
    lockup_rgba = bytearray(lw * lh * 4)

    # Colors: Hometown Aqua (#98BEAE) for emblem/tagline, warm Gentle Light (#EDEAE0) for script/title
    aqua = (152.0, 190.0, 174.0)
    cream = (242.0, 239.0, 231.0)

    for dy in range(lh):
        sy = y0 + dy
        for dx in range(lw):
            sx = x0 + dx
            si = (sy * src_w + sx) * 3
            r, g, b = src_rgb[si], src_rgb[si + 1], src_rgb[si + 2]
            lum = 0.2126 * r + 0.7152 * g + 0.0722 * b

            if lum <= 68.5:
                a = 0.0
                out_rgb = (0, 0, 0)
            elif lum <= 85.0:
                # Subtle background emblem watermark
                t = _smoothstep(68.5, 85.0, lum)
                a = t * 0.26
                out_rgb = aqua
            elif lum <= 152.0:
                # Curved 'community rooted in PEOSTA • IA', 'PERSONALIZED HEALTHCARE SINCE 2023', and AA edges
                t = _smoothstep(85.0, 152.0, lum)
                a = 0.26 + t * 0.68
                mix = _smoothstep(126.0, 160.0, lum)
                out_rgb = tuple(aqua[c] * (1.0 - mix) + cream[c] * mix for c in range(3))
            else:
                # Core strokes of 'Burds' script and 'FAMILY PRACTICE'
                t = _smoothstep(152.0, 195.0, lum)
                a = 0.94 + t * 0.06
                mix = _smoothstep(126.0, 176.0, lum)
                out_rgb = tuple(aqua[c] * (1.0 - mix) + cream[c] * mix for c in range(3))

            di = (dy * lw + dx) * 4
            lockup_rgba[di] = int(round(out_rgb[0]))
            lockup_rgba[di + 1] = int(round(out_rgb[1]))
            lockup_rgba[di + 2] = int(round(out_rgb[2]))
            lockup_rgba[di + 3] = max(0, min(255, int(round(a * 255.0))))

    _encode_png(bytes(lockup_rgba), "rgba", lw, lh, OUT / "brand-lockup-transparent.png")

    # Composite transparent lockup onto a true Deep Green (#003C42) textured ripple banner (953x355)
    ripple_path = OUT / "water-ripple.png"
    base_rgb = bytearray(src_w * src_h * 3)
    deep_r, deep_g, deep_b = 0.0, 60.0, 66.0  # #003C42

    if ripple_path.exists():
        rip = _decode_rgb(ripple_path, f"scale={src_w}:{src_h}:flags=bicubic")
        for i in range(src_w * src_h):
            ri = i * 3
            rlum = (0.2126 * rip[ri] + 0.7152 * rip[ri + 1] + 0.0722 * rip[ri + 2]) / 255.0
            delta = (rlum - 0.5) * 18.0
            base_rgb[ri] = max(0, min(255, int(round(deep_r + delta))))
            base_rgb[ri + 1] = max(0, min(255, int(round(deep_g + delta))))
            base_rgb[ri + 2] = max(0, min(255, int(round(deep_b + delta))))
    else:
        for i in range(src_w * src_h):
            ri = i * 3
            base_rgb[ri], base_rgb[ri + 1], base_rgb[ri + 2] = 0, 60, 66

    for dy in range(lh):
        sy = y0 + dy
        for dx in range(lw):
            sx = x0 + dx
            di = (dy * lw + dx) * 4
            a = lockup_rgba[di + 3] / 255.0
            if a <= 0.0:
                continue
            bi = (sy * src_w + sx) * 3
            for c in range(3):
                base_rgb[bi + c] = int(round(base_rgb[bi + c] * (1.0 - a) + lockup_rgba[di + c] * a))

    _encode_png(bytes(base_rgb), "rgb24", src_w, src_h, OUT / "fb-banner.png")
    print("wrote brand-lockup-transparent.png and updated fb-banner.png")


if __name__ == "__main__":
    # Official 8-color brand palette tokens
    DEEP_GREEN = "#003C42"
    ROOTED_SAGE = "#6F8371"
    HOMETOWN_AQUA = "#98BEAE"
    GENTLE_LIGHT = "#E9E6DC"

    OUT.joinpath("emblem-dark.svg").write_text(
        emblem(DEEP_GREEN, ROOTED_SAGE, cut_fill="#FFFFFF"), encoding="utf-8"
    )
    OUT.joinpath("emblem-light.svg").write_text(
        emblem(GENTLE_LIGHT, HOMETOWN_AQUA, cut_fill=DEEP_GREEN), encoding="utf-8"
    )
    OUT.joinpath("favicon.svg").write_text(
        emblem(GENTLE_LIGHT, HOMETOWN_AQUA, bg=DEEP_GREEN), encoding="utf-8"
    )
    OUT.joinpath("hero-banner-bg.svg").write_text(hero_banner_bg(), encoding="utf-8")
    print("wrote emblem-dark.svg, emblem-light.svg, favicon.svg, hero-banner-bg.svg")
    build_banner_assets()
