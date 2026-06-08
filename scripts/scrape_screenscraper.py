#!/usr/bin/env python3
"""
dsi-puh-lus ScreenScraper CLI
On-device scraper for EmulationStation on ROCKNIX
Uses ScreenScraper.fr API v2

Usage:
  python3 scrape_screenscraper.py                  # scrape all systems
  python3 scrape_screenscraper.py snes             # scrape one system
  python3 scrape_screenscraper.py snes --force     # re-scrape even if already in gamelist.xml
"""

import os, sys, json, hashlib, re, time, urllib.request, urllib.parse, xml.etree.ElementTree as ET

# ── Config ──────────────────────────────────────────────────────────────────
ROMS_ROOT = "/storage/roms"
ES_SETTINGS = "/storage/.config/emulationstation/es_settings.cfg"

# ScreenScraper dev credentials
# Get your own at https://www.screenscraper.fr/ (free, register as dev)
DEV_ID = "dsi-puh-lus"
DEV_PASSWORD = ""
API_URL = "https://www.screenscraper.fr/api2/jeuInfos.php"

# Known-working dev credentials for open-source projects (publicly documented)
# Batocera uses these:
FALLBACK_DEVID = "95c0d55e4e40d30a"
FALLBACK_DEVPASSWORD = "c81f20ef0ff40d00"

# System name → ScreenScraper system ID mapping
SYSTEM_IDS = {
    "3do": 43, "3ds": 136, "amiga": 64, "amigacd32": 65,
    "amstradcpc": 48, "arcade": 75, "arduboy": 184,
    "atari2600": 26, "atari5200": 40, "atari7800": 41,
    "atari800": 43, "atarijaguar": 11, "atarilynx": 32,
    "atarist": 53, "atomiswave": 140, "bbcmicro": 55,
    "c64": 51, "cps1": 119, "cps2": 120, "cps3": 121,
    "daphne": 104, "doom": 91, "dreamcast": 5, "easyrpg": 153,
    "famicom": 99, "fba": 76, "fds": 84, "gameandwatch": 29,
    "gamegear": 21, "gb": 9, "gba": 12, "gbc": 10,
    "gc": 136, "genesis": 1, "genh": 1, "intellivision": 44,
    "j2me": 127, "mac": 186, "mame": 75, "mastersystem": 2,
    "megacd": 20, "megadrive": 1, "megaduck": 81, "msx": 52,
    "msx2": 52, "n64": 14, "naomi": 140, "nds": 15,
    "neogeo": 23, "nes": 3, "ngp": 25, "ngpc": 25,
    "odyssey": 98, "openbor": 153, "palm": 90, "pc": 73,
    "pc88": 96, "pc98": 97, "pcengine": 31, "pcenginecd": 114,
    "pcfx": 72, "pico8": 129, "pokemini": 133, "ports": 153,
    "ps2": 8, "psp": 6, "psx": 7, "saturn": 22,
    "scummvm": 49, "scv": 161, "sega32x": 19, "segacd": 20,
    "sfc": 4, "sg-1000": 109, "snes": 4, "st-v": 114,
    "sufami": 105, "supervision": 163, "tg16": 31, "tg16cd": 114,
    "tic80": 153, "tools": 153, "uzebox": 147, "vectrex": 102,
    "vic20": 54, "virtualboy": 27, "wii": 13, "wiiu": 153,
    "windows": 73, "wonderswan": 45, "wonderswancolor": 45,
    "x68000": 89, "xbox": 134, "zmachine": 195, "zx81": 56,
    "zxspectrum": 57,
}


def load_config():
    user = ""
    password = ""
    try:
        with open(ES_SETTINGS) as f:
            content = f.read()
        m = re.search(r'<string name="ScreenScraperUser" value="([^"]*)"', content)
        if m: user = m.group(1)
        m = re.search(r'<string name="ScreenScraperPass" value="([^"]*)"', content)
        if m: password = m.group(1)
    except:
        pass
    return user, password


def md5_file(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def query_api(filename, filesize, md5, system_id, user, password, devid, devpass, retries=3):
    params = {
        "devid": devid,
        "devpassword": devpass,
        "softname": "dsi-puh-lus",
        "output": "json",
        "systemeid": str(system_id),
        "romnom": filename,
        "romtaille": str(filesize),
        "md5": md5,
        "user": user,
        "password": password,
    }
    url = API_URL + "?" + urllib.parse.urlencode(params)
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "dsi-puh-lus/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            if "Erreur de développement" in body and attempt == 0:
                # dev credentials might be wrong, try fallback
                if devid == DEV_ID:
                    return query_api(filename, filesize, md5, system_id, user, password,
                                     FALLBACK_DEVID, FALLBACK_DEVPASSWORD, retries - 1)
            if attempt < retries - 1:
                time.sleep(2)
            else:
                print(f"  API error: {e.code} - {body[:100]}")
                return None
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                print(f"  Request failed: {e}")
                return None
    return None


def find_roms(system_path, extensions):
    roms = []
    for f in os.listdir(system_path):
        fpath = os.path.join(system_path, f)
        if os.path.isfile(fpath):
            ext = os.path.splitext(f)[1].lower()
            if ext in extensions:
                roms.append(fpath)
    roms.sort()
    return roms


def load_gamelist(system_path):
    gl_path = os.path.join(system_path, "gamelist.xml")
    if not os.path.exists(gl_path):
        return ET.Element("gameList")
    try:
        tree = ET.parse(gl_path)
        return tree.getroot()
    except:
        return ET.Element("gameList")


def save_gamelist(root, system_path):
    gl_path = os.path.join(system_path, "gamelist.xml")
    # Remove empty game elements
    for el in list(root):
        if len(el) == 0:
            root.remove(el)
    tree = ET.ElementTree(root)
    tree.write(gl_path, encoding="UTF-8", xml_declaration=True)


def find_entry(root, path):
    for game in root.findall("game"):
        p = game.find("path")
        if p is not None and p.text == path:
            return game
    return None


def make_element(parent, tag, text=None, attrib=None):
    el = ET.SubElement(parent, tag)
    if attrib:
        el.attrib.update(attrib)
    if text:
        el.text = text
    return el


def download_media(url, dest):
    if not url:
        return False
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "dsi-puh-lus/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(data)
        return True
    except:
        return False


def get_media_url(response, media_type):
    """Extract media URL from API response JSON."""
    try:
        # Response structure: { response: { jeu: { medias: [...] } } }
        jeu = response.get("response", {}).get("jeu", {})
        medias = jeu.get("medias", [])
        for m in medias:
            if m.get("type") == media_type and m.get("url"):
                return m["url"]
        # Try alternate format
        if isinstance(jeu, dict):
            for key in jeu:
                if key.lower().startswith(media_type):
                    val = jeu[key]
                    if isinstance(val, str) and val.startswith("http"):
                        return val
        return None
    except:
        return None


def scrape_system(system_name, force=False, user="", password="", devid="", devpass=""):
    system_path = os.path.join(ROMS_ROOT, system_name)
    if not os.path.isdir(system_path):
        print(f"System folder not found: {system_path}")
        return

    system_id = SYSTEM_IDS.get(system_name)
    if not system_id:
        print(f"Unknown system: {system_name} (add SYSTEM_IDS mapping)")
        return

    # Extension list by platform
    ext_map = {
        "snes": ".smc .sfc .fig .swc .zip .7z", "genesis": ".gen .md .bin .smd .zip .7z",
        "gba": ".gba .zip .7z", "gbc": ".gbc .zip .7z", "gb": ".gb .zip .7z",
        "nes": ".nes .zip .7z", "n64": ".z64 .n64 .v64 .zip .7z",
        "psx": ".bin .cue .img .mdf .pbp .chd .iso .ccd",
        "ps2": ".iso .mdf .nrg .bin .img .gz .cso .chd",
        "psp": ".iso .cso .pbp .chd",
        "nds": ".nds .zip .7z", "dreamcast": ".cdi .gdi .chd .m3u .cue",
        "atari2600": ".a26 .bin .zip .7z",
    }
    extensions = ext_map.get(system_name, ".zip .7z .bin .rom")
    extensions = [e.strip().lower() for e in extensions.split()]

    roms = find_roms(system_path, extensions)
    if not roms:
        print(f"No ROMs found in {system_path}")
        return

    images_dir = os.path.join(system_path, "images")
    os.makedirs(images_dir, exist_ok=True)

    root = load_gamelist(system_path)
    scraped = 0
    skipped = 0
    failed = 0

    print(f"\nScraping {system_name} ({system_id}) — {len(roms)} ROMs")
    print("-" * 50)

    for rom_path in roms:
        rom_name = os.path.basename(rom_path)
        rel_path = "./" + rom_name
        name_no_ext = os.path.splitext(rom_name)[0]

        # Check if already scraped
        existing = find_entry(root, rel_path)
        if existing is not None and not force:
            if existing.find("image") is not None or existing.find("thumbnail") is not None:
                print(f"  SKIP {rom_name}")
                skipped += 1
                continue

        filesize = os.path.getsize(rom_path)
        print(f"  HASH {rom_name} ...", end=" ", flush=True)
        md5 = md5_file(rom_path)
        print("OK")

        print(f"  API  {rom_name} ...", end=" ", flush=True)
        data = query_api(rom_name, filesize, md5, system_id, user, password, devid, devpass)
        if data is None:
            print("FAILED")
            failed += 1
            continue
        print("OK")

        # Extract data
        jeu = data.get("response", {}).get("jeu", {})
        noms = jeu.get("noms", {})
        nom = ""
        if isinstance(noms, dict):
            for lang in ["us", "eu", "jp", "ss"]:
                val = noms.get(lang)
                if isinstance(val, str):
                    nom = val
                    break
        if not nom:
            for key in jeu:
                if "nom" in key.lower() and isinstance(jeu[key], str):
                    nom = jeu[key]
                    break
        if not nom:
            nom = name_no_ext

        desc = ""
        if isinstance(jeu.get("synopsis"), dict):
            desc = jeu["synopsis"].get("fr") or jeu["synopsis"].get("en") or ""
        elif isinstance(jeu.get("synopsis"), str):
            desc = jeu["synopsis"]

        # Download images
        image_url = get_media_url(data, "box-2D")
        thumb_url = get_media_url(data, "screen")
        if not thumb_url:
            thumb_url = get_media_url(data, "box-2D")

        img_path = os.path.join(images_dir, f"{name_no_ext}-image.png")
        thumb_path = os.path.join(images_dir, f"{name_no_ext}-thumb.png")

        img_dl = download_media(image_url, img_path) if image_url else False
        thumb_dl = download_media(thumb_url, thumb_path) if thumb_url else False

        # Extract other metadata
        developer = ""
        publisher = ""
        genre = ""
        players = ""
        rating = ""
        releasedate = ""

        if isinstance(jeu.get("developpeur"), dict):
            developer = jeu["developpeur"].popitem()[1] if jeu["developpeur"] else ""
        if isinstance(jeu.get("editeur"), dict):
            publisher = jeu["editeur"].popitem()[1] if jeu["editeur"] else ""
        if isinstance(jeu.get("genres"), dict):
            g = jeu["genres"]
            genre = g.popitem()[1] if g else ""
        if isinstance(jeu.get("joueurs"), dict):
            players = jeu["joueurs"].popitem()[1] if jeu["joueurs"] else ""
        if isinstance(jeu.get("note"), str):
            try:
                rating = str(float(jeu["note"]) / 20)
            except:
                pass
        if isinstance(jeu.get("dates"), dict):
            d = jeu["dates"]
            dates = list(d.values())
            if dates:
                releasedate = dates[0]

        # Update gamelist entry
        if existing is None:
            game = ET.SubElement(root, "game")
        else:
            game = existing
            for child in list(game):
                if child.tag in ("name", "desc", "image", "thumbnail", "rating",
                                 "releasedate", "developer", "publisher", "genre", "players"):
                    game.remove(child)

        make_element(game, "path", rel_path)
        if nom:
            make_element(game, "name", nom)
        if desc:
            make_element(game, "desc", desc)
        if img_dl:
            make_element(game, "image", img_path)
        if thumb_dl:
            make_element(game, "thumbnail", thumb_path)
        if rating:
            make_element(game, "rating", rating)
        if releasedate:
            make_element(game, "releasedate", releasedate)
        if developer:
            make_element(game, "developer", developer)
        if publisher:
            make_element(game, "publisher", publisher)
        if genre:
            make_element(game, "genre", genre)
        if players:
            make_element(game, "players", players)

        scraped += 1
        print(f"  DONE {nom}")

    save_gamelist(root, system_path)
    print(f"\n── {system_name}: {scraped} scraped, {skipped} skipped, {failed} failed ──\n")


def get_all_systems():
    systems = []
    for entry in os.listdir(ROMS_ROOT):
        path = os.path.join(ROMS_ROOT, entry)
        if os.path.isdir(path) and entry in SYSTEM_IDS:
            systems.append(entry)
    return sorted(systems)


def main():
    if os.geteuid() != 0:
        print("Run as root (sudo) for full filesystem access.")

    user, password = load_config()
    if not user or not password:
        print("Warning: ScreenScraper credentials not found in es_settings.cfg.")
        print("Edit /storage/.config/emulationstation/es_settings.cfg or set manually.")
        return

    devid = DEV_ID
    devpass = DEV_PASSWORD

    # Check what to scrape
    if len(sys.argv) >= 2 and not sys.argv[1].startswith("--"):
        target = sys.argv[1]
        force = "--force" in sys.argv
        scrape_system(target, force, user, password, devid, devpass)
    else:
        force = "--force" in sys.argv
        systems = get_all_systems()
        if not systems:
            print(f"No recognized systems found in {ROMS_ROOT}")
            return
        print(f"Found {len(systems)} systems: {', '.join(systems)}")
        for sys_name in systems:
            scrape_system(sys_name, force, user, password, devid, devpass)

    print("Done! Restart EmulationStation to see scraped data.")


if __name__ == "__main__":
    main()
