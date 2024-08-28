from utils import download_manifest, save_file, setup_session
import json
import os
import subprocess
from multiprocessing.pool import ThreadPool

def get_valorant_version(path):
    with open(path, "rb") as exe_file:
        data = exe_file.read()
        pattern = "++Ares-Core+release-".encode("utf-16le")
        pos = data.find(pattern) + len(pattern)
        short_version = data[pos:pos+10].decode("utf-16le")
        pos += 10
        version = '\0'
        while '\0' in version:
            pos += 2
            version = data[pos:pos+32].decode("utf-16le").rstrip("\x00")
        return version

def fetch_hotfixes(region):
    releases = session.get(f"https://sieve.services.riotcdn.net/api/v1/products/valorant/version-sets/{region}", timeout=2)
    releases.raise_for_status()

    for release in releases.json()["releases"]:
        platform = release["release"]["labels"]["riot:platform"]["values"][0]
        path = f'VALORANT/{region}/{platform}'

        os.makedirs(path, exist_ok=True)
        save_file(f'{path}/{release["release"]["labels"]["buildVersion"]["values"][0]}.txt', release["download"]["url"])

session = setup_session()
pool = ThreadPool(4)

valorant_release = session.get("https://clientconfig.rpg.riotgames.com/api/v1/config/public?namespace=keystone.products.valorant.patchlines", timeout=2)

configurations = [configuration for configuration in json.loads(valorant_release.content)["keystone.products.valorant.patchlines.live"]["platforms"]["win"]["configurations"]]
os.makedirs("VALORANT/temp", exist_ok=True)
pool.starmap(download_manifest, {(configuration["patch_url"], "VALORANT/temp", session) for configuration in configurations}, 1)

region_order = {"na": 0, "br": 1, "latam": 2, "kr": 3, "ap": 4, "eu": 5} # the order they are updated in, to maximize cache efficiency when requesting files in order
for configuration in sorted(configurations, key=lambda config: region_order[config["valid_shards"]["live"][0]]):
    patch_url = configuration["patch_url"]
    region = configuration["valid_shards"]["live"][0]
    os.makedirs(f"VALORANT/{region}", exist_ok=True)
    subprocess.check_call(["./ManifestDownloader.exe", f"VALORANT/temp/{patch_url[-25:]}", "-b", "https://valorant.secure.dyn.riotcdn.net/channels/public/bundles", "-f", "ShooterGame/Binaries/Win64/VALORANT-Win64-Shipping.exe", "-o", "VALORANT/temp", "-t", "8"], timeout=60)
    exe_version = get_valorant_version("VALORANT/temp/ShooterGame/Binaries/Win64/VALORANT-Win64-Shipping.exe")

    save_file(f"VALORANT/{region}/{exe_version}.txt", patch_url)

pool.map(fetch_hotfixes, ["ap", "br", "eu", "latam", "na", "kr"], 1)
