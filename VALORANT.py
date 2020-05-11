from login import get_tokens
import sys
import requests
import json
import os

if (len(sys.argv) < 3):
    print("Error: Provide username and password in call.")
    exit(1)

entitlements_token, bearer = get_tokens(sys.argv[1], sys.argv[2])

player_json = requests.get("https://clientconfig.rpg.riotgames.com/api/v1/config/player?os=windows&region=EUW&app=Riot%20Client&version=99.0.0.9999999&patchline=KeystoneFoundationLiveWin", headers={"X-Riot-Entitlements-JWT": entitlements_token, "Authorization": f"Bearer {bearer}"})

for configuration in json.loads(player_json.content)["keystone.products.valorant.patchlines.live"]["platforms"]["win"]["configurations"]:
    patch_url = configuration["patch_url"]
    id = patch_url[-25:-9]
    region = configuration["valid_shards"]["live"][0]
    os.makedirs(f"VALORANT/{region}", exist_ok=True)
    try:
        with open(f"VALORANT/{region}/{id}.txt", "x") as out_file:
            out_file.write(patch_url)
    except FileExistsError:
        pass
