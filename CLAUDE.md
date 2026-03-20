# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Mutti** is a static photography website showcasing photographs of Angela Merkel. It's a purely visual/artistic project — no political intent. The site is labeled "beta".

## Development

This is a plain HTML/CSS/JS project with no build tools, bundler, or package manager. To develop:

- Open `index.html` directly in a browser, or use any local server (e.g., `python3 -m http.server`)
- There are no tests, linting, or build commands

## Architecture

**Pages:**
- `index.html` — Landing page with hero section, animated about text, and a parallax photo gallery leading to Categories
- `Categories.html` — Displays photo categories (Animal, Food&Beverage, Vintage, Technology, Transport, Sport) as cards, plus a Random section. Has its own inline `<style>` and `<script>` blocks (not using the shared CSS)

**JavaScript:**
- `items.js` — Data module (ES module with `export`) containing an array of photo objects. Each item has: `img` (external URL), `alt`, `legende`, `id`, `parllaxSpeed`, and optionally `place`, `category`, `keyWord`
- `main.js` — Handles the scroll-triggered text reveal animation on the landing page using SplitType + GSAP

**Styles:**
- `styles.css` — Shared styles for `index.html` (hero, about section, footer gallery, responsive breakpoints)
- `Categories.html` has all its CSS inline in a `<style>` tag

**Key external dependencies (loaded via CDN):**
- GSAP 3.12.5 + ScrollTrigger — scroll-based animations and parallax
- SplitType — text splitting for word-by-word reveal animation
- Grained.js — film grain effect (currently commented out)
- Google Fonts: Pirata One (logo font)
- Adobe Typekit: ivysoft-variable (used in Categories page headings)

## Important Patterns

- The landing page gallery is built dynamically from `items.js` with absolute positioning and mouse-driven parallax via GSAP
- Images are mostly hosted externally (various news/media URLs), not stored locally. Local images are gallery thumbnails and UI icons
- Responsive design uses two sets of hardcoded position arrays (`itemPositionsLarge` / `itemPositionsSmall`) switching at 768px, plus CSS media queries at 576px, 768px, 992px, 1024px, and 1200px
- The `Categories.html` page uses GSAP ScrollTrigger timelines for card entrance animations
- Comments in both French and English appear throughout the code
