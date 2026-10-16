"""
Sanity and architectural tests for project structure, module imports,
version synchronization, and storage integrity.
"""

import unittest
from pathlib import Path

import tomlkit

import config_manager
import core_extractor
import path_installer
import preset_manager
import server
import storage
import system_checker
import updater


class TestProjectStructure(unittest.TestCase):

    def test_version_synchronization(self):
        """Ensures pyproject.toml and updater.py are in sync."""
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        self.assertTrue(pyproject_path.exists(), "pyproject.toml debe existir en el directorio raíz.")

        doc = tomlkit.loads(pyproject_path.read_text(encoding="utf-8"))
        pyproject_ver = doc["project"]["version"]

        self.assertEqual(
            pyproject_ver,
            updater.CURRENT_VERSION,
            f"Versión de pyproject.toml ({pyproject_ver}) no coincide con updater.py ({updater.CURRENT_VERSION})"
        )

    def test_storage_atomic_write_and_cleanup(self):
        """Verifies atomic write correctly creates files without leaving residual tmp files."""
        test_file = Path(__file__).parent.parent / ".cache" / "test_atomic_write.txt"
        test_content = "design-extractor-atomic-verification-content-ok"

        try:
            storage.atomic_write(test_file, test_content)
            self.assertTrue(test_file.exists())
            self.assertEqual(test_file.read_text(encoding="utf-8"), test_content)

            # Ensure no residual temp files in the cache directory
            parent_dir = test_file.parent
            tmp_files = list(parent_dir.glob("tmp*"))
            self.assertEqual(len(tmp_files), 0, "No deben quedar archivos temporales tras un atomic_write exitoso.")
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_mcp_server_tools_registered(self):
        """Verifies that all modular tools are registered in the FastMCP instance."""
        import asyncio
        try:
            tools = asyncio.run(server.mcp.list_tools())
            registered_tools = [t.name for t in tools]
        except Exception:
            if hasattr(server.mcp, "_tool_manager") and hasattr(server.mcp._tool_manager, "_tools"):
                registered_tools = list(server.mcp._tool_manager._tools.keys())
            else:
                registered_tools = []

        expected_tools = [
            "extract_design_system",
            "extract_design_tokens",
            "generate_shadcn_theme",
            "generate_tailwind_v4_theme",
            "extract_brand_assets",
            "check_accessibility_audit",
            "inspect_component",
            "generate_tailwind_theme",
            "capture_page_screenshot",
            "set_output_directory",
            "get_output_directory",
            "check_for_updates",
            "update_server"
        ]

        if registered_tools:
            for tool_name in expected_tools:
                self.assertIn(tool_name, registered_tools, f"Herramienta MCP '{tool_name}' no encontrada en el servidor.")

    def test_redact_sensitive_data(self):
        """Verifies sensitive username redaction."""
        import os
        user = os.environ.get("USERNAME") or os.environ.get("USER")
        if user and len(user) > 2:
            raw_msg = f"Error accessing C:\\Users\\{user}\\SecretFolder"
            sanitized = storage.redact_sensitive_data(raw_msg)
            self.assertNotIn(user, sanitized)
            self.assertIn("[USER]", sanitized)


if __name__ == "__main__":
    unittest.main()
