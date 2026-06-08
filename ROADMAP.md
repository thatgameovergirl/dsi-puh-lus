# dsi-puh-lus — Build Roadmap

EmulationStation theme for ROCKNIX on Anbernic RG DS.

## Device facts (CORRECTED — verified via swaymsg get_tree)

- ES is launched at **1920×480** (forced resolution; `fbset` reporting 640×480 was the
  legacy console fb and is misleading under Wayland/sway).
- sway lays the two 640×480 panels out **side by side** in compositor space (DSI-2 @ x:0,
  DSI-1 @ x:640 → 1280×480 desktop). ES's 1920 canvas maps as THREE columns:
  - X 0.000–0.333 (col 1) = **TOP** screen (DSI-2)
  - X 0.333–0.666 (col 2) = **BOTTOM** screen (DSI-1)
  - X 0.666–1.000 (col 3) = **off-screen** (beyond the 1280 desktop) — keep empty
- The split is **horizontal in theme coords (X)**, NOT vertical. No stretch; native 640×480.
- `theme.xml` MUST gate on `${screen.width} == 1920` (gating on 640 = theme never loads,
  ES shows its bare default — this was the cause of "no images / huge fonts").
- **Keyboard is `wvkbd`** drawn by the sway compositor — NOT an ES theme element.
  Cannot be moved from the theme. Upstream fix exists (ROCKNIX commit "Move
  wlr_virtual_keyboard to DUAL_SCREEN block"); otherwise a manual sway config edit.

---

## Phase 1 — Scaffolding
*Trivial. Goal: theme loads on device without errors.*

- [x] Create folder structure and `theme.xml` with resolution detection for 640×480
- [x] Copy `assets/` from `dii-ess-aye` (fonts, system logos, sounds, UI images)
- [x] Create empty placeholder XMLs for each view (`system`, `gamecarousel`, `menu`)
- [x] Drop onto device, confirm ES loads the theme

---

## Phase 2 — Base layout
*Easy. Goal: both zones are visually distinct and correctly positioned.*

- [x] Full-canvas background image or color
- [x] Visual boundary at Y=0.5 (dividing line or distinct top/bottom background zones)
- [x] Status bar (clock, battery, network icons) anchored top-left of top zone
- [x] Confirm zones render correctly on both physical screens

---

## Phase 3 — System view, top screen
*Easy. Goal: system identity visible on top screen.*

- [x] System logo centered in top zone (Y 0.0–0.5)
- [x] Game count text (e.g. `24 Games`) — system name intentionally omitted

---

## Phase 4 — System carousel, bottom screen
*Easy–medium. Goal: navigate between systems on bottom screen.*

- [x] Horizontal carousel of system logos in bottom zone (Y 0.5–1.0)
- [x] D-pad left/right navigation
- [x] Adapt coordinate pattern from `dii-ess-aye` — logic stays the same, only coords change

---

## Phase 5 — Gamelist top screen
*Medium. Goal: selected game metadata on top screen.*

- [x] System logo pinned to top of top zone
- [x] Description text in left column (Y 0.0–0.5)
- [x] Box artwork (`md_image`) in right column (Y 0.0–0.5)

---

## Phase 6 — Text list, bottom screen
*Medium. Goal: browse games on bottom screen with metadata indicators.*

- [x] Vertical text list in bottom zone (Y 0.5–1.0)
- [x] Each entry: game name left-aligned, boxart on top screen
- [x] Save state and RetroAchievements indicators handled natively by ROCKNIX

---

## Phase 7 — Keyboard and dialogs
*Skipped — see `KNOWN_ISSUES.md`.*

- [x] Keyboard is `wvkbd` (Wayland compositor) — position not theme-controllable.
      Documented as upstream-level limitation.

---

## Phase 8 — Scraper overlay
*Skipped — see `KNOWN_ISSUES.md`.*

- [x] Batch scraper notification is a hardcoded C++ GUI component positioned at the
      top-right of the 1920-wide canvas (col 3, off-screen). No `scraper` theme view
      exists in this ES build. Styling-only via menu theme elements; position not
      theme-controllable. Documented as upstream-level limitation.

---

## Phase 9 — Scripts & installation
*Requirement. Goal: permanent install via enable script in Ports.*

- [x] `scripts/enable_theme_dsi-puh-lus.sh` — searches for `dsi-puh-lus` folder,
      bind-mounts `start_es_dsi-puh-lus.sh` → `/usr/bin/start_es.sh`, writes sway config,
      sets `ThemeSet=dsi-puh-lus` / `FullScreenMenu=false` / `GameTransitionStyle=fade`,
      restarts `essway`
- [x] `scripts/start_es_dsi-puh-lus.sh` — launches ES at `--resolution 1920 480`
- [x] Test enable script, confirm ES restarts with theme

---

## Phase 10 — Polish
*Last. Goal: production-ready zip.*

- [x] Tune font sizes for 2× display stretch (all `fontSize` values land in the
      `0.029–0.032` range across the theme — verified consistent via grep)
- [x] Colors, spacing, animations (no `shadowColor`/`shadowOffset` anywhere in
      `theme-rgds.xml` — confirmed via grep; `glowColor`/`glowSize` used instead,
      which IS supported on text elements)
- [x] Package as zip, target path: `/storage/.config/emulationstation/themes/dsi-puh-lus/`
