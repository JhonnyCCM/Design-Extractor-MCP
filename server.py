"""
Web Design Extractor & Style Cloner MCP Server
Extracts complete visual design systems, typography scales, container structures,
div layouts, deep source code analysis, and generates detailed AI Agent instruction sheets.
All outputs are automatically saved to the user's configured directory.
"""

import os
import re
import json
from urllib.parse import urlparse
from pathlib import Path
from typing import Optional
from mcp.server.fastmcp import FastMCP

from config_manager import get_configured_output_dir, set_configured_output_dir
from storage import atomic_write, redact_sensitive_data
from core_extractor import (
    async_extract_page_design_data,
    async_inspect_single_element,
    async_take_screenshot,
    generate_agent_design_spec,
    generate_w3c_design_tokens
)

mcp = FastMCP("web-design-extractor")


def _url_to_slug(url: str) -> str:
    """Converts a URL to a filesystem-friendly slug."""
    parsed = urlparse(url)
    netloc = parsed.netloc.replace("www.", "")
    path = parsed.path.strip("/").replace("/", "_")
    slug = f"{netloc}_{path}" if path else netloc
    slug = re.sub(r"[^\w\-.]", "_", slug).strip("_")
    return slug or "webpage"


@mcp.tool()
def get_output_directory() -> str:
    """
    Returns the currently configured storage directory where all generated
    Markdown specifications (.md), design tokens (.json), and screenshots (.png) are saved.
    """
    target = get_configured_output_dir()
    return f"Active storage directory: {target}"


@mcp.tool()
def set_output_directory(path: str) -> str:
    """
    Updates and persists the output directory where all generated Markdown specifications
    and screenshots will be saved.

    Args:
        path: The absolute folder path (e.g., 'C:\\Users\\jonni\\DesignSpecs' or 'D:\\Proyectos\\Specs').

    Returns:
        Confirmation message with the resolved directory path.
    """
    try:
        saved_path = set_configured_output_dir(path)
        return f"Successfully updated and persisted output directory to: {saved_path}"
    except Exception as e:
        return f"Error setting output directory: {str(e)}"


@mcp.tool()
async def extract_design_system(
    url: str,
    output_file: str = "",
    storage_state: str = "",
    cookie: str = ""
) -> str:
    """
    Visits a webpage with a headless browser, conducts deep source code and DOM inspection
    (HTML source, stylesheets, CSS variables, typography hierarchy, container max-widths,
    div nesting patterns, responsive grid/flex layouts, and component skeletons),
    captures a screenshot, and saves a comprehensive Markdown instruction sheet AND standard
    W3C DTCG tokens JSON to the configured directory.

    Args:
        url: The URL of the webpage to analyze (e.g. 'https://stripe.com' or 'https://linear.app').
        output_file: Optional custom filename or path. If omitted, automatically saves to configured directory as '<slug>_spec.md'.
        storage_state: Optional path to an authenticated session file (e.g. 'auth.json' from 'design-extractor login <url>').
        cookie: Optional direct session cookie (e.g. 'MoodleSession=abc123xyz' or 'sessionid=...').

    Returns:
        The complete Master Design System & Agent Instructions Sheet with storage location details.
    """
    try:
        out_dir = get_configured_output_dir()
        slug = _url_to_slug(url)

        # 1. Extract DOM, CSS and source code intelligence
        data = await async_extract_page_design_data(
            url,
            storage_state=storage_state or None,
            cookies=cookie or None
        )
        spec_md = generate_agent_design_spec(data, url)
        tokens_data = generate_w3c_design_tokens(data)

        # 2. Determine file paths
        if output_file:
            target_md = Path(output_file).resolve()
            if not target_md.suffix:
                target_md = target_md / f"{slug}_design_spec.md"
        else:
            target_md = out_dir / f"{slug}_design_spec.md"

        target_tokens = target_md.parent / f"{slug}_design_tokens.json"
        target_png = target_md.parent / f"{slug}_preview.png"

        target_md.parent.mkdir(parents=True, exist_ok=True)
        atomic_write(target_md, spec_md)
        atomic_write(target_tokens, json.dumps(tokens_data, indent=2, ensure_ascii=False) + "\n")

        # 3. Capture screenshot
        await async_take_screenshot(
            url,
            str(target_png),
            full_page=True,
            storage_state=storage_state or None,
            cookies=cookie or None
        )

        location_notice = (
            f"\n\n---\n"
            f"### 📁 Archivos Guardados en Carpeta Configurada:\n"
            f"- **Especificación Markdown (.md):** `{target_md}`\n"
            f"- **Tokens W3C DTCG (.json):** `{target_tokens}`\n"
            f"- **Captura de Pantalla (.png):** `{target_png}`\n"
        )

        return spec_md + location_notice
    except Exception as e:
        return f"Error extracting design system from {url}: {redact_sensitive_data(str(e))}"


@mcp.tool()
async def extract_design_tokens(
    url: str,
    output_file: str = "",
    storage_state: str = "",
    cookie: str = ""
) -> str:
    """
    Extracts design tokens in standard W3C Design Tokens Community Group (DTCG) JSON format
    (compatible with Figma Tokens, Style Dictionary, Tailwind and design pipelines).
    Saves the JSON file to disk and returns the structured token payload.

    Args:
        url: The URL of the webpage to analyze.
        output_file: Optional custom filename or path for the tokens JSON.
        storage_state: Optional path to an authenticated session file ('auth.json').
        cookie: Optional direct session cookie ('MoodleSession=...').

    Returns:
        JSON string of W3C DTCG design tokens.
    """
    try:
        out_dir = get_configured_output_dir()
        slug = _url_to_slug(url)

        data = await async_extract_page_design_data(
            url,
            storage_state=storage_state or None,
            cookies=cookie or None
        )
        tokens_data = generate_w3c_design_tokens(data)

        if output_file:
            target_json = Path(output_file).resolve()
            if not target_json.suffix:
                target_json = target_json / f"{slug}_design_tokens.json"
        else:
            target_json = out_dir / f"{slug}_design_tokens.json"

        target_json.parent.mkdir(parents=True, exist_ok=True)
        formatted_json = json.dumps(tokens_data, indent=2, ensure_ascii=False) + "\n"
        atomic_write(target_json, formatted_json)

        return formatted_json
    except Exception as e:
        return f"Error extracting design tokens for {url}: {redact_sensitive_data(str(e))}"



@mcp.tool()
async def inspect_page_source(
    url: str,
    storage_state: str = "",
    cookie: str = ""
) -> str:
    """
    Inspects the raw source code of a webpage: framework detection (React, Next.js, Vue, Tailwind, etc.),
    external stylesheet links, font definitions, and meta tags.

    Args:
        url: The URL of the webpage to inspect.
        storage_state: Optional path to an authenticated session file ('auth.json').
        cookie: Optional direct session cookie ('MoodleSession=...').

    Returns:
        JSON string summarizing framework detection, stylesheets, scripts, and meta tags.
    """
    try:
        data = await async_extract_page_design_data(
            url,
            storage_state=storage_state or None,
            cookies=cookie or None
        )
        summary = {
            "title": data.get("title"),
            "url": data.get("url"),
            "techStack": data.get("techStack", []),
            "mediaBreakpoints": data.get("mediaBreakpoints", []),
            "keyframes": data.get("keyframes", []),
            "externalFonts": data.get("externalFonts", []),
            "metaTags": data.get("metaTags", {}),
            "cssVariablesCount": len(data.get("cssVariables", {})),
            "sampledDeveloperUtilityClasses": data.get("sampledUtilityClasses", [])[:15]
        }
        return json.dumps(summary, indent=2)
    except Exception as e:
        return f"Error inspecting source code for {url}: {str(e)}"


@mcp.tool()
async def inspect_component(
    url: str,
    selector: str,
    storage_state: str = "",
    cookie: str = ""
) -> str:
    """
    Inspects a specific HTML element or component on a page by CSS selector (e.g. 'header', '.pricing-card', 'button').
    Returns its exact computed CSS, layout dimensions, typography, colors, and outer HTML snippet.

    Args:
        url: The URL of the webpage.
        selector: CSS selector for the target element (e.g. 'header', 'button.cta', '#hero').
        storage_state: Optional path to an authenticated session file ('auth.json').
        cookie: Optional direct session cookie ('MoodleSession=...').

    Returns:
        JSON string containing detailed computed styles and structural metrics.
    """
    try:
        res = await async_inspect_single_element(
            url,
            selector,
            storage_state=storage_state or None,
            cookies=cookie or None
        )
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error inspecting selector '{selector}' on {url}: {str(e)}"


@mcp.tool()
async def generate_tailwind_theme(
    url: str,
    storage_state: str = "",
    cookie: str = ""
) -> str:
    """
    Extracts the design tokens from a webpage and outputs a ready-to-paste Tailwind CSS configuration
    and CSS custom properties block.

    Args:
        url: The URL of the webpage to analyze.
        storage_state: Optional path to an authenticated session file ('auth.json').
        cookie: Optional direct session cookie ('MoodleSession=...').

    Returns:
        Tailwind config JavaScript and CSS variables snippet.
    """
    try:
        data = await async_extract_page_design_data(
            url,
            storage_state=storage_state or None,
            cookies=cookie or None
        )
        spec_md = generate_agent_design_spec(data, url)
        if "## 5. Ready-to-Paste Tailwind CSS Configuration" in spec_md:
            tailwind_part = spec_md.split("## 5. Ready-to-Paste Tailwind CSS Configuration")[1].split("---")[0]
            return f"### Extracted Tailwind Configuration for {url}\n\n{tailwind_part.strip()}"
        return spec_md
    except Exception as e:
        return f"Error generating Tailwind theme for {url}: {str(e)}"


@mcp.tool()
async def capture_page_screenshot(
    url: str,
    output_path: str = "",
    storage_state: str = "",
    cookie: str = ""
) -> str:
    """
    Captures a full-page high-resolution screenshot of a webpage for visual design reference
    and saves it to the configured directory or a custom path.

    Args:
        url: The URL of the webpage.
        output_path: Optional file path. If omitted, saves to the configured directory.
        storage_state: Optional path to an authenticated session file ('auth.json').
        cookie: Optional direct session cookie ('MoodleSession=...').

    Returns:
        Confirmation message with the absolute path of the saved screenshot.
    """
    try:
        if not output_path:
            out_dir = get_configured_output_dir()
            slug = _url_to_slug(url)
            output_path = str(out_dir / f"{slug}_preview.png")
        saved_path = await async_take_screenshot(
            url,
            output_path,
            full_page=True,
            storage_state=storage_state or None,
            cookies=cookie or None
        )
        return f"Full-page screenshot successfully captured and saved to: {saved_path}"
    except Exception as e:
        return f"Error capturing screenshot for {url}: {redact_sensitive_data(str(e))}"


@mcp.tool()
def check_for_updates() -> str:
    """
    Checks if a newer version of Design Extractor MCP is available in the official GitHub repository.
    Returns current status and instructions to upgrade if an update is found.
    """
    from updater import check_for_updates
    has_update, msg, remote_id = check_for_updates(force=True)
    if has_update:
        return f"UPDATE AVAILABLE: {msg}\nTo install the update, invoke the 'update_server' tool or run 'design-extractor update' in terminal."
    return f"UP TO DATE: {msg}"


@mcp.tool()
def update_server() -> str:
    """
    Pulls the latest code from GitHub and updates dependencies.
    Requires restarting the MCP client/agent afterwards to load new code.
    """
    from updater import apply_update
    ok, msg = apply_update()
    if ok:
        return f"SUCCESS: {msg}\nPlease restart your AI agent or reload your MCP server connection to use the updated version."
    return f"UPDATE FAILED: {msg}"


if __name__ == "__main__":
    mcp.run()

