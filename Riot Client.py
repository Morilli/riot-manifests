import requests
import json
import os
from multiprocessing.pool import ThreadPool

patchlines = ["KeystoneFoundationLiveWin", "KeystoneFoundationBetaWin"]

def download_jsons(patchline):
    url = f"https://clientconfig.rpg.riotgames.com/api/v1/config/public?version=99.0.0.9999999&patchline={patchline}&app=Riot Client&namespace=keystone.self_update"
    json_file = requests.get(url)
    json_file.raise_for_status()

    level = json.loads(json_file.content)["keystone.self_update.level"]
    manifest_url = json.loads(json_file.content)["keystone.self_update.manifest_url"][-25:-9]
    os.makedirs(f"Riot Client/{patchline}", exist_ok=True)
    try:
        with open(f"Riot Client/{patchline}/{manifest_url}_{level}.json", "xb") as out_file:
            out_file.write(json_file.content)
    except FileExistsError:
        pass

any(ThreadPool(2).imap_unordered(download_jsons, patchlines))
