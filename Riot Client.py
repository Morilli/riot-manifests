from utils import get_exe_version
import requests
import json
import os
import subprocess
import shutil

patchlines = ["KeystoneFoundationLiveWin", "KeystoneFoundationBetaWin"]

for patchline in patchlines:
    json_file = requests.get(f"https://clientconfig.rpg.riotgames.com/api/v1/config/public?version=99.0.0.9999999&patchline={patchline}&app=Riot Client&namespace=keystone.self_update", timeout=1)
    json_file.raise_for_status()

    level = json.loads(json_file.content)["keystone.self_update.level"]
    manifest_url = json.loads(json_file.content)["keystone.self_update.manifest_url"]
    os.makedirs(f"Riot Client/{patchline}", exist_ok=True)
    try:
        subprocess.check_call(["./ManifestDownloader.exe", manifest_url, "-b", "https://ks-foundation.secure.dyn.riotcdn.net/channels/public/bundles", "-f", "RiotClientServices.exe", "-o", "Riot Client/temp", "-t", "8"], timeout=20)
    except:
        shutil.rmtree("Riot Client/temp")
        raise
    exe_version = get_exe_version("Riot Client/temp/RiotClientServices.exe")
    try:
        with open(f"Riot Client/{patchline}/{exe_version}_{level}.json", "xb") as out_file:
            out_file.write(json_file.content)
    except FileExistsError:
        pass

shutil.rmtree("Riot Client/temp")
