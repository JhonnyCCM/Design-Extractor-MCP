"""
Web Design System, Layout & Structural Extractor Engine
Reverse-engineers complete visual design, typography, layout architecture,
DOM hierarchy patterns (div nesting, containers, grids), and outputs a master
AI Agent Prompt Instruction Sheet.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright

BROWSER_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

EXTRACTION_JS = """
() => {
    // Universal color normalizer via 1x1 canvas getImageData
    const canvas = document.createElement('canvas');
    canvas.width = 1;
    canvas.height = 1;
    const ctx = canvas.getContext('2d', { willReadFrequently: true });

    const normalizeColor = (colorStr) => {
        if (!colorStr || colorStr === 'transparent' || colorStr === 'rgba(0, 0, 0, 0)') return null;
        try {
            ctx.clearRect(0, 0, 1, 1);
            ctx.fillStyle = colorStr;
            ctx.fillRect(0, 0, 1, 1);
            const [r, g, b, a] = ctx.getImageData(0, 0, 1, 1).data;
            if (a === 0) return null;
            if (a < 255) {
                const alpha = Math.round((a / 255) * 100) / 100;
                return `rgba(${r}, ${g}, ${b}, ${alpha})`;
            }
            return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
        } catch (e) {
            return colorStr;
        }
    };

    const rgbToHex = normalizeColor;

    const cleanRadius = (r) => {
        if (!r || r === '0px') return null;
        if (r.includes('e+') || parseFloat(r) >= 999) return '9999px';
        return r;
    };

    const getLuminance = (colorStr) => {
        const hex = normalizeColor(colorStr);
        if (!hex) return 255;
        if (hex.startsWith('#') && hex.length >= 7) {
            const r = parseInt(hex.slice(1, 3), 16);
            const g = parseInt(hex.slice(3, 5), 16);
            const b = parseInt(hex.slice(5, 7), 16);
            return 0.299 * r + 0.587 * g + 0.114 * b;
        }
        return 128;
    };

    // Clean DOM node for skeleton preview
    const cleanElementSkeleton = (el, maxDepth = 3, currentDepth = 0) => {
        if (!el || currentDepth > maxDepth) return null;
        const tag = el.tagName.toLowerCase();
        if (['script', 'style', 'svg', 'noscript', 'iframe'].includes(tag)) return null;

        const classes = (el.className && typeof el.className === 'string') 
            ? el.className.split(' ').slice(0, 6).join(' ').trim() 
            : '';
        const id = el.id ? `#${el.id}` : '';
        const classStr = classes ? `.${classes.split(' ').join('.')}` : '';
        
        let children = [];
        if (currentDepth < maxDepth) {
            for (let child of el.children) {
                const childNode = cleanElementSkeleton(child, maxDepth, currentDepth + 1);
                if (childNode) children.push(childNode);
                if (children.length >= 5) break;
            }
        }

        return {
            tag,
            id: el.id || null,
            classes: classes || null,
            children: children.length > 0 ? children : null
        };
    };

    const formatSkeletonToTree = (node, indent = 0) => {
        if (!node) return '';
        const pad = '  '.repeat(indent);
        const classPart = node.classes ? ` class="${node.classes}"` : '';
        const idPart = node.id ? ` id="${node.id}"` : '';
        if (!node.children || node.children.length === 0) {
            return `${pad}<${node.tag}${idPart}${classPart} />\n`;
        }
        let out = `${pad}<${node.tag}${idPart}${classPart}>\n`;
        for (const c of node.children) {
            out += formatSkeletonToTree(c, indent + 1);
        }
        out += `${pad}</${node.tag}>\n`;
        return out;
    };

    // 0. Source Code & Framework Inspection
    const techStack = [];
    const htmlSnippet = document.documentElement.outerHTML.slice(0, 40000);

    if (document.querySelector('#__next') || window.__NEXT_DATA__) techStack.push('Next.js');
    if (document.querySelector('[data-reactroot]') || window.React) techStack.push('React');
    if (document.querySelector('[data-v-]') || window.__NUXT__) techStack.push('Vue / Nuxt');
    if (document.querySelector('[data-astro-cid-]')) techStack.push('Astro');
    if (document.querySelector('html.w-mod-js') || htmlSnippet.includes('wf-page')) techStack.push('Webflow');
    if (htmlSnippet.includes('cdn.shopify.com') || window.Shopify) techStack.push('Shopify');
    if (htmlSnippet.includes('wp-content') || htmlSnippet.includes('wp-includes')) techStack.push('WordPress');

    // Utility classes and Tailwind detection
    let tailwindDetected = false;
    const sampledUtilityClasses = [];
    const twPattern = /^(flex|grid|hidden|block|inline|text-|bg-|p[xytrbl]?-|m[xytrbl]?-|rounded|border|shadow|max-w-|w-|h-|gap-|space-|items-|justify-|leading-|font-|transition-|duration-|hover:|dark:|sm:|md:|lg:|xl:|2xl:)/;
    let twCount = 0;
    const allElsForTW = document.querySelectorAll('*');
    for (let i = 0; i < Math.min(allElsForTW.length, 1200); i++) {
        const clsList = allElsForTW[i].classList;
        for (let j = 0; j < clsList.length; j++) {
            const c = clsList[j];
            if (twPattern.test(c)) {
                twCount++;
                if (sampledUtilityClasses.length < 20 && !sampledUtilityClasses.includes(c)) {
                    sampledUtilityClasses.push(c);
                }
            }
        }
    }
    if (twCount > 15 || htmlSnippet.includes('tailwind')) {
        techStack.push('Tailwind CSS');
        tailwindDetected = true;
    }

    // Stylesheet rules: Media query breakpoints & Keyframe animations
    const mediaBreakpoints = new Set();
    const keyframes = [];
    try {
        for (const sheet of document.styleSheets) {
            try {
                for (const rule of sheet.cssRules) {
                    if (rule.type === CSSRule.MEDIA_RULE) {
                        const cond = rule.conditionText || (rule.media && rule.media.mediaText);
                        if (cond) {
                            const matches = cond.match(/(?:min-width|max-width):\s*[\d.]+(?:px|rem|em)/g);
                            if (matches) {
                                matches.forEach(m => mediaBreakpoints.add(m));
                            }
                        }
                    } else if (rule.type === CSSRule.KEYFRAMES_RULE) {
                        if (keyframes.length < 6 && !keyframes.includes(rule.name)) {
                            keyframes.push(rule.name);
                        }
                    }
                }
            } catch (e) {}
        }
    } catch (e) {}

    // Meta tags
    const metaTags = {};
    document.querySelectorAll('meta[name], meta[property]').forEach(m => {
        const key = m.getAttribute('name') || m.getAttribute('property');
        const val = m.getAttribute('content');
        if (key && val && ['description', 'viewport', 'generator', 'og:title'].includes(key)) {
            metaTags[key] = val.slice(0, 80);
        }
    });

    // 1. External Font links
    const externalFonts = [];
    document.querySelectorAll('link[rel="stylesheet"]').forEach(l => {
        if (l.href && (l.href.includes('fonts.googleapis.com') || l.href.includes('use.typekit.net') || l.href.includes('font'))) {
            externalFonts.push(l.href);
        }
    });

    // 2. CSS Custom Properties (:root / html / body)
    const cssVariables = {};
    try {
        for (const sheet of document.styleSheets) {
            try {
                for (const rule of sheet.cssRules) {
                    if (rule.selectorText && (rule.selectorText.includes(':root') || rule.selectorText === 'html' || rule.selectorText === 'body')) {
                        if (rule.style) {
                            for (let i = 0; i < rule.style.length; i++) {
                                const prop = rule.style[i];
                                if (prop.startsWith('--')) {
                                    const val = rule.style.getPropertyValue(prop).trim();
                                    if (val && !cssVariables[prop]) {
                                        cssVariables[prop] = val;
                                    }
                                }
                            }
                        }
                    }
                }
            } catch (e) {}
        }
    } catch (e) {}

    // 3. Body & Theme baseline
    const bodyEl = document.body;
    const bodyStyle = window.getComputedStyle(bodyEl);
    const htmlStyle = window.getComputedStyle(document.documentElement);
    const bodyBg = rgbToHex(bodyStyle.backgroundColor) || rgbToHex(htmlStyle.backgroundColor) || '#ffffff';
    const bodyColor = rgbToHex(bodyStyle.color) || '#111827';
    const isDark = getLuminance(bodyBg) < 128;

    // Helper for computed typography
    const extractTypo = (el) => {
        if (!el) return null;
        const s = window.getComputedStyle(el);
        return {
            fontFamily: s.fontFamily.split(',')[0].replace(/['"]/g, '').trim(),
            fullFontFamily: s.fontFamily,
            fontSize: s.fontSize,
            fontWeight: s.fontWeight,
            lineHeight: s.lineHeight,
            letterSpacing: s.letterSpacing,
            color: rgbToHex(s.color),
            textTransform: s.textTransform !== 'none' ? s.textTransform : null
        };
    };

    const typography = {
        h1: extractTypo(document.querySelector('h1')),
        h2: extractTypo(document.querySelector('h2')),
        h3: extractTypo(document.querySelector('h3')),
        h4: extractTypo(document.querySelector('h4')),
        p: extractTypo(document.querySelector('p')),
        body: extractTypo(document.body)
    };

    // 4. Element Aggregations
    const bgFreq = {};
    const textFreq = {};
    const borderFreq = {};
    const radiusFreq = {};
    const shadowFreq = {};
    const containerWidths = {};
    const gapFreq = {};
    let flexCount = 0;
    let gridCount = 0;

    const allEls = document.querySelectorAll('*');
    const limit = Math.min(allEls.length, 2500);

    for (let i = 0; i < limit; i++) {
        const el = allEls[i];
        const s = window.getComputedStyle(el);

        const bg = rgbToHex(s.backgroundColor);
        if (bg && bg !== 'rgba(0, 0, 0, 0)') {
            bgFreq[bg] = (bgFreq[bg] || 0) + 1;
        }

        const col = rgbToHex(s.color);
        if (col) {
            textFreq[col] = (textFreq[col] || 0) + 1;
        }

        if (s.borderWidth && s.borderWidth !== '0px') {
            const bCol = rgbToHex(s.borderColor);
            if (bCol) borderFreq[bCol] = (borderFreq[bCol] || 0) + 1;
        }

        const cr = cleanRadius(s.borderRadius);
        if (cr) {
            radiusFreq[cr] = (radiusFreq[cr] || 0) + 1;
        }

        if (s.boxShadow && s.boxShadow !== 'none') {
            shadowFreq[s.boxShadow] = (shadowFreq[s.boxShadow] || 0) + 1;
        }

        if (s.display === 'flex' || s.display === 'inline-flex') flexCount++;
        if (s.display === 'grid' || s.display === 'inline-grid') gridCount++;

        if (s.gap && s.gap !== 'normal' && s.gap !== '0px') {
            gapFreq[s.gap] = (gapFreq[s.gap] || 0) + 1;
        }

        if (s.maxWidth && s.maxWidth !== 'none' && s.maxWidth !== '100%' && s.maxWidth.endsWith('px')) {
            const pxVal = parseInt(s.maxWidth);
            if (pxVal >= 600 && pxVal <= 1920) {
                containerWidths[s.maxWidth] = (containerWidths[s.maxWidth] || 0) + 1;
            }
        }
    }

    const getTopKeys = (dict, count = 5) => Object.entries(dict)
        .sort((a, b) => b[1] - a[1])
        .slice(0, count)
        .map(([k]) => k);

    // 5. Structural Landmarks & Skeletons
    // Navbar
    const headerEl = document.querySelector('header') || document.querySelector('nav') || document.querySelector('[role="banner"]');
    let navInfo = null;
    let headerSkeleton = null;
    if (headerEl) {
        const s = window.getComputedStyle(headerEl);
        navInfo = {
            tag: headerEl.tagName.toLowerCase(),
            position: s.position,
            backgroundColor: rgbToHex(s.backgroundColor),
            backdropFilter: s.backdropFilter !== 'none' ? s.backdropFilter : null,
            borderBottom: `${s.borderBottomWidth} ${s.borderBottomStyle} ${rgbToHex(s.borderBottomColor)}`,
            height: s.height,
            padding: s.padding,
            isSticky: s.position === 'sticky' || s.position === 'fixed'
        };
        headerSkeleton = formatSkeletonToTree(cleanElementSkeleton(headerEl, 3));
    }

    // Hero Section
    const heroEl = document.querySelector('main > section:first-of-type, header + section, [class*="hero"], main > div:first-of-type');
    let heroSkeleton = null;
    if (heroEl) {
        heroSkeleton = formatSkeletonToTree(cleanElementSkeleton(heroEl, 3));
    }

    // Card or Feature Section
    const cardEl = document.querySelector('[class*="card"], article, [class*="feature"], [class*="pricing"], [class*="box"]');
    let cardSkeleton = null;
    let cardInfo = null;
    if (cardEl) {
        const s = window.getComputedStyle(cardEl);
        cardInfo = {
            backgroundColor: rgbToHex(s.backgroundColor),
            border: `${s.borderWidth} ${s.borderStyle} ${rgbToHex(s.borderColor)}`,
            borderRadius: s.borderRadius,
            boxShadow: s.boxShadow !== 'none' ? s.boxShadow : null,
            padding: s.padding
        };
        cardSkeleton = formatSkeletonToTree(cleanElementSkeleton(cardEl, 3));
    }

    // Buttons
    const buttons = [];
    document.querySelectorAll('button, a[role="button"], .btn').forEach(btn => {
        if (buttons.length < 4 && btn.offsetParent !== null) {
            const s = window.getComputedStyle(btn);
            const text = (btn.innerText || btn.textContent || '').trim();
            if (text.length > 0 && text.length < 35) {
                buttons.push({
                    text: text.slice(0, 25),
                    bg: rgbToHex(s.backgroundColor),
                    color: rgbToHex(s.color),
                    border: `${s.borderWidth} ${s.borderStyle} ${rgbToHex(s.borderColor)}`,
                    borderRadius: s.borderRadius,
                    padding: s.padding,
                    fontSize: s.fontSize,
                    fontWeight: s.fontWeight,
                    boxShadow: s.boxShadow !== 'none' ? s.boxShadow : null
                });
            }
        }
    });

    // Badges / Pills
    const badges = [];
    document.querySelectorAll('[class*="badge"], [class*="tag"], [class*="pill"], [class*="chip"]').forEach(el => {
        if (badges.length < 3 && el.offsetParent !== null) {
            const s = window.getComputedStyle(el);
            const text = (el.innerText || '').trim();
            if (text.length > 1 && text.length < 25) {
                badges.push({
                    text: text,
                    bg: rgbToHex(s.backgroundColor),
                    color: rgbToHex(s.color),
                    borderRadius: s.borderRadius,
                    padding: s.padding,
                    fontSize: s.fontSize,
                    border: `${s.borderWidth} ${s.borderStyle} ${rgbToHex(s.borderColor)}`
                });
            }
        }
    });

    // Layout Paradigm
    const layoutParadigm = {
        primaryLayout: gridCount > flexCount ? 'CSS Grid Oriented' : 'Flexbox Oriented',
        flexUsageCount: flexCount,
        gridUsageCount: gridCount,
        commonGaps: getTopKeys(gapFreq, 4)
    };

    return {
        title: document.title,
        url: window.location.href,
        isDark,
        bodyBg,
        bodyColor,
        externalFonts,
        cssVariables,
        typography,
        colors: {
            backgrounds: getTopKeys(bgFreq, 8),
            texts: getTopKeys(textFreq, 8),
            borders: getTopKeys(borderFreq, 6)
        },
        radii: getTopKeys(radiusFreq, 6),
        shadows: getTopKeys(shadowFreq, 4),
        containers: getTopKeys(containerWidths, 5),
        layoutParadigm,
        techStack,
        mediaBreakpoints: Array.from(mediaBreakpoints),
        keyframes,
        sampledUtilityClasses,
        metaTags,
        navigation: navInfo,
        headerSkeleton,
        heroSkeleton,
        cardInfo,
        cardSkeleton,
        buttons,
        badges
    };
}
"""


def extract_page_design_data(url: str, wait_seconds: int = 2) -> Dict[str, Any]:
    """Inspects a page using Playwright and extracts comprehensive design data."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=BROWSER_USER_AGENT,
            viewport={"width": 1440, "height": 900}
        )
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=40000)
        try:
            page.wait_for_load_state("networkidle", timeout=7000)
        except Exception:
            pass
        page.wait_for_timeout(wait_seconds * 1000)

        data = page.evaluate(EXTRACTION_JS)
        browser.close()
        return data


def inspect_single_element(url: str, selector: str) -> Dict[str, Any]:
    """Inspects a specific element on a page by CSS selector."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=BROWSER_USER_AGENT, viewport={"width": 1440, "height": 900})
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=35000)
        page.wait_for_timeout(2000)

        js = f"""(sel) => {{
            const el = document.querySelector(sel);
            if (!el) return {{ error: 'Element not found: ' + sel }};
            const s = window.getComputedStyle(el);
            const rgbToHex = (color) => {{
                if (!color || color === 'transparent' || color === 'rgba(0, 0, 0, 0)') return null;
                const match = color.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)(?:,\\s*([\\d.]+))?\\)/);
                if (!match) return color;
                const r = parseInt(match[1]);
                const g = parseInt(match[2]);
                const b = parseInt(match[3]);
                const a = match[4] !== undefined ? parseFloat(match[4]) : 1;
                return a < 1 ? `rgba(${{r}}, ${{g}}, ${{b}}, ${{a}})` : "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
            }};

            return {{
                tagName: el.tagName.toLowerCase(),
                className: el.className,
                computedStyles: {{
                    display: s.display,
                    flexDirection: s.flexDirection,
                    gridTemplateColumns: s.gridTemplateColumns,
                    gap: s.gap,
                    width: s.width,
                    maxWidth: s.maxWidth,
                    padding: s.padding,
                    margin: s.margin,
                    backgroundColor: rgbToHex(s.backgroundColor),
                    color: rgbToHex(s.color),
                    fontFamily: s.fontFamily,
                    fontSize: s.fontSize,
                    fontWeight: s.fontWeight,
                    lineHeight: s.lineHeight,
                    borderRadius: s.borderRadius,
                    border: `${{s.borderWidth}} ${{s.borderStyle}} ${{rgbToHex(s.borderColor)}}`,
                    boxShadow: s.boxShadow,
                    backdropFilter: s.backdropFilter
                }},
                outerHTMLSample: el.outerHTML.slice(0, 500)
            }};
        }}"""

        result = page.evaluate(js, selector)
        browser.close()
        return result


def take_screenshot(url: str, output_path: str, full_page: bool = True) -> str:
    """Takes a full-page or viewport screenshot of a webpage."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=BROWSER_USER_AGENT, viewport={"width": 1440, "height": 900})
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=35000)
        page.wait_for_timeout(2500)

        out_file = Path(output_path).resolve()
        out_file.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(out_file), full_page=full_page)
        browser.close()
        return str(out_file)


async def async_extract_page_design_data(url: str, wait_seconds: int = 2) -> Dict[str, Any]:
    """Inspects a page using Playwright Async API and extracts comprehensive design data."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=BROWSER_USER_AGENT,
            viewport={"width": 1440, "height": 900}
        )
        page = await context.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=40000)
        try:
            await page.wait_for_load_state("networkidle", timeout=7000)
        except Exception:
            pass
        await page.wait_for_timeout(wait_seconds * 1000)

        data = await page.evaluate(EXTRACTION_JS)
        await browser.close()
        return data


async def async_inspect_single_element(url: str, selector: str) -> Dict[str, Any]:
    """Inspects a specific element on a page by CSS selector using Async API."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=BROWSER_USER_AGENT, viewport={"width": 1440, "height": 900})
        page = await context.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=35000)
        await page.wait_for_timeout(2000)

        js = f"""(sel) => {{
            const el = document.querySelector(sel);
            if (!el) return {{ error: 'Element not found: ' + sel }};
            const s = window.getComputedStyle(el);
            const rgbToHex = (color) => {{
                if (!color || color === 'transparent' || color === 'rgba(0, 0, 0, 0)') return null;
                const match = color.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)(?:,\\s*([\\d.]+))?\\)/);
                if (!match) return color;
                const r = parseInt(match[1]);
                const g = parseInt(match[2]);
                const b = parseInt(match[3]);
                const a = match[4] !== undefined ? parseFloat(match[4]) : 1;
                return a < 1 ? `rgba(${{r}}, ${{g}}, ${{b}}, ${{a}})` : "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
            }};

            return {{
                tagName: el.tagName.toLowerCase(),
                className: el.className,
                computedStyles: {{
                    display: s.display,
                    flexDirection: s.flexDirection,
                    gridTemplateColumns: s.gridTemplateColumns,
                    gap: s.gap,
                    width: s.width,
                    maxWidth: s.maxWidth,
                    padding: s.padding,
                    margin: s.margin,
                    backgroundColor: rgbToHex(s.backgroundColor),
                    color: rgbToHex(s.color),
                    fontFamily: s.fontFamily,
                    fontSize: s.fontSize,
                    fontWeight: s.fontWeight,
                    lineHeight: s.lineHeight,
                    borderRadius: s.borderRadius,
                    border: `${{s.borderWidth}} ${{s.borderStyle}} ${{rgbToHex(s.borderColor)}}`,
                    boxShadow: s.boxShadow,
                    backdropFilter: s.backdropFilter
                }},
                outerHTMLSample: el.outerHTML.slice(0, 500)
            }};
        }}"""

        result = await page.evaluate(js, selector)
        await browser.close()
        return result


async def async_take_screenshot(url: str, output_path: str, full_page: bool = True) -> str:
    """Takes a full-page or viewport screenshot using Async API."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=BROWSER_USER_AGENT, viewport={"width": 1440, "height": 900})
        page = await context.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=35000)
        await page.wait_for_timeout(2500)

        out_file = Path(output_path).resolve()
        out_file.parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(out_file), full_page=full_page)
        await browser.close()
        return str(out_file)



def generate_agent_design_spec(data: Dict[str, Any], url: str) -> str:
    """
    Transforms extracted design data into a master Markdown specification
    and agent instruction sheet.
    """
    is_dark = data.get("isDark", False)
    theme_name = "Modern Dark Theme" if is_dark else "Clean Light Theme"
    body_bg = data.get("bodyBg", "#ffffff")
    body_color = data.get("bodyColor", "#111827")
    
    # Typography
    typo = data.get("typography", {})
    body_typo = typo.get("body") or typo.get("p") or {}
    h1_typo = typo.get("h1") or {}
    h2_typo = typo.get("h2") or {}
    h3_typo = typo.get("h3") or {}
    
    font_family_primary = body_typo.get("fontFamily", "Inter, system-ui, sans-serif")
    font_family_heading = (h1_typo.get("fontFamily") if h1_typo else None) or font_family_primary
    
    # Colors
    bg_colors = data.get("colors", {}).get("backgrounds", [])
    text_colors = data.get("colors", {}).get("texts", [])
    border_colors = data.get("colors", {}).get("borders", [])
    
    primary_accent = None
    buttons = data.get("buttons", [])
    for b in buttons:
        btn_bg = b.get("bg")
        if btn_bg and btn_bg != body_bg and btn_bg not in ["#000000", "#ffffff", "transparent"]:
            primary_accent = btn_bg
            break
            
    if not primary_accent and len(bg_colors) > 1:
        for c in bg_colors:
            if c != body_bg and c not in ["#000000", "#ffffff"]:
                primary_accent = c
                break
    if not primary_accent:
        primary_accent = "#2563eb"  # fallback brand blue

    # Surface & Card Background
    card_info = data.get("cardInfo") or {}
    surface_bg = card_info.get("backgroundColor")
    if not surface_bg or surface_bg == "transparent":
        surface_bg = bg_colors[1] if len(bg_colors) > 1 and bg_colors[1] != body_bg else ("#18181b" if is_dark else "#ffffff")

    # Radii
    radii = data.get("radii", ["8px", "12px", "9999px"])
    shadows = data.get("shadows", [])
    containers = data.get("containers", ["1280px"])
    max_container = containers[0] if containers else "1280px"

    # Layout Paradigm
    layout_p = data.get("layoutParadigm", {})
    common_gaps = layout_p.get("commonGaps", ["16px", "24px", "32px"])

    # Navigation & Landmarks
    nav = data.get("navigation") or {}
    header_skeleton = data.get("headerSkeleton")
    hero_skeleton = data.get("heroSkeleton")
    card_skeleton = data.get("cardSkeleton")

    # Source Code Intelligence
    tech_stack = data.get("techStack", [])
    breakpoints = data.get("mediaBreakpoints", [])
    keyframes = data.get("keyframes", [])
    tw_classes = data.get("sampledUtilityClasses", [])

    # Build Master Markdown
    md = f"""# Master Web Architecture & Design System Specification
> **Target Source:** `{url}`  
> **Aesthetic Archetype:** `{theme_name}`  
> **Intended Recipient:** AI Agent / Frontend Engineer building a clone or matching interface.

---

## 1. Aesthetic Identity & Visual Philosophy
This site uses a **{theme_name}** architecture characterized by:
- **Base Canvas:** Background `{body_bg}` with high-contrast text `{body_color}`.
- **Card & Surface Treatment:** Surfaces sit on `{surface_bg}` with subtle 1px border `{border_colors[0] if border_colors else '1px solid rgba(255, 255, 255, 0.08)'}` and border-radius `{radii[0] if radii else '12px'}`.
- **Primary Accent / Brand Color:** `{primary_accent}` used for primary interactive states, badges, and key CTA buttons.
- **Layout Rhythm:** Heavy reliance on **{layout_p.get('primaryLayout', 'Flexbox and CSS Grid')}** with container max-width `{max_container}` and section vertical breathing room (`py-16` / `py-24`).

---

## 2. Source Code & Architecture Intelligence
- **Frameworks & Tech Stack Detected:** {", ".join([f"`{t}`" for t in tech_stack]) if tech_stack else '`Custom HTML/CSS Stack`'}
- **Responsive Media Query Breakpoints:** {", ".join([f"`{b}`" for b in breakpoints[:6]]) if breakpoints else '`Fluid responsive (standard breakpoints)`'}
- **Stylesheet Keyframe Animations:** {", ".join([f"`{k}`" for k in keyframes]) if keyframes else '`Standard transition transitions`'}
- **Observed Utility Classes (Developer Intent):** {", ".join([f"`{c}`" for c in tw_classes[:14]]) if tw_classes else '`Semantic / Component-based CSS`'}

---

## 3. Design Tokens & Visual Specs

### Color Palette
| Token | Value | Role / Usage |
| :--- | :--- | :--- |
| **Canvas / Background** | `{body_bg}` | Root page body background |
| **Surface / Card** | `{surface_bg}` | Cards, dropdowns, panels, modal overlays |
| **Primary Text** | `{body_color}` | Headings, titles, high-emphasis copy |
| **Primary Brand Accent** | `{primary_accent}` | CTA buttons, active links, brand highlights |
| **Border Tone** | `{border_colors[0] if border_colors else '#e5e7eb'}` | Structural card borders, dividers, inputs |

### Typography Scale & Hierarchy
- **Heading Font Family:** `{font_family_heading}`
- **Body Font Family:** `{font_family_primary}`

| Level | Size | Weight | Line Height | Tracking | Text Color |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **H1 (Hero Title)** | `{h1_typo.get('fontSize', '48px')}` | `{h1_typo.get('fontWeight', '700')}` | `{h1_typo.get('lineHeight', '1.1')}` | `{h1_typo.get('letterSpacing', '-0.02em')}` | `{h1_typo.get('color', body_color)}` |
| **H2 (Section Header)** | `{h2_typo.get('fontSize', '32px')}` | `{h2_typo.get('fontWeight', '600')}` | `{h2_typo.get('lineHeight', '1.25')}` | `{h2_typo.get('letterSpacing', 'normal')}` | `{h2_typo.get('color', body_color)}` |
| **H3 (Card Title)** | `{h3_typo.get('fontSize', '20px')}` | `{h3_typo.get('fontWeight', '600')}` | `{h3_typo.get('lineHeight', '1.4')}` | `normal` | `{h3_typo.get('color', body_color)}` |
| **Body (Paragraph)** | `{body_typo.get('fontSize', '16px')}` | `{body_typo.get('fontWeight', '400')}` | `{body_typo.get('lineHeight', '1.5')}` | `normal` | `{body_typo.get('color', body_color)}` |

### Radii, Shadows & Spacing Scales
- **Border Radii:** {", ".join([f"`{r}`" for r in radii[:4]])}
- **Common Grid / Flex Gaps:** {", ".join([f"`{g}`" for g in common_gaps[:3]])}
- **Box Shadows:**
{chr(10).join([f"  - `{s}`" for s in shadows[:3]]) if shadows else "  - `0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06)`"}

---

## 4. Structural Blueprint & Div / Container Nesting Rules

### Container Architecture & Nesting Paradigm
The page enforces a strict, symmetrical container hierarchy for almost all sections:
```html
<!-- STANDARD SECTION WRAPPER PATTERN -->
<section class="w-full py-16 md:py-24 relative overflow-hidden">
  <!-- Inner Max-Width Container -->
  <div class="max-w-[{max_container}] mx-auto px-4 sm:px-6 lg:px-8">
    
    <!-- Section Header (Centered or Left-Aligned) -->
    <div class="max-w-2xl mx-auto text-center mb-12 md:mb-16">
      <h2 class="text-3xl font-bold tracking-tight">{h2_typo.get('fontSize', '32px')} Headline</h2>
      <p class="mt-4 text-base text-muted-foreground">Descriptive subtitle paragraph.</p>
    </div>

    <!-- Responsive Grid of Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- Card items here -->
    </div>

  </div>
</section>
```

### Observed Component DOM Skeletons

#### 1. Header / Navigation Bar Skeleton
{f'```html{chr(10)}{header_skeleton}```' if header_skeleton else 'No distinct header skeleton captured.'}
- **Header Positioning:** `{nav.get('position', 'sticky')}` {'(sticky top with backdrop blur)' if nav.get('isSticky') else ''}
- **Backdrop Effect:** `{nav.get('backdropFilter', 'backdrop-blur-md') if nav.get('backdropFilter') else 'Solid'}`
- **Border Bottom:** `{nav.get('borderBottom', '1px solid border')}`

#### 2. Hero Section Skeleton
{f'```html{chr(10)}{hero_skeleton}```' if hero_skeleton else 'No distinct hero section captured.'}

#### 3. Card / Box Skeleton
{f'```html{chr(10)}{card_skeleton}```' if card_skeleton else 'Standard card with border-radius, 1px border, and inner padding.'}

---

## 5. Ready-to-Paste Tailwind CSS Configuration

```javascript
/** @type {{import('tailwindcss').Config}} */
module.exports = {{
  darkMode: '{'class' if is_dark else 'media'}',
  theme: {{
    extend: {{
      colors: {{
        background: '{body_bg}',
        foreground: '{body_color}',
        primary: {{
          DEFAULT: '{primary_accent}',
          foreground: '#ffffff',
        }},
        card: {{
          DEFAULT: '{surface_bg}',
          foreground: '{body_color}',
        }},
        border: '{border_colors[0] if border_colors else "#e5e7eb"}',
      }},
      fontFamily: {{
        sans: ['{font_family_primary}', 'sans-serif'],
        heading: ['{font_family_heading}', 'sans-serif'],
      }},
      borderRadius: {{
        DEFAULT: '{radii[0] if radii else "8px"}',
        card: '{radii[1] if len(radii) > 1 else (radii[0] if radii else "12px")}',
        pill: '9999px',
      }},
      maxWidth: {{
        container: '{max_container}',
      }}
    }},
  }},
  plugins: [],
}}
```

---

## 6. Directives & Rules Sheet for the AI Agent

> **Instructions for the Agent:**  
> When constructing web pages or UI components for this project, you must strictly comply with the following instructions:

```markdown
### AGENT MASTER DIRECTIVES: DESIGN FIDELITY RULES

1. **CANVAS & PALETTE CONSTRAINTS:**
   - Always set the root canvas to `{body_bg}` and default text to `{body_color}`.
   - All card surfaces, dropdowns, and elevated panels MUST use `{surface_bg}`.
   - Use `{primary_accent}` ONLY for primary buttons, active states, and focal accents. Do not invent alternative bright colors.
   - Use `{border_colors[0] if border_colors else '1px solid rgba(255, 255, 255, 0.08)'}` for card borders.

2. **TYPOGRAPHY RULES:**
   - Headings MUST use `{font_family_heading}`.
   - Body copy and UI labels MUST use `{font_family_primary}`.
   - Hero titles (H1) must follow size `{h1_typo.get('fontSize', '48px')}` with tracking `{h1_typo.get('letterSpacing', '-0.02em')}` and weight `{h1_typo.get('fontWeight', '700')}`.
   - Never use arbitrary font weights; stick to 400 (normal), 500 (medium), 600 (semibold), and 700 (bold).

3. **STRUCTURAL & CONTAINER RULES:**
   - Wrap EVERY major section in:
     `<section class="py-16 md:py-24"><div class="max-w-[{max_container}] mx-auto px-4 sm:px-6 lg:px-8">...</div></section>`
   - Do NOT mix container max-widths across different sections on the same page.
   - Multi-column grids must use responsive patterns:
     `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6` (or `gap-8`).

4. **COMPONENT RULES:**
   - **Buttons:**
     - Primary: Background `{primary_accent}`, text color `#ffffff`, rounded `{buttons[0].get('borderRadius', radii[0] if radii else '8px') if buttons else '8px'}`, padding `10px 20px`, font-weight `600`, transition `all 0.2s`.
     - Secondary/Ghost: Transparent or subtle surface background with 1px border matching the border token.
   - **Cards:**
     - Background `{surface_bg}`, border `{border_colors[0] if border_colors else '1px solid border'}`, rounded `{radii[0] if radii else '12px'}`, padding `24px` (`p-6`), soft shadow.
   - **Badges:**
     - Pill shaped (`rounded-full`), small font (`text-xs`), subtle background with accent color.
```
"""
    return md
