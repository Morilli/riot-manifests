from login import get_tokens
import sys
import requests
import json
import os
from multiprocessing.pool import ThreadPool
import subprocess
import shutil

public_json = requests.get("https://clientconfig.rpg.riotgames.com/api/v1/config/public?namespace=keystone.products.bacon.patchlines", timeout=10)
public_json.raise_for_status()
version = json.loads(public_json.content)["keystone.products.bacon.patchlines.live"]["platforms"]["win"]["configurations"][0]["version"]
url = json.loads(public_json.content)["keystone.products.bacon.patchlines.live"]["platforms"]["win"]["configurations"][0]["patch_url"]
try:
    with open(f"LoR/{version}.txt", "x") as out_file:
        out_file.write(url)
except FileExistsError:
    pass

if (len(sys.argv) < 3):
    print("Error: Provide username and password in call.")
    exit(1)

subprocess.run(["./ManifestDownloader.exe", url, "-b", "https://bacon.secure.dyn.riotcdn.net/channels/public/bundles", "-f", "LoR_Data/StreamingAssets/ClientInternalConfig.json", "-o", "LoR/temp"])
with open("LoR/temp/LoR_Data/StreamingAssets/ClientInternalConfig.json", "r") as in_file:
    clienthash = json.loads(in_file.read())["clientHash"]
shutil.rmtree("LoR/temp")

regions = ["americas", "asia", "europe", "sea"]
entitlements_token, bearer = get_tokens(sys.argv[1], sys.argv[2])

def get_json(region):
    url = f"https://fe-{region}.b.pvp.net/dataservice/v1/platform/win/patchline-ref/live/client-hash/{clienthash}/client-remote-config"
    json_file = requests.get(url, headers={"X-Riot-Entitlements-JWT": entitlements_token, "Authorization": f"Bearer {bearer}"}, timeout=10)
    json_file.raise_for_status()
    version = json.loads(json_file.content)["PatchlineRefBuildId"]
    os.makedirs(f"LoR/{region}", exist_ok=True)
    try:
        with open(f"LoR/{region}/{version}.json", "xb") as out_file:
            out_file.write(json_file.content)
    except FileExistsError:
        pass

any(ThreadPool(4).imap_unordered(get_json, regions))
