import sys
import os
import argparse
import json
import readline

from datetime import datetime
from attrs import define

import keycloak
from agent import Agent, Expression


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

now = datetime.now
KEYCLOAK_URL = None

def ask_yes_no(question: str) -> bool:
    out = input(question)
    while out.lower() not in ["y", "n", "yes", "no"]:
        out = input(question)
    
    return out.lower() == "y" or out.lower() == "yes"

def replace_tokens(old_tokens: keycloak.Tokens, new_tokens: keycloak.Tokens):
    old_tokens.access_token = new_tokens.access_token
    old_tokens.access_token_expires = new_tokens.access_token_expires
    old_tokens.refresh_token = new_tokens.refresh_token
    old_tokens.refresh_token_expires = new_tokens.refresh_token_expires
    old_tokens.scope = new_tokens.scope
    old_tokens.username = new_tokens.username
    old_tokens.client_id = new_tokens.client_id

def ensure_valid_tokens(tokens: keycloak.Tokens):
    if now() >= tokens.access_token_expires:
        replace_tokens(
            tokens,
            keycloak.get_token(KEYCLOAK_URL, "refresh_token", tokens.username, tokens.refresh_token, tokens.client_id)
        )

def print_active_connections(tokens: keycloak.Tokens, agent: Agent):
    ensure_valid_tokens(tokens)
    agent.injected_headers = {"X-KEYCLOAK-JWT": tokens.access_token}

    connections = [conn for conn in agent.get_connections() if conn.state == "active"]
    if len(connections) != 0:
        print("Active connections:")
        for i, connection in enumerate(connections):
            label = connection.their_label if connection.their_label is not None else "Unlabeled"
            print(f"{i + 1}. With {label}, ID: {connection.connection_id}")
    else:
        print(bcolors.WARNING + "No active connections!" + bcolors.ENDC)

def create_credential_definition(tokens: keycloak.Tokens, agent: Agent):
    schema_name = input("Schema name: ")
    attributes = input("Comma divided attributes (attr1, attr2, attr3, ...): ").replace(" ", "").split(",")
    version = input("Schema version [default: auto-increment]: ")

    if version.replace(" ", "") == "":
        version = None
    
    ensure_valid_tokens(tokens)
    agent.injected_headers = {"X-KEYCLOAK-JWT": tokens.access_token}
    

    schema = agent.create_credential_schema(schema_name, attributes, version)
    print(bcolors.OKBLUE + f"Created schema {schema.id}, version {schema.version}" + bcolors.ENDC)
    
    credential_definition_id = agent.create_credential_definition(schema)
    print(bcolors.OKGREEN + f"Created credential definition with id: {credential_definition_id}" + bcolors.ENDC)
    

def send_credential_offer(tokens: keycloak.Tokens, agent: Agent):
    schema = None
    while schema is None:
        schema_id_or_name = input("Schema id or name: ")

        ensure_valid_tokens(tokens)
        agent.injected_headers = {"X-KEYCLOAK-JWT": tokens.access_token}

        maybe_schemas = agent.get_created_schemas(schema_id_or_name)
        if len(maybe_schemas) == 0:
            schema = agent.get_schema(schema_id_or_name)
        else:
            schema = maybe_schemas[0]
        
        if schema is None:
            print("Invalid schema id or name!")
    
    connection_id = None
    while connection_id is None:
        conn_id = input("Connection id: ")

        ensure_valid_tokens(tokens)
        agent.injected_headers = {"X-KEYCLOAK-JWT": tokens.access_token}

        connections = agent.get_connections()
        if conn_id not in [conn.connection_id for conn in connections]:
            print("Invalid connection id!")
        else:
            connection_id = conn_id

    print("Please input your credential JSON.")
    print("Attributes: " + str(schema.attributes))
    credential = None
    while credential is None:
        lines = []
        line = input(">")
        while line != "":
            lines.append(line)
            line = input(">")
        
        credential_json = "\n".join(lines)
        try:
            cred = json.loads(credential_json)
        except json.JSONDecodeError:
            print("Invalid JSON!")
            continue

        for attribute in schema.attributes:
            if cred.get(attribute) is None:
                print(f"Missing attribute: {attribute}!")
                cred = None
                break
        
        if cred is not None:
            credential = cred
    
    ensure_valid_tokens(tokens)
    agent.injected_headers = {"X-KEYCLOAK-JWT": tokens.access_token}


    offer = agent.create_credential_offer(schema, connection_id, credential)

    offer_state = offer["state"]
    if offer_state == "offer_sent":
        print(bcolors.OKGREEN + "Successfully created offer!" + bcolors.ENDC)
    else:
        print(bcolors.WARNING + f"There might have been an error with your credential offer, state: {offer_state}" + bcolors.ENDC)

def send_proof_request(tokens: keycloak.Tokens, agent: Agent):
    connection_id = None
    while connection_id is None:
        conn_id = input("Connection id: ")

        ensure_valid_tokens(tokens)
        agent.injected_headers = {"X-KEYCLOAK-JWT": tokens.access_token}

        connections = agent.get_connections()
        if conn_id not in [conn.connection_id for conn in connections]:
            print("Invalid connection id!")
        else:
            connection_id = conn_id
    
    schema = None
    while schema is None:
        schema_id_or_name = input("Schema id: ")

        ensure_valid_tokens(tokens)
        agent.injected_headers = {"X-KEYCLOAK-JWT": tokens.access_token}

        schema = agent.get_schema(schema_id_or_name)
        
        if schema is None:
            print("Invalid schema id or name!")
    
    print(f"Attributes: {schema.attributes}")
    attributes = None
    while attributes == None:
        attrs = input("Which attributes do want you the holder to present (attr1, attr2, ...)? ").replace(" ", "").split(",")
        for attr in attrs:
            if attr not in schema.attributes:
                print(f"Invalid attribute {attr}!")
                attrs = None
                break
        
        if attrs != None:
            attributes = attrs
    
    restrictions = {}
    want_to_add_restrictions = ask_yes_no("Do you want to add restrictions (Y/N)? ")
    while want_to_add_restrictions:
        key = input("Attribute? ")
        if key not in schema.attributes:
            continue
        value = input("Restriction value? ")

        restrictions[key] = value

        want_to_add_restrictions = ask_yes_no("Do you want to add another restriction (Y/N)? ")
    
    ensure_valid_tokens(tokens)
    agent.injected_headers = {"X-KEYCLOAK-JWT": tokens.access_token}

    agent.send_proof_presential_proposal("Proof request", attributes, connection_id, restrictions=restrictions)

    print(bcolors.OKGREEN + "Proof request sent!" + bcolors.ENDC)
    



def main(arguments: list[str]):
    parser = argparse.ArgumentParser(
        prog="agent-cli"
    )

    parser.add_argument("-a", "--agent-url", help="reverse proxy url", default="http://localhost:8080")
    parser.add_argument("-l", "--ledger-url", help="ledger url", default="http://localhost:9000")
    parser.add_argument("-k", "--keycloak-url", help="keycloak url", default="http://keycloak:8090")
    parser.add_argument("-c", "--credentials", help="a json file with keycloak credentials", default="credentials.json")

    args = parser.parse_args(arguments[1:])

    global KEYCLOAK_URL
    KEYCLOAK_URL = args.keycloak_url

    tokens = None
    if not os.path.exists(args.credentials):
        print("Please put in your keycloak login credentials:")
        print(bcolors.WARNING + f"WARNING: Your credentials will be saved in plaintext to '{args.credentials}'" + bcolors.ENDC)
        while tokens is None:
            username = input("Username: ")
            password = input("Password: ")

            tokens = keycloak.get_token(args.keycloak_url, "password", username, password, "agent")
            if tokens is None:
                print("Invalid credentials!")
        
        with open(args.credentials, "w+") as f:
            f.write(json.dumps({"username": username, "password": password}))
    else:
        credentials = None
        with open(args.credentials, "r") as f:
            credentials = json.loads(f.read())
        
        if credentials.get("username") is None or credentials.get("password") is None:
            print(bcolors.FAIL + f"Invalid credentials file ('{args.credentials}') - missing 'username' or 'password' key!" + bcolors.ENDC)
            return 1

        tokens = keycloak.get_token(args.keycloak_url, "password", credentials["username"], credentials["password"], "agent")
        if tokens is None:
            print(bcolors.FAIL + f"Invalid credentials file ('{args.credentials}') - invalid credentials!" + bcolors.ENDC)
            print(bcolors.WARNING + f"WARNING: Deleting {args.credentials}" + bcolors.ENDC)
            return 1
    
    print(bcolors.OKGREEN + "Successfully logged in!" + bcolors.ENDC)

    ensure_valid_tokens(tokens)
    agent = Agent(args.agent_url, args.ledger_url, {"X-KEYCLOAK-JWT": tokens.access_token})

    menu = {
        "1": print_active_connections,
        "2": create_credential_definition,
        "3": send_credential_offer,
        "4": send_proof_request
    }

    while True:

        print("""
--------------------------------------
|  Agent CLI Menu:                   |
|  1. Print active connections       |
|  2. Create a credential definition |
|  3. Send a cerdential offer        |
|  4. Send a proof request           |
|  E: Exit                           |
--------------------------------------
        """)
        option = input(">").replace(".", "")

        if option == "E":
            return 0
        
        if option not in menu.keys():
            print("Invalid option!")
            continue

        menu[option](tokens, agent)

if __name__ == "__main__":
    sys.exit(main(sys.argv))