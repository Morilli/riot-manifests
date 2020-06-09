import requests
import re
import json

def get_lor_tokens(username, password, session=None) -> (str, str, str, str):
    if session is None:
        session = requests.sessions.session()

    post_payload = {
        "client_id": "bacon-client",
        "nonce": "none",
        "response_type": "token id_token",
        "redirect_uri": "http://localhost/redirect",
        "scope": "openid ban lol link account"
    }
    post_response = session.post("https://auth.riotgames.com/api/v1/authorization", json=post_payload, timeout=1)
    post_response.raise_for_status()

    put_payload = {
        "type": "auth",
        "username": username,
        "password": password
    }
    put_response = session.put("https://auth.riotgames.com/api/v1/authorization", json=put_payload, timeout=1)
    put_response.raise_for_status()

    access_token, id_token = re.search("access_token=(.*)&scope=.*id_token=(.*)&token_type=", put_response.content.decode()).groups()

    entitlements_token_response = session.post("https://entitlements.auth.riotgames.com/api/token/v1", json={"urn": "urn:entitlement:%"}, headers={"Authorization": f"Bearer {access_token}"}, timeout=1)
    entitlements_token_response.raise_for_status()
    entitlements_token = json.loads(entitlements_token_response.content)["entitlements_token"]

    userinfo_response = session.get("https://auth.riotgames.com/userinfo", headers={"Authorization": f"Bearer {access_token}"}, timeout=1)
    userinfo_response.raise_for_status()
    userinfo = userinfo_response.content.decode()

    pas_response = session.get("https://riot-geo.pas.si.riotgames.com/pas/v1/service/lor-game", headers={"Authorization": f"Bearer {access_token}"}, timeout=1)
    pas_response.raise_for_status()
    pas = pas_response.content.decode()

    return (entitlements_token, access_token, id_token, userinfo, pas)
