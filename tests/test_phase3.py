"""
Unit tests for Phase 3 improvements in Design Extractor MCP:
- Authentication support (storage_state & cookies parsing)
- Multi-viewport responsive matrix formatting
- W3C DTCG Design Tokens schema generation
- CLI parsing for login and auth options
"""

import unittest
import json
from pathlib import Path

from core_extractor import (
    _parse_cookie_arg,
    generate_w3c_design_tokens,
    generate_agent_design_spec
)


class TestPhase3Features(unittest.TestCase):

    def test_parse_cookie_arg_single_string(self):
        cookies = _parse_cookie_arg("MoodleSession=abc123xyz", "https://moodle.university.edu/course")
        self.assertEqual(len(cookies), 1)
        self.assertEqual(cookies[0]["name"], "MoodleSession")
        self.assertEqual(cookies[0]["value"], "abc123xyz")
        self.assertEqual(cookies[0]["domain"], "moodle.university.edu")
        self.assertEqual(cookies[0]["path"], "/")

    def test_parse_cookie_arg_multiple_string(self):
        cookie_str = "MoodleSession=token123; sessionid=sess456; theme=dark"
        cookies = _parse_cookie_arg(cookie_str, "https://app.example.com/dashboard")
        self.assertEqual(len(cookies), 3)
        names = [c["name"] for c in cookies]
        self.assertIn("MoodleSession", names)
        self.assertIn("sessionid", names)
        self.assertIn("theme", names)

    def test_parse_cookie_arg_json_list(self):
        json_data = json.dumps([
            {"name": "token", "value": "xyz", "domain": "example.com", "path": "/"}
        ])
        cookies = _parse_cookie_arg(json_data, "https://example.com")
        self.assertEqual(len(cookies), 1)
        self.assertEqual(cookies[0]["name"], "token")

    def test_generate_w3c_design_tokens_schema(self):
        mock_data = {
            "isDark": False,
            "bodyBg": "#ffffff",
            "bodyColor": "#111827",
            "colors": {
                "backgrounds": ["#ffffff", "#f8fafc", "#0284c7"],
                "texts": ["#111827", "#64748b"],
                "borders": ["#e2e8f0"]
            },
            "typography": {
                "body": {"fontSize": "16px", "fontFamily": "Inter, sans-serif", "fontWeight": "400", "lineHeight": "1.5"},
                "h1": {"fontSize": "48px", "fontFamily": "Poppins, sans-serif", "fontWeight": "700", "lineHeight": "1.1"}
            },
            "buttons": [{"bg": "#0284c7"}],
            "radii": ["8px", "16px", "9999px"],
            "shadows": ["0 4px 6px -1px rgba(0, 0, 0, 0.1)"],
            "containers": ["1280px"],
            "dualTheme": {
                "hasDarkThemeSupport": True,
                "light": {"background": "#ffffff", "foreground": "#111827"},
                "dark": {
                    "background": "#09090b",
                    "foreground": "#f4f4f5",
                    "cardBackground": "#18181b",
                    "cardBorder": "rgba(255, 255, 255, 0.1)"
                }
            }
        }

        tokens = generate_w3c_design_tokens(mock_data)

        # 1. DTCG Schema declaration
        self.assertEqual(tokens["$schema"], "https://design-tokens.github.io/community-group/format/")

        # 2. Color token format
        self.assertEqual(tokens["color"]["canvas"]["$type"], "color")
        self.assertEqual(tokens["color"]["canvas"]["$value"], "#ffffff")
        self.assertEqual(tokens["color"]["brand"]["primary"]["$type"], "color")
        self.assertEqual(tokens["color"]["brand"]["primary"]["$value"], "#0284c7")

        # 3. Typography token format
        self.assertEqual(tokens["typography"]["fontFamily"]["heading"]["$type"], "fontFamily")
        self.assertIn("Poppins", tokens["typography"]["fontFamily"]["heading"]["$value"])
        self.assertEqual(tokens["typography"]["fontSize"]["h1"]["$value"], "48px")
        self.assertEqual(tokens["typography"]["fontSize"]["h1"]["$type"], "dimension")

        # 4. Radii & Spacing
        self.assertEqual(tokens["borderRadius"]["sm"]["$value"], "8px")
        self.assertEqual(tokens["borderRadius"]["sm"]["$type"], "dimension")

        # 5. Dual theme mode tokens
        self.assertIn("mode", tokens)
        self.assertEqual(tokens["mode"]["dark"]["canvas"]["$value"], "#09090b")

    def test_generate_agent_design_spec_includes_responsive_matrix(self):
        mock_data = {
            "isDark": False,
            "bodyBg": "#ffffff",
            "bodyColor": "#111827",
            "typography": {
                "h1": {"fontSize": "48px", "fontFamily": "Inter"},
                "body": {"fontSize": "16px", "fontFamily": "Inter"}
            },
            "colors": {"backgrounds": ["#ffffff"], "texts": ["#111827"], "borders": ["#e5e7eb"]},
            "responsiveMatrix": {
                "desktop": {
                    "windowWidth": 1440,
                    "h1FontSize": "48px",
                    "navigationMode": "Barra Completa Visible",
                    "gridSummary": "3 Columnas"
                },
                "tablet": {
                    "windowWidth": 768,
                    "h1FontSize": "36px",
                    "navigationMode": "Barra Completa Visible",
                    "gridSummary": "2 Columnas"
                },
                "mobile": {
                    "windowWidth": 375,
                    "h1FontSize": "28px",
                    "navigationMode": "Colapsada (Menú Hamburguesa)",
                    "gridSummary": "1 Columna (Stack)"
                }
            }
        }

        spec = generate_agent_design_spec(mock_data, "https://test.local")
        self.assertIn("### Responsive Multi-Viewport Matrix", spec)
        self.assertIn("| **Desktop** | `1440px` | `48px` | `Barra Completa Visible` | `3 Columnas` |", spec)
        self.assertIn("| **Mobile** | `375px` | `28px` | `Colapsada (Menú Hamburguesa)` | `1 Columna (Stack)` |", spec)


if __name__ == "__main__":
    unittest.main()
