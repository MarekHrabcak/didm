import logging
import os
import socket
import jose
import requests
import urllib.parse

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Any, Union
from keycloak import KeycloakOpenID

def resolve_host(host: str) -> str:
    return str(socket.gethostbyname(host))

def env_or_default(variable_name: str, default: str) -> str:
    value = os.environ.get(variable_name)

    return default if value is None else value

keycloak_host = env_or_default("KEYCLOAK_HOST", "keycloak")
keycloak_port = env_or_default("KEYCLOAK_PORT", "8090")
keycloak_protocol = env_or_default("KEYCLOAK_PROTOCOL", "http://")
realm_name = env_or_default("KEYCLOAK_REALM", "master")
client_id = env_or_default("KEYCLOAK_CLIENT_ID", "agent")


def decode_and_verify_token(access_token: str) -> dict:
    kc = KeycloakOpenID(
        server_url=keycloak_protocol + resolve_host(keycloak_host) + ":" + keycloak_port,
        realm_name=realm_name,
        client_id=client_id,
        verify=False
    )

    public_key = "-----BEGIN PUBLIC KEY-----\n" + kc.public_key() + "\n-----END PUBLIC KEY-----"
    verification_options = {"verify-signature": True, "verify_aud": False, "verify_exp": True}

    return kc.decode_token(access_token, public_key, options=verification_options)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=["*"],
)

@app.api_route("/{full_path:path}", methods=["GET", "POST", "DELETE", "PUT", "PATCH"])
async def catch_all(request: Request, full_path: str, response: Response):
    token = request.headers.get('X-KEYCLOAK-JWT')
    if token is None:
        response.status_code = 401
        response.headers['X-PROXY-INTERCEPT'] = '1'
        return {"error": "Unauthorized"}
    
    try:
        token = decode_and_verify_token(token)
    except jose.exceptions.ExpiredSignatureError:
        response.status_code = 401
        response.headers['X-PROXY-INTERCEPT'] = '1'
        return {"error": "Expired token!"}
    
    audience = token.get('aud')
    if token.get('aud') is None:
        response.status_code = 401
        response.headers['X-PROXY-INTERCEPT'] = '1'
        return {"error": "Missing audience!"}
    
    if type(audience) == list:
        # filter all http:// and https:// audiences
        valid_audiences = [
            aud for aud in audience if aud.startswith('http://') or aud.startswith('https://')
        ]

        if len(valid_audiences) == 0:
            response.status_code = 401
            response.headers['X-PROXY-INTERCEPT'] = '1'
            return {"error": "No valid agent audience found!"}

        # TODO: add logic for choosing the correct audience by port

        audience = audience[0]

    headers = dict([
        (k, v) for (k, v) in request.headers.items() if k != 'X-KEYCLOAK-JWT'
    ])

    encoded_query_params = urllib.parse.urlencode(dict(request.query_params.items()))

    url = audience + f'/{full_path}'
    if encoded_query_params != '':
        url += '?' + encoded_query_params

    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        body = b''
        async for chunk in request.stream():
            body += chunk
    

    if request.method == "GET":
        request_func = requests.get
    elif request.method == "POST":
        request_func = requests.post
    elif request.method == "DELETE":
        request_func = requests.delete
    elif request.method == "PUT":
        request_func = requests.put
    elif request.method == "PATCH":
        request_func = requests.patch
    elif request.method == "OPTIONS":
        request_func = requests.options

    proxy_response = request_func(
        url=url,
        data=body,
        headers=headers
    )

    for k, v in proxy_response.headers.items():
        response.headers[k] = v
    response.body = proxy_response.content
    response.status_code = proxy_response.status_code

    logging.warn(f"proxied request from {request.client.host} to {url}")

    return response

