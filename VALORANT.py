from utils import download_manifest, save_file
import requests
import json
import os
import subprocess
import shutil
from multiprocessing.pool import ThreadPool

def get_valorant_version(path):
    with open(path, "rb") as exe_file:
        data = exe_file.read()
        pattern = "++Ares-Core+release-".encode("utf-16le")
        pos = data.find(pattern) + len(pattern) + 48
        return data[pos:pos+32].decode("utf-16le").rstrip("\x00")

valorant_release = requests.get("https://clientconfig.rpg.riotgames.com/api/v1/config/public?namespace=keystone.products.valorant.patchlines", timeout=1)

configurations = [configuration for configuration in json.loads(valorant_release.content)["keystone.products.valorant.patchlines.live"]["platforms"]["win"]["configurations"]]
os.makedirs("VALORANT/temp", exist_ok=True)
ThreadPool(4).starmap(download_manifest, {(configuration["patch_url"], "VALORANT/temp") for configuration in configurations}, 1)

region_order = {"na": 0, "br": 1, "latam": 2, "kr": 3, "ap": 4, "eu": 5} # the order they are updated in, to maximize cache efficiency when requesting files in order
for configuration in sorted(configurations, key=lambda config: region_order[config["valid_shards"]["live"][0]]):
    patch_url = configuration["patch_url"]
    region = configuration["valid_shards"]["live"][0]
    os.makedirs(f"VALORANT/{region}", exist_ok=True)
    try:
        subprocess.check_call(["./ManifestDownloader.exe", f"VALORANT/temp/{patch_url[-25:]}", "-b", "https://valorant.secure.dyn.riotcdn.net/channels/public/bundles", "-f", "ShooterGame/Binaries/Win64/VALORANT-Win64-Shipping.exe", "-o", "VALORANT/temp", "-t", "8"], timeout=60)
    except:
        shutil.rmtree("VALORANT/temp")
        raise
    exe_version = get_valorant_version("VALORANT/temp/ShooterGame/Binaries/Win64/VALORANT-Win64-Shipping.exe")

    save_file(f"VALORANT/{region}/{exe_version}.txt", patch_url)

shutil.rmtree("VALORANT/temp")
