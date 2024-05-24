from utils import get_exe_version, save_file, setup_session
import json
import os
import subprocess
import plistlib

patchlines = ["KeystoneFoundationLiveWin", "KeystoneFoundationBetaWin", "KeystoneFoundationLiveMac", "KeystoneFoundationBetaMac"]
session = setup_session()

for patchline in patchlines:
    json_file = session.get(f"https://clientconfig.rpg.riotgames.com/api/v1/config/public?version=99.0.0.9999999&patchline={patchline}&app=Riot Client&namespace=keystone.self_update", timeout=2)
    json_file.raise_for_status()

    level = json.loads(json_file.content)["keystone.self_update.level"]
    manifest_url = json.loads(json_file.content)["keystone.self_update.manifest_url"]
    os.makedirs(f"Riot Client/{patchline}", exist_ok=True)
    download_info = ("^Contents/Info.plist", "mac") if "Mac" in patchline else ("RiotClientFoundation.dll", "win")
    subprocess.check_call(["./ManifestDownloader.exe", manifest_url, "-b", "https://ks-foundation.secure.dyn.riotcdn.net/channels/public/bundles", "-f", download_info[0], "-o", "Riot Client/temp", "-t", "8"], timeout=10)
    if download_info[1] == "win":
        exe_version = get_exe_version(f"Riot Client/temp/{download_info[0]}")
    else:
        with open(f"Riot Client/temp/{download_info[0][1:]}", "rb") as in_file:
            exe_version = f'{plistlib.load(in_file)["FileVersion"]}_{manifest_url[-25:-9]}'
    save_file(f"Riot Client/{patchline}/{exe_version}_{level}.json", json_file.content)
