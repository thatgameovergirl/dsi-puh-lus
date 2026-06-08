#!/bin/bash

THEME_PATH=""
if [ -d "/roms/themes/dsi-puh-lus" ]; then
    THEME_PATH="/roms/themes/dsi-puh-lus"
elif [ -d "/roms/themes/dsi-puh-lus-main" ]; then
    THEME_PATH="/roms/themes/dsi-puh-lus-main"
elif [ -d "/storage/.config/emulationstation/themes/dsi-puh-lus" ]; then
    THEME_PATH="/storage/.config/emulationstation/themes/dsi-puh-lus"
elif [ -d "/storage/.config/emulationstation/themes/dsi-puh-lus-main" ]; then
    THEME_PATH="/storage/.config/emulationstation/themes/dsi-puh-lus-main"
else
    echo "ERROR! Couldn't find dsi-puh-lus theme folder on your device!"
    exit 1
fi

chmod +x "${THEME_PATH}/scripts/start_es_dsi-puh-lus.sh"
# Drop any existing bind mounts first so repeated runs don't stack (we saw 1024 stacked).
while mountpoint -q /usr/bin/start_es.sh; do umount /usr/bin/start_es.sh || break; done
mount --bind "${THEME_PATH}/scripts/start_es_dsi-puh-lus.sh" "/usr/bin/start_es.sh"

cat <<EOF >/storage/.config/sway/config
seat * hide_cursor 1000
default_border none
exec_always mako
output DSI-2 transform 0
output DSI-2 bg #000000 solid_color
output DSI-2 allow_tearing yes
output DSI-2 max_render_time off
for_window [title=".*(Secondary|\[w2\]|Sub|Bottom|Screen 2|GamePad).*"] move window to output DSI-1
for_window [title="RetroArch\s(melonDS|DeSmuME|VecX|MAME|FinalBurn|FB Alpha).*"] exec /usr/bin/vertical-check
for_window [app_id="drastic"] input "1046:911:Goodix_Capacitive_TouchScreen" map_to_output DSI-2
for_window [app_id="emulationstation"] reload
exec_always swaymsg '[app_id="emulationstation"]' floating enable, fullscreen disable, move absolute position 0 0
exec_always swaymsg '[app_id="emulationstation"]' focus
EOF

swaymsg reload

ES_SETTINGS="/storage/.config/emulationstation/es_settings.cfg"
if grep -q '<string name="FullScreenMenu"' "$ES_SETTINGS" 2>/dev/null; then
    sed -i 's|<string name="FullScreenMenu" value="[^"]*" />|<string name="FullScreenMenu" value="false" />|' "$ES_SETTINGS"
else
    sed -i 's|</config>|\t<string name="FullScreenMenu" value="false" />\n</config>|' "$ES_SETTINGS"
fi

if grep -q '<string name="GameTransitionStyle"' "$ES_SETTINGS" 2>/dev/null; then
    sed -i 's|<string name="GameTransitionStyle" value="[^"]*" />|<string name="GameTransitionStyle" value="fade" />|' "$ES_SETTINGS"
else
    sed -i 's|</config>|\t<string name="GameTransitionStyle" value="fade" />\n</config>|' "$ES_SETTINGS"
fi

if grep -q '<string name="ThemeSet"' "$ES_SETTINGS" 2>/dev/null; then
    sed -i 's|<string name="ThemeSet" value="[^"]*" />|<string name="ThemeSet" value="dsi-puh-lus" />|' "$ES_SETTINGS"
else
    sed -i 's|</config>|\t<string name="ThemeSet" value="dsi-puh-lus" />\n</config>|' "$ES_SETTINGS"
fi

systemctl restart essway
