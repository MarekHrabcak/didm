from attrs import define
from typing import Optional, Literal
import requests
import time

@define
class Expression:
    attribute_name: str
    predicate: str
    value: str

@define
class DID:
    did: str
    verkey: str

@define
class Schema:
    attributes: list[str]
    id: str
    name: str
    sequence_number: int
    ver: str
    version: str

    def create_from(d: dict) -> "Schema":
        return Schema(
            attributes=d["attrNames"],
            id=d["id"],
            name=d["name"],
            sequence_number=d["seqNo"],
            ver=d["ver"],
            version=d["version"],
        )

@define
class Connection:
    state: Literal["invitation"] | Literal["active"] | Literal["pending"]
    created_at: str
    updated_at: str
    connection_id: str
    their_role: str
    connection_protocol: str
    rfc23_state: str
    invitation_key: str
    accept: str
    invitation_mode: str
    their_label: str
    their_did: str

    def create_from(d: dict) -> "Connection":
        return Connection(
            state=d["state"],
            created_at=d["created_at"],
            updated_at=d["updated_at"],
            connection_id=d["connection_id"],
            their_role=d["their_role"],
            connection_protocol=d["connection_protocol"],
            rfc23_state=d["rfc23_state"],
            invitation_key=d["invitation_key"],
            accept=d["accept"],
            invitation_mode=d["invitation_mode"],
            their_label=d.get("their_label"),
            their_did=d.get("their_did")
        )

class Agent:
    def __init__(self, api_url: str, ledger_url: str, injected_headers: dict = {}):
        self.api_url = api_url
        self.ledger_url = ledger_url

        self.injected_headers = injected_headers
        
        public_did = self.get_public_did()
        if public_did is None:
            public_did = self.create_public_did()

        self.public_did = public_did
    
    def get_schema(self, schema_id: str) -> Optional[Schema]:
        response = requests.get(
            f"{self.api_url}/schemas/{schema_id}",
            headers=self.injected_headers
        ).json()

        schema = response.get("schema")
        if schema is None:
            return None
        
        return Schema.create_from(schema)
    
    def get_connections(self) -> list[Connection]:
        response = requests.get(
            f"{self.api_url}/connections",
            headers=self.injected_headers
        ).json()

        results = response.get("results")
        return list(
            [Connection.create_from(conn) for conn in results]
        )

    def get_created_schemas(self, schema_name: Optional[str] = None) -> list[Schema]:
        schema_ids = requests.get(
            f"{self.api_url}/schemas/created",
            params={
                "schema_name": schema_name
            } if schema_name else None,
            headers=self.injected_headers
        ).json().get("schema_ids")

        schemas = [self.get_schema(schema_id) for schema_id in schema_ids]

        return list(schemas)
    
    def send_proof_presential_proposal(
        self, 
        name: str,
        attributes: list[str], 
        connection_id: str,
        version: str = "1.0",
        restrictions: dict[str, str] = {},
        expressions: Optional[list[Expression]] = None
    ):
        requested_attributes = {}
        for attribute in attributes:
            restriction = restrictions.get(attribute)
            requested_attributes[f"0_{attribute}_uuid"] = {"name": attribute}
            if restriction is not None:
                requested_attributes[f"0_{attribute}_uuid"]["restrictions"] = [{f"attr::{attribute}::value": restriction}]
        
        requested_predicates = {}
        if expressions is not None:
            for expr in expressions:
                requested_predicates[f"0_{expr.attribute_name}_GE_uuid"] = {
                    "name": expr.attribute_name,
                    "p_type": expr.predicate,
                    "p_value": expr.value
                }


        response = requests.post(
            f"{self.api_url}/present-proof/send-request",
            json={
                "trace": True,
                "connection_id": connection_id,
                "proof_request": {
                    "name": name,
                    "version": version,
                    "requested_attributes": requested_attributes,
                    "requested_predicates": requested_predicates,
                    "timestamp": int(time.time() * 1000)
                }
            },
            headers=self.injected_headers
        )

        print(response.text)
    
    def create_credential_schema(self, schema_name: str, attributes: list, schema_version: str = None) -> Schema:
        if schema_version is None:
            existing_schema_versions = self.get_created_schemas(schema_name)
            existing_schema_versions.sort(key=lambda s: s.sequence_number)

            if len(existing_schema_versions) == 0:
                # there is no existing schema with this name
                schema_version = "1.0"
            else:
                # increment the last version number by one
                latest_schema =existing_schema_versions[-1]
                parts = latest_schema.version.split(".")
                parts[-1] = str(int(parts[-1]) + 1)
                schema_version = ".".join(parts)

        response = requests.post(
            f"{self.api_url}/schemas",
            json={
                "attributes": attributes,
                "schema_name": schema_name,
                "schema_version": schema_version
            },
            headers=self.injected_headers
        ).json()

        schema = response.get("schema")
        return Schema.create_from(schema)
    
    def create_credential_definition(self, schema: Schema) -> str:
        response = requests.post(
            f"{self.api_url}/credential-definitions",
            json={
                "revocation_registry_size": 1000,
                "schema_id": schema.id,
                "support_revocation": False,
                "tag": "default"
            },
            headers=self.injected_headers
        ).json()

        return response.get("credential_definition_id")
    
    def get_credential_definition_id(self, schema_id: str) -> str:
        response = requests.get(
            f"{self.api_url}/credential-definitions/created",
            params={
                "schema_id": schema_id
            },
            headers=self.injected_headers
        ).json()

        return response.get("credential_definition_ids")[0]
    
    def get_credential_definition(self, cred_def_id: str) -> Optional[dict]:
        response = requests.get(
            f"{self.api_url}/credential-definitions/{cred_def_id}",
            headers=self.injected_headers
        ).json()

        return response.get("credential_definition")
    
    def write_transaction_to_ledger(self, transaction_id: str) -> dict:
        response = requests.post(
            f"{self.api_url}/transactions/{transaction_id}/write",
            headers=self.injected_headers
        )

        if not response.text.startswith("{") or response.json().get("state") != "active":
            raise Exception(f"Failed to write transaction to ledger. {response.text}")
        
        return response.json()
    
    def create_revocation_registry(self, credential_definition_id: str, max_cred_num: int = 1000) -> dict:
        response = requests.post(
            f"{self.api_url}/revocation/create-registry",
            json={
                "credential_definition_id": credential_definition_id,
                "max_cred_num": max_cred_num
            },
            headers=self.injected_headers
        )

        response = response.json()
        registry_creation_result = response.get("result")

        revocation_registry_id = registry_creation_result.get("revoc_reg_id")
        if revocation_registry_id is None:
            raise Exception("Failed to create revocation registry!")
        
        requests.patch(
            f"{self.api_url}/revocation/registry/{revocation_registry_id}",
            json={
                "tails_public_uri": f"http://host.docker.internal:6543/revocation/registry/{revocation_registry_id}/tails-file"
            },
            headers=self.injected_headers
        )

        return registry_creation_result
    
    def set_endorser_info_for_connection(self, connection_id: str, endorser_did: str) -> dict:
        response = requests.post(
            f"{self.api_url}/transactions/{connection_id}/set-endorser-info",
            params={
                "conn_id": connection_id,
                "endorser_did": endorser_did
            },
            headers=self.injected_headers
        )

        result = response.json()
        if result.get("endorser_did") is None:
            raise Exception(f"Failed to set endorser did for connection! {response.text}")
        return result
    
    def set_endorser_role_for_connection(self, connection_id: str, my_job: Literal["TRANSACTION_ENDORSER"] | Literal["TRANSACTION_AUTHOR"]) -> dict:
        response = requests.post(
            f"{self.api_url}/transactions/{connection_id}/set-endorser-role",
            params={
                "conn_id": connection_id,
                "transaction_my_job": my_job
            },
            headers=self.injected_headers
        )

        result = response.json()
        if result.get("transaction_my_job") is None:
            raise Exception(f"Failed to set endorser role for connecton! {response.text}")
        
        return result

    def create_revocation_registry_transaction(self, revocation_registry_id: str, connection_id: str) -> dict:
        transaction = requests.post(
            f"{self.api_url}/revocation/registry/{revocation_registry_id}/definition",
            params={
                "conn_id": connection_id,
                "create_transaction_for_endorser": "false"
            },
            headers=self.injected_headers
        )

        if not transaction.text.startswith("{"):
            raise Exception(f"Failed to create revocation registry definition transaction! {transaction.text}")
        
        return transaction.json()
    
    def create_revocation_registry_entry_transaction(self, revocation_registry_id: str, connection_id: str) -> dict:
        transaction = requests.post(
            f"{self.api_url}/revocation/registry/{revocation_registry_id}/entry",
            params={
                "conn_id": connection_id,
                "create_transaction_for_endorser": "false"
            },
            headers=self.injected_headers
        )

        if not transaction.text.startswith("{"):
            raise Exception("Failed to create revocation registry entry transaction")
        
        return transaction.json()
    
    def create_credential_offer(self, schema: Schema, connection_id: str, credential: dict, comment: str = "Credential offer") -> dict:
        credential_definition_id = self.get_credential_definition_id(schema.id)

        # validate credential
        # for attribute in schema.attributes:
        #     if attribute not in credential.keys():
        #         raise Exception(f"Invalid credential! (missing '{attribute}' attribute)")
            
        response = requests.post(
            f"{self.api_url}/issue-credential/send",
            json={
                "auto_remove": True,
                "comment": comment,
                "connection_id": connection_id,
                "cred_def_id": credential_definition_id,
                "credential_proposal": {
                    "@type": "issue-credential/1.0/credential-preview",
                    "attributes": list([
                        {"name": attribute, "value": credential[attribute]} 
                            for attribute in schema.attributes
                    ]) 
                },
                "issuer_did": self.public_did.did,
                "schema_id": schema.id,
                # TODO
                "schema_issuer_did": self.public_did.did,
                "schema_name": schema.name,
                "schema_version": schema.version,
                "trace": True
            },
            headers=self.injected_headers
        )

        print(response.text)

        return response.json()

    def get_public_did(self) -> Optional[DID]:
        response = requests.get(
            f"{self.api_url}/wallet/did/public",
            headers=self.injected_headers
        ).json()

        result = response.get("result")
        if result is None or result.get("posture") != "posted":
            return None
        
        return DID(
            did=result.get("did"),
            verkey=result.get("verkey")
        )
    
    def create_public_did(self) -> DID:
        response = requests.post(
            f"{self.api_url}/wallet/did/create",
            json={
                "method": "sov"
            },
            headers=self.injected_headers
        ).json()

        result = response.get("result")
        
        did = result.get("did")
        verkey = result.get("verkey")

        requests.post(
            f"{self.ledger_url}/register",
            json={
                "did": did,
                "verkey": verkey
            }
        )


        response = requests.post(
            f"{self.api_url}/wallet/did/public",
            params={
                "did": did
            },
            headers=self.injected_headers
        ).json()

        result = response.get("result")
        if result is None or result.get("posture") != "posted":
            raise Exception("Failed to create a public DID")
        

        return DID(
            did=result.get("did"),
            verkey=result.get("verkey")
        )

