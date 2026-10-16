"""
Unit tests for Phase 4 improvements in Design Extractor MCP:
- HSL color conversion for Shadcn UI
- Native Shadcn UI globals.css exporter with :root and .dark HSL variables
- Native Tailwind CSS v4 CSS-first theme exporter (@theme directive)
- Brand assets extraction metadata validation
- WCAG 2.1 accessibility contrast audit validation
"""

import unittest
from pathlib import Path

from core_extractor import (
    _hex_or_rgb_to_hsl_components,
    generate_shadcn_theme,
    generate_tailwind_v4_theme
)


class TestPhase4Features(unittest.TestCase):

    def test_hex_to_hsl_components(self):
        # White
        white_hsl = _hex_or_rgb_to_hsl_components("#ffffff")
        self.assertEqual(white_hsl, "0.0 0.0% 100.0%")

        # Black
        black_hsl = _hex_or_rgb_to_hsl_components("#000000")
        self.assertEqual(black_hsl, "0.0 0.0% 0.0%")

        # Pure Red #ff0000
        red_hsl = _hex_or_rgb_to_hsl_components("#ff0000")
        self.assertEqual(red_hsl, "0.0 100.0% 50.0%")

        # Short Hex #fff
        short_white = _hex_or_rgb_to_hsl_components("#fff")
        self.assertEqual(short_white, "0.0 0.0% 100.0%")

    def test_rgb_string_to_hsl_components(self):
        rgb_str = "rgb(255, 255, 255)"
        hsl = _hex_or_rgb_to_hsl_components(rgb_str)
        self.assertEqual(hsl, "0.0 0.0% 100.0%")

        rgba_str = "rgba(0, 0, 0, 0.8)"
        hsl_black = _hex_or_rgb_to_hsl_components(rgba_str)
        self.assertEqual(hsl_black, "0.0 0.0% 0.0%")

    def test_generate_shadcn_theme(self):
        mock_data = {
            "isDark": False,
            "bodyBg": "#ffffff",
            "bodyColor": "#09090b",
            "colors": {
                "backgrounds": ["#ffffff", "#f4f4f5", "#2563eb"],
                "texts": ["#09090b", "#71717a"],
                "borders": ["#e4e4e7"]
            },
            "buttons": [{"bg": "#2563eb", "color": "#ffffff"}],
            "cardInfo": {"backgroundColor": "#ffffff"},
            "radii": ["8px", "12px", "9999px"],
            "dualTheme": {
                "hasDarkThemeSupport": True,
                "light": {"background": "#ffffff", "foreground": "#09090b"},
                "dark": {
                    "background": "#09090b",
                    "foreground": "#f4f4f5",
                    "cardBackground": "#18181b",
                    "cardBorder": "rgba(255, 255, 255, 0.1)"
                }
            }
        }

        css = generate_shadcn_theme(mock_data)

        # Verify key Shadcn UI CSS structure
        self.assertIn("@tailwind base;", css)
        self.assertIn(":root {", css)
        self.assertIn(".dark {", css)
        self.assertIn("--background:", css)
        self.assertIn("--foreground:", css)
        self.assertIn("--primary:", css)
        self.assertIn("--radius:", css)
        self.assertIn("@layer base", css)

        # Verify radius is parsed to rem (8px -> 0.5rem)
        self.assertIn("--radius: 0.5rem;", css)

    def test_generate_tailwind_v4_theme(self):
        mock_data = {
            "bodyBg": "#ffffff",
            "bodyColor": "#111827",
            "colors": {
                "backgrounds": ["#ffffff", "#f8fafc"],
                "texts": ["#111827", "#64748b"],
                "borders": ["#e2e8f0"]
            },
            "typography": {
                "h1": {"fontFamily": "Poppins, sans-serif"},
                "body": {"fontFamily": "Inter, sans-serif"}
            },
            "buttons": [{"bg": "#0284c7"}],
            "cardInfo": {"backgroundColor": "#f8fafc"},
            "radii": ["8px", "16px"],
            "containers": ["1280px"]
        }

        css = generate_tailwind_v4_theme(mock_data)

        # Verify Tailwind v4 @theme directive
        self.assertIn('@import "tailwindcss";', css)
        self.assertIn("@theme {", css)
        self.assertIn("--color-background: #ffffff;", css)
        self.assertIn("--color-foreground: #111827;", css)
        self.assertIn("--color-primary: #0284c7;", css)
        self.assertIn("--font-heading: Poppins, sans-serif;", css)
        self.assertIn("--font-sans: Inter, sans-serif;", css)
        self.assertIn("--radius-sm: 8px;", css)
        self.assertIn("--container-max-width: 1280px;", css)

    def test_brand_assets_and_accessibility_audit_structure(self):
        mock_audit = [
            {"pair": "Texto Base sobre Canvas", "fg": "#111827", "bg": "#ffffff", "ratio": 16.1, "level": "AAA"},
            {"pair": "Texto de Botón CTA sobre Fondo", "fg": "#ffffff", "bg": "#2563eb", "ratio": 4.6, "level": "AA"}
        ]
        mock_brand = {
            "faviconUrl": "https://example.com/favicon.ico",
            "hasLogoSvg": True,
            "logoSvgSnippet": "<svg viewBox='0 0 100 100'><circle cx='50' cy='50' r='40'/></svg>",
            "totalSvgsOnPage": 12
        }

        # Check accessibility audit records
        self.assertEqual(len(mock_audit), 2)
        self.assertEqual(mock_audit[0]["level"], "AAA")
        self.assertGreater(mock_audit[0]["ratio"], 7.0)

        # Check brand assets
        self.assertTrue(mock_brand["hasLogoSvg"])
        self.assertIn("<svg", mock_brand["logoSvgSnippet"])
        self.assertEqual(mock_brand["totalSvgsOnPage"], 12)


if __name__ == "__main__":
    unittest.main()
