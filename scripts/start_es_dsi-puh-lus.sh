#!/bin/bash
# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2024 ROCKNIX (https://github.com/ROCKNIX)

### setup is the same
. $(dirname $0)/es_settings

# Themed loading screen. ES draws this image during startup plus its own
# "Loading..." text + progress bar. The old --no-splash gave a black screen
# with only a bare red bar.
SPLASH="/storage/.config/emulationstation/themes/dsi-puh-lus/assets/images/common/splash.png"
[ -f "$SPLASH" ] || SPLASH="/roms/themes/dsi-puh-lus/assets/images/common/splash.png"

emulationstation --log-path /var/log --splash-image "$SPLASH" --resolution 1920 480
