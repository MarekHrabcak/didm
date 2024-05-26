from datetime import datetime, timedelta
from attrs import define
from typing import Optional
import requests

@define
class Tokens:
    access_token: str
    access_token_expires: datetime
    
    refresh_token: str
    refresh_token_expires: datetime

    username: str
    client_id: str

    scope: str

    def create_from(d: dict, username: str, client_id: str) -> "Tokens":
        now = datetime.now()

        return Tokens(
            access_token=d["access_token"],
            access_token_expires=now + timedelta(seconds=d["expires_in"]),
            refresh_token=d["refresh_token"],
            refresh_token_expires=now + timedelta(seconds=d["refresh_expires_in"]),
            username=username,
            client_id=client_id,
            scope=d["scope"]
        )

def get_token(
    keycloak_url: str, 
    grant_type: str, 
    username: str, 
    grant_value: str, 
    client_id: str, 
    realm: str = "master", 
    scope: str = "openid"
) -> Optional[Tokens]:
    response = requests.post(
        f"{keycloak_url}/realms/{realm}/protocol/openid-connect/token",
        data={
            "username": username,
            "client_id": client_id,
            "grant_type": grant_type,
            grant_type: grant_value,
            "scope": scope
        }
    )

    if response.status_code != 200:
        return None
    
    return Tokens.create_from(response.json(), username, client_id)