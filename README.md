# dsi-puh-lus

A custom [EmulationStation](https://emulationstation.org/) theme for [ROCKNIX](https://github.com/ROCKNIX/distribution), built specifically for the dual-screen **Anbernic RG DS**. It splits ES's 1920×480 canvas into a proper top-screen / bottom-screen layout — system and game art, status info, and RetroAchievements data on top; navigation and game lists on the bottom — instead of stretching a single-screen theme across both panels.

## Requirements

- **Hardware**: [Anbernic RG DS](https://anbernic.com/products/rgds)
- **Firmware**: [ROCKNIX](https://github.com/ROCKNIX/distribution/releases)

## Features

- Dual-screen-aware layout: the canvas is split into three 640px columns (top screen, bottom screen, off-screen bleed), and every element respects that boundary
- Selectable backgrounds ("Castlevania Throne", "Mario Castle") via ES's subset menu
- Hero/logo art with a soft white outline so dark artwork stays visible against dark backgrounds
- Custom system carousel with a golden selection glow and animated pointer
- Styled game list with a translucent panel and resized box art
- Live RetroAchievements username shown in the top status bar
- Status indicators (clock, battery, network) themed to match the UI
- Bundled scripts: theme enable/launch from the Ports menu, and a Python ScreenScraper helper for scraping over SSH

## Written in

- EmulationStation theme XML (`formatVersion 7`)
- Bash (enable/launch scripts)
- Python (ScreenScraper helper, asset-prep tooling)

## Installation

See [INSTALL.txt](INSTALL.txt).

## Known issue: on-screen keyboard positioning

The `wvkbd` on-screen keyboard sometimes appears in inconsistent positions across different text-input screens (e.g. WiFi setup vs. RetroAchievements login). This **cannot be fixed from the theme** — `wvkbd`'s placement is controlled entirely by the `sway` compositor's window/output focus handling via the Wayland `zwp_text_input_v3` protocol, which the theme XML has no hooks into. A real fix would need either a `sway` `for_window` rule shipped at the OS level or an upstream ES patch making the keyboard dual-screen-aware.

## Known issue: scraper on-screen notification doesn't appear
Scraper batch progress overlay renders off-screen — When running a batch scrape, the progress notification doesn't appear on screen. ROCKNIX's ES fork has no theme-able scraper view; the overlay is a hardcoded C++ component pinned to the top-right of the 1920px canvas — which lands in the off-screen third column on this dual-screen layout. Theme-side styling (fonts/colors) still applies, but position can't be fixed without an upstream patch. Workaround: use the bundled scrape_screenscraper.py to scrape over SSH instead.

## Credits

- **[beebono](https://github.com/beebono/dii-ess-aye)** — creator of the original `dii-ess-aye` theme this is forked from
- **ravage_savage** (Reddit) — background artwork; see their awesome upgrade via Reddit.(https://www.reddit.com/u/ravage_savage/s/8Ik7afKkzw)
- **[Ant](https://github.com/anthonycaccese)** — status and slot icons, and their implementation
- **[Jeod](https://github.com/JeodC)** — testing the Thor variant
- **[Zoidburg13](https://github.com/Zoidburg13)** — system icons
- **Dan Patric** — console logos, from [Console Logos: Professionally Redrawn (plus Official Versions)](https://archive.org/details/console-logos-professionally-redrawn-plus-official-versions)
- **AnB** - A heartfelt thanks to my wife, who always listens to my rambling without understanding a single word of it.

## Trademarks & attribution

- "Castlevania Throne" is derived from *Castlevania: Symphony of the Night* artwork — Castlevania belongs to Konami.
- "Mario Castle" depicts SMB. artwork — SMB belongs to the big N. The original artist is unknown to us; if you made this piece, get in touch and we'll credit you.

All trademarks and copyrighted artwork remain the property of their respective owners. This is a fan-made, non-commercial theme shared with the ROCKNIX/EmulationStation community.
