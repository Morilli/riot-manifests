import requests
import json
import os

valorant_release = requests.get("https://clientconfig.rpg.riotgames.com/api/v1/config/public?namespace=keystone.products.valorant.patchlines", timeout=10)

for configuration in json.loads(valorant_release.content)["keystone.products.valorant.patchlines.live"]["platforms"]["win"]["configurations"]:
    patch_url = configuration["patch_url"]
    id = patch_url[-25:-9]
    region = configuration["valid_shards"]["live"][0]
    os.makedirs(f"VALORANT/{region}", exist_ok=True)
    try:
        with open(f"VALORANT/{region}/{id}.txt", "x") as out_file:
            out_file.write(patch_url)
    except FileExistsError:
        pass
