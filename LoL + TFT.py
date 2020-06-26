import requests
import json
import os
from multiprocessing.pool import ThreadPool
import hachoir.parser
import hachoir.metadata
from hachoir.stream import FileInputStream
import subprocess
import shutil
import re

version_sets = ["BR1", "EUN1", "EUW1", "JP1", "KR", "LA1", "LA2", "NA1", "OC1", "PBE1", "RU", "TR1"]

def update_versions(region):
    for OS in ["android", "ios", "macos", "windows"]:
        releases = requests.get(f"https://sieve.services.riotcdn.net/api/v1/products/lol/version-sets/{region}?q[platform]={OS}", timeout=1)
        releases.raise_for_status()

        for release in json.loads(releases.content)["releases"]:
            path = f'{"LoL" if OS == "macos" or OS == "windows" else "TFT"}/{region}/{OS}/{release["release"]["labels"]["riot:artifact_type_id"]["values"][0]}'
            os.makedirs(path, exist_ok=True)
            try:
                with open(f'{path}/{release["release"]["labels"]["riot:artifact_version_id"]["values"][0].split("+")[0]}.txt', "x") as out_file:
                    out_file.write(release["download"]["url"])
            except FileExistsError:
                pass

any(ThreadPool(4).imap_unordered(update_versions, version_sets))

def get_exe_version(path):
    stream = FileInputStream(path)
    parser = hachoir.parser.guessParser(stream)
    metadata = hachoir.metadata.extractMetadata(parser)
    version = metadata.get("version")
    stream.close()
    return version

region_map = {"BR": "BR1", "EUNE": "EUN1", "EUW": "EUW1", "JP": "JP1", "KR": "KR", "LA1": "LA1", "LA2": "LA2", "NA": "NA1", "OC1": "OC1", "RU": "RU", "TR": "TR1", "PBE": "PBE1"}

client_releases = requests.get("https://clientconfig.rpg.riotgames.com/api/v1/config/public?namespace=keystone.products.league_of_legends.patchlines", timeout=1)
client_releases.raise_for_status()

configurations = []
versions = []
for patchline in json.loads(client_releases.content).values():
    for platform in ["win", "mac"]:
        for configuration in patchline["platforms"][platform]["configurations"]:
            if platform == "mac":
                versions.append((region_map[configuration["id"]], "macos", re.search("theme/(.*?)/", configuration["metadata"]["theme_manifest"]).group(1) + f"_{configuration['patch_url'][-25:-9]}", configuration["patch_url"]))
            else:
                configurations.append((region_map[configuration["id"]], configuration["patch_url"]))

urls = {configuration[1] for configuration in configurations}
for url in urls:
    try:
        subprocess.check_call(["./ManifestDownloader.exe", url, "-f", "LeagueClient.exe", "-o", "LoL/temp", "-t", "4"], timeout=20)
    except:
        shutil.rmtree("LoL/temp")
        raise
    exe_version = get_exe_version("LoL/temp/LeagueClient.exe")
    for configuration in configurations:
        if configuration[1] == url:
            versions.append((configuration[0], "windows", exe_version, url))

shutil.rmtree("LoL/temp")

for version in versions:
    path = f"LoL/{version[0]}/{version[1]}/league-client"
    os.makedirs(path, exist_ok=True)
    try:
        with open(f"{path}/{version[2]}.txt", "x") as out_file:
            out_file.write(version[3])
    except FileExistsError:
        pass
