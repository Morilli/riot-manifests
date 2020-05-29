import requests
import re
import json

def get_tokens(username, password) -> (str, str):
    session = requests.sessions.session()

    post_payload = {
        "client_id": "riot-client",
        "nonce": "none",
        "response_type": "token id_token",
        "redirect_uri": "http://localhost/redirect",
    }
    post_response = session.post("https://auth.riotgames.com/api/v1/authorization", json=post_payload)
    post_response.raise_for_status()

    put_payload = {
        "type": "auth",
        "username": username,
        "password": password
    }
    put_response = session.put("https://auth.riotgames.com/api/v1/authorization", json=put_payload)
    put_response.raise_for_status()

    bearer = re.search("access_token=(.*)&scope=", put_response.content.decode()).group(1)

    entitlements_token_response = session.post("https://entitlements.auth.riotgames.com/api/token/v1", json={"urn": "urn:entitlement:%"}, headers={"Authorization": f"Bearer {bearer}"})
    entitlements_token_response.raise_for_status()

    entitlements = json.loads(entitlements_token_response.content.decode())["entitlements_token"]

    return (entitlements, bearer)
