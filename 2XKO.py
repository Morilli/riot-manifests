from utils import save_file, setup_session
import os

def update_versions():
    lion_releases = session.get("https://sieve.services.riotcdn.net/api/v1/products/lion/version-sets/prod_client", timeout=2)
    lion_releases.raise_for_status()

    for release in lion_releases.json()["releases"]:
        artifact_type_id = release["release"]["labels"]["riot:artifact_type_id"]["values"][0]
        artifact_version_id = release["release"]["labels"]["riot:artifact_version_id"]["values"][0]
        platform = release["release"]["labels"]["riot:platform"]["values"][0]
        path = f'2XKO/{artifact_type_id}/{platform}' if platform != "windows" else f'2XKO/{artifact_type_id}'

        filename = f"{artifact_version_id}.txt" if artifact_type_id == "base_release" else f"{release["release"]["labels"]["Stream"]["values"][0]}_{artifact_version_id}.txt"
        os.makedirs(path, exist_ok=True)
        save_file(f"{path}/{filename}", release["download"]["url"])

session = setup_session()

update_versions()
