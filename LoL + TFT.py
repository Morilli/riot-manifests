import requests
import json
import os
from multiprocessing.pool import ThreadPool

version_sets = ["BR1", "EUN1", "EUW1", "JP1", "KR", "LA1", "LA2", "NA1", "OC1", "PBE1", "RU", "TR1"]

def update_versions(region):
    for OS in ["android", "ios", "macos", "windows"]:
        url = f"https://sieve.services.riotcdn.net/api/v1/products/lol/version-sets/{region}?q[platform]={OS}"
        releases = requests.get(url)
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
