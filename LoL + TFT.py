from requests import Session
from utils import get_exe_version, download_manifest, save_file
import json
import plistlib
import os
from multiprocessing.pool import ThreadPool
import subprocess
import shutil

version_sets = ["BR1", "EUN1", "EUW1", "JP1", "KR", "LA1", "LA2", "NA1", "OC1", "PBE1", "RU", "STAGING", "TR1"]
session = Session()
pool = ThreadPool(8)

def update_versions(region):
    for OS in ["android", "ios", "macos", "windows"]:
        releases = session.get(f"https://sieve.services.riotcdn.net/api/v1/products/lol/version-sets/{region}?q[platform]={OS}", timeout=1)
        releases.raise_for_status()

        for release in json.loads(releases.content)["releases"]:
            path = f'{"LoL" if OS == "macos" or OS == "windows" else "TFT"}/{region}/{OS}/{release["release"]["labels"]["riot:artifact_type_id"]["values"][0]}'
            os.makedirs(path, exist_ok=True)
            save_file(f'{path}/{release["release"]["labels"]["riot:artifact_version_id"]["values"][0].split("+")[0]}.txt', release["download"]["url"])

pool.map(update_versions, version_sets, 1)

region_map = {"BR": "BR1", "EUNE": "EUN1", "EUW": "EUW1", "JP": "JP1", "KR": "KR", "LA1": "LA1", "LA2": "LA2", "NA": "NA1", "OC1": "OC1", "RU": "RU", "TR": "TR1", "PBE": "PBE1"}
os_map = {"win": "windows", "mac": "macos"}

client_releases = session.get("https://clientconfig.rpg.riotgames.com/api/v1/config/public?namespace=keystone.products.league_of_legends.patchlines", timeout=1)
client_releases.raise_for_status()

configurations = []
for patchline in json.loads(client_releases.content).values():
    for platform in patchline["platforms"]:
        for configuration in patchline["platforms"][platform]["configurations"]:
            configurations.append((region_map[configuration["id"]], platform, configuration["patch_url"]))

versions = []
os.makedirs("LoL/temp", exist_ok=True)
pool.starmap(download_manifest, {(configuration[2], "LoL/temp", session) for configuration in configurations}, 1)

for configuration in configurations:
    try:
        if configuration[1] == "mac":
            subprocess.check_call(["./ManifestDownloader.exe", f"LoL/temp/{configuration[2][-25:]}", "-f", "Contents/LoL/LeagueClient.app/Contents/Info.plist", "-o", "LoL/temp"], timeout=5)
            with open("LoL/temp/Contents/LoL/LeagueClient.app/Contents/Info.plist", "rb") as in_file:
                exe_version = f'{plistlib.load(in_file)["FileVersion"]}_{configuration[2][-25:-9]}'
        else: # windows
            subprocess.check_call(["./ManifestDownloader.exe", f"LoL/temp/{configuration[2][-25:]}", "-f", "LeagueClient.exe", "-o", "LoL/temp", "-t", "4"], timeout=10)
            exe_version = get_exe_version("LoL/temp/LeagueClient.exe")
    except:
        shutil.rmtree("LoL/temp")
        raise
    versions.append((configuration[0], os_map[configuration[1]], exe_version, configuration[2]))

shutil.rmtree("LoL/temp")

for version in versions:
    path = f"LoL/{version[0]}/{version[1]}/league-client"
    os.makedirs(path, exist_ok=True)
    save_file(f"{path}/{version[2]}.txt", version[3])
