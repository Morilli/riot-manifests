from login import get_lor_tokens
import sys
import requests
import json
import os
from multiprocessing.pool import ThreadPool
import subprocess
import shutil

public_json = requests.get("https://clientconfig.rpg.riotgames.com/api/v1/config/public?namespace=keystone.products.bacon.patchlines", timeout=1)
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

try:
    subprocess.run(["./ManifestDownloader.exe", url, "-b", "https://bacon.secure.dyn.riotcdn.net/channels/public/bundles", "-f", "LoR_Data/StreamingAssets/ClientInternalConfig.json", "-o", "LoR/temp"], timeout=10)
except:
    shutil.rmtree("LoR/temp")
    raise
with open("LoR/temp/LoR_Data/StreamingAssets/ClientInternalConfig.json", "r") as in_file:
    clienthash = json.loads(in_file.read())["clientHash"]
shutil.rmtree("LoR/temp")

regions = ["europe"] #["americas", "asia", "europe", "sea"]
entitlements_token, access_token, id_token, userinfo, pas = get_lor_tokens(sys.argv[1], sys.argv[2])

def get_json(region):
    login_payload = {"RsoEntitlementsToken": entitlements_token, "RsoIdToken": id_token, "RsoUserinfoToken": userinfo, "PasToken": pas}
    login_response = requests.post(f"https://l-{region}.b.pvp.net/login/v1/session", headers={"X-Rso-Auth": access_token}, json=login_payload, timeout=1)
    login_response.raise_for_status()

    new_access_token = json.loads(login_response.content)["AccessToken"]
    json_file = requests.get(f"https://fe-{region}.b.pvp.net/dataservice/v1/platform/win/patchline-ref/live/client-hash/{clienthash}/client-remote-config", headers={"Authorization": f"Bearer {new_access_token}"}, timeout=1)
    json_file.raise_for_status()
    version = json.loads(json_file.content)["PatchlineRefBuildId"]
    os.makedirs(f"LoR/{region}", exist_ok=True)
    try:
        with open(f"LoR/{region}/{version}.json", "xb") as out_file:
            out_file.write(json_file.content)
    except FileExistsError:
        pass

any(ThreadPool(1).imap_unordered(get_json, regions))
