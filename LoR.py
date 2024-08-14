from utils import get_lor_tokens, save_file, setup_session
import sys
import json
import os
from multiprocessing.pool import ThreadPool
import subprocess

session = setup_session()
public_json = session.get("https://clientconfig.rpg.riotgames.com/api/v1/config/public?namespace=keystone.products.bacon.patchlines", timeout=2)
public_json.raise_for_status()
version = public_json.json()["keystone.products.bacon.patchlines.live"]["platforms"]["win"]["configurations"][0]["version"]
url = public_json.json()["keystone.products.bacon.patchlines.live"]["platforms"]["win"]["configurations"][0]["patch_url"]
save_file(f"LoR/{version}.txt", url)

if (len(sys.argv) < 3):
    print("Error: Provide username and password in call.")
    exit(1)

subprocess.check_call(["./ManifestDownloader.exe", url, "-b", "https://bacon.secure.dyn.riotcdn.net/channels/public/bundles", "-f", "LoR_Data/StreamingAssets/ClientInternalConfig.json", "-o", "LoR/temp"], timeout=10)
with open("LoR/temp/LoR_Data/StreamingAssets/ClientInternalConfig.json", "r") as in_file:
    clienthash = json.load(in_file)["clientHash"]

regions = ["europe"] #["americas", "asia", "europe", "sea"]
entitlements_token, access_token, id_token, userinfo, pas = get_lor_tokens(sys.argv[1], sys.argv[2], session)

def get_json(region):
    login_payload = {"RsoEntitlementsToken": entitlements_token, "RsoIdToken": id_token, "RsoUserinfoToken": userinfo, "PasToken": pas, "ClientPatchline": "live"}
    login_response = session.post(f"https://l-{region}-green.b.pvp.net/login/v1/session", headers={"X-Rso-Auth": access_token}, json=login_payload)
    login_response.raise_for_status()

    new_access_token = login_response.json()["AccessToken"]
    json_file = session.get(f"https://fe-{region}-green.b.pvp.net/dataservice/v1/platform/win/patchline-ref/live/client-hash/{clienthash}/client-remote-config", headers={"Authorization": f"Bearer {new_access_token}"}, timeout=1)
    json_file.raise_for_status()
    version = json_file.json()["PatchlineRefBuildId"]
    os.makedirs(f"LoR/{region}", exist_ok=True)
    save_file(f"LoR/{region}/{version}.json", json_file.content)

ThreadPool(1).map(get_json, regions, 1)
