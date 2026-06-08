#!/usr/bin/env python3
"""
Deploy theme files to the RG DS over SSH and verify the result.

  python deploy.py theme-rgds.xml assets/images/common/selector_glow_gold.png
  python deploy.py --logos                  # push all systems/*.png
  python deploy.py --shot                   # just grab a screenshot to _device_shot.png
  python deploy.py <files...> --shot        # push, restart ES, screenshot

Device: root@<IP> / rocknix (set DSI_HOST env to override IP).
Restart with `systemctl restart essway` and confirm the emulationstation PID changed
(ES caches textures in memory -- a file copy alone does NOT update the screen).
Requires: paramiko
"""
import paramiko, sys, os, time, io

HOST=os.environ.get("DSI_HOST","10.185.79.35"); USER="root"; PW="rocknix"
ROOT=os.path.join(os.path.dirname(__file__),"..")
REMOTE="/storage/.config/emulationstation/themes/dsi-puh-lus"
# grim needs sway's wayland env; these values are what work on this build:
GRIM="XDG_RUNTIME_DIR=/run/0-runtime-dir WAYLAND_DISPLAY=wayland-1 grim /tmp/shot.png"

args=[a for a in sys.argv[1:]]
do_shot="--shot" in args;  do_logos="--logos" in args
files=[a for a in args if not a.startswith("--")]

ssh=paramiko.SSHClient(); ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST,username=USER,password=PW,timeout=40,banner_timeout=40,auth_timeout=40)
run=lambda c:(lambda o,e:(o.read()+e.read()).decode('utf-8','replace').strip())(
    *ssh.exec_command(c)[1:3])

if do_logos:
    d=os.path.join(ROOT,"assets","images","systems")
    files+= [f"assets/images/systems/{f}" for f in os.listdir(d)
             if f.lower().endswith(".png") and not f.startswith("._")]

if files:
    old=run("pgrep emulationstation")
    sftp=ssh.open_sftp()
    for rel in files:
        sftp.put(os.path.join(ROOT,rel.replace("/",os.sep)), f"{REMOTE}/{rel}")
        print("pushed", rel)
    sftp.close()
    run("systemctl restart essway"); time.sleep(10)
    new=run("pgrep emulationstation")
    print(f"ES {old} -> {new}", "RESTARTED" if new and new!=old else "WARN: pid unchanged")

if do_shot or files:
    print(run(GRIM+"; echo grim=$?"))
    sftp=ssh.open_sftp()
    sftp.get("/tmp/shot.png", os.path.join(ROOT,"assets","images","common","_device_shot.png"))
    sftp.close()
    print("screenshot -> assets/images/common/_device_shot.png "
          "(carousel is at capture x~960,y~298 on the 1280x480 grab)")
ssh.close()
