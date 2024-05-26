# Aries framework with Hyperledger INDY
# Requirements
Docker Desktop is required!
### Run von-network (local)
```shell
cd aries/von-network
```
If running for the first time:
```shell
./manage build
```

```shell
./manage start
./manage logs
```
**See nodes status**
http://localhost:9000/

<img width="922" alt="image" src="https://github.com/Happy-PC/aries/assets/108731656/f23bef5a-829c-4bca-859b-50c67455ecf4">

### Run DEMO in Docker

**Map the `keycloak` host to localhost:**
- In /etc/hosts:
```
# ...
127.0.0.1 keycloak
# ...
```

**FIX Mac port 8021 problem **
```shell
sudo launchctl unload -w /System/Library/LaunchDaemons/com.apple.ftp-proxy.plist
```
**SET Mac forward requests from 192.168.65.9 to 127.0.0.1: **
```shell

#Forward all traffic to ip 192.168.65.9 to localhost on MAC OSX
sudo ifconfig lo0 192.168.65.9 alias
```
**Run DEMO**
```shell
cd aries/aries-acapy-controllers/AliceFaberAcmeDemo
LEDGER_URL=http://host.docker.internal:9000 ALICE_AGENT_HOST=host.docker.internal ./run_demo webstart
```

### Run APPS in browser
http://localhost:9021/

http://localhost:9031/

http://localhost:9041/

http://localhost:9000/ 

## AML module
```shell
cd AML
docker-compose up -d
```
Open phpMyAdmin in browser   
http://localhost:8080/index.php   


**AML API testing**  
Successfull scenario request
```shell
curl -X POST http://127.0.0.1:8090/aml -H "Content-Type: application/json" -d '{"name": "Kean"}'
```
Response  
{
  "message": "Name 'Kean' FOUND"
}

Unsuccessfull scenario request
```shell
curl -X POST http://127.0.0.1:8090/aml -H "Content-Type: application/json" -d '{"name": "Kean2"}'
```
Response  
{
  "message": "Name 'John Doe' NOT FOUND"
}

**Multiagent**
```shell
cd agent/v3_multidemo  
docker-compose build  
docker-compose run  
```

**Create wallet Using SWAGGER**  
See the following two files (renamed to *.txt to satisfy github):  
postgres-indy-args-local.yml.txt  
faber-local-multitenant.sh.txt  

run a local von-network (./manage start 192.168.0.11 --logs, your IP will differ)  
run a local postgres (the command is in the yml file included above)  
(optionally) run a tails server if you are going to be revoking credentials  
Run the agent using the above .sh script  

Once the agent is running:  

Open the swagger page in a browser http://localhost:8021  
Create a new sub-wallet - remember the token  
authenticate the swagger page using Bearer <your sub-wallet token>  
you can now call admin endpoints for your sub-wallet  
re-start your aca-py agent ( to kill it and then run the .sh script again)  
You will need to re-authenticate with your bearer token again  
call the admin endpoints for your subwallet  


## Keycloak
cd keycloak/

TBD...


# HOWTO
## GIT repo VON-Network
git clone https://github.com/bcgov/von-network

**aca-py repo**
https://github.com/hyperledger/aries-acapy-controllers.git

**Aries Cloud Agent Python (ACA-Py) Demos in DOCKER**
https://github.com/hyperledger/aries-cloudagent-python/blob/main/demo/README.md#running-in-docker
git clone https://github.com/hyperledger/aries-cloudagent-python.git 

# Usecases
https://github.com/Happy-PC/aries/blob/main/Usecases.md

### OR run commands in terminal for public von-network
```shell
cd aries/aries-acapy-controllers/AliceFaberAcmeDemo
LEDGER_URL=http://test.bcovrin.vonx.io ./run_demo webstart -l 
```

# Public DID Registration process
1. POST {agent_admin_api}/wallet/did/create
body:
```json
{
  "method": "sov"
}
```

2. Get DID and VERKEY from response

3. POST `{ledger}/register`
```json
{
    "did": {did from previous response},
    "verkey": {verkey from previous response}
}
```

4. POST `{admin_agent_api}/wallet/did/public?did={registered public did}`

# Create credential schema
Requirements:
- a public did that is assigned to the agent you are using

1. POST `{agent_admin_api}/schemas`
Example body:
```json
{
  "attributes": [
    "name",
    "aml_result"
  ],
  "schema_name": "aml-asessment",
  "schema_version": "1.0"
}
```

Verify schema
```shell
curl -X 'GET' \
  'http://localhost:8021/schemas/5jnvZf9HuHKnehVtH5QSUd%3A2%3AmarekTestSchema%3A1.0' \
  -H 'accept: application/json'
```

Response  

```json
{
  "schema": {
    "ver": "1.0",
    "id": "5jnvZf9HuHKnehVtH5QSUd:2:marekTestSchema:1.0",
    "name": "marekTestSchema",
    "version": "1.0",
    "attrNames": [
      "name",
      "age"
    ],
    "seqNo": 114
  }
}
```

2. Get schema ID from result

3. POST `{agent_admin_api}/credential-definitions`
```json
{
  "revocation_registry_size": 1000,
  "schema_id": "X7Rwt7PVftD5yZbaN8TunD:2:aml-asessment:1.0",
  "support_revocation": true,
  "tag": "default"
}
```

# Send credential offer
Requirements:
- a public did that is assigned to the agent you are using
- a credential schema that is posted to the ledger

1. POST `{agnet_admin_api}/issue-credential/send-offer`
Example body:
```json
{
  "auto_issue": true,
  "auto_remove": true,
  "comment": "hello",
  "connection_id": "0bf9d0a4-3534-4708-a0d8-c2c8c8a09658",
  "cred_def_id": "X7Rwt7PVftD5yZbaN8TunD:3:CL:63:default",
  "credential_preview": {
    "@type": "issue-credential/1.0/credential-preview",
    "attributes": [
      {
        "name": "name",
        "value": "Alice"
      },
      {
        "name": "aml_result",
        "value": "terrorist"
      }
    ]
  },
  "trace": true
}
```

https://github.com/hyperledger/aries-rfcs/tree/main/features/0453-issue-credential-v2  


![image](https://github.com/Happy-PC/aries/assets/108731656/26a2868a-4ebc-484c-aae0-0d37eff0635b)


1 Request /issue-credential/send-offer
```json
curl -X 'POST' \
  'http://localhost:8021/issue-credential/send-offer' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "auto_issue": true,
  "auto_remove": true,
  "comment": "test",
  "connection_id": "e6d00cad-7326-4563-b868-3b9f7e66b890",
  "cred_def_id": "5jnvZf9HuHKnehVtH5QSUd:3:CL:112:faber.agent.degree_schema",
  "credential_preview": {
    "@type": "issue-credential/1.0/credential-preview",
    "attributes": [
      {
        "name": "degree",
        "value": "mgr"
      },
{
        "name": "birthdate_dateint",
        "value": "11"
      },
{
        "name": "name",
        "value": "user"
      },
{
        "name": "date",
        "value": "01012024"
      },

{
        "name": "timestamp",
        "value": "01010101"
      }
    ]
  },
  "trace": true
}'
```

2 response
```json
{
  "state": "offer_sent",
  "created_at": "2024-03-29T15:01:43.493309Z",
  "updated_at": "2024-03-29T15:01:43.493309Z",
  "trace": true,
  "credential_exchange_id": "48e5be39-9e48-4085-88de-2ea3afa2fbff",
  "connection_id": "e6d00cad-7326-4563-b868-3b9f7e66b890",
  "thread_id": "4641a32b-d9f9-4fbd-8e0a-a5298ea8dfdc",
  "initiator": "self",
  "role": "issuer",
  "credential_definition_id": "5jnvZf9HuHKnehVtH5QSUd:3:CL:112:faber.agent.degree_schema",
  "schema_id": "5jnvZf9HuHKnehVtH5QSUd:2:degree schema:65.45.76",
  "credential_proposal_dict": {
    "@type": "https://didcomm.org/issue-credential/1.0/propose-credential",
    "@id": "a2f9f2ac-dfd8-46d1-bf88-eaf8d324df50",
    "~trace": {
      "target": "log",
      "full_thread": true,
      "trace_reports": []
    },
    "comment": "test",
    "credential_proposal": {
      "@type": "https://didcomm.org/issue-credential/1.0/credential-preview",
      "attributes": [
        {
          "name": "degree",
          "value": "mgr"
        },
        {
          "name": "birthdate_dateint",
          "value": "11"
        },
        {
          "name": "name",
          "value": "user"
        },
        {
          "name": "date",
          "value": "01012024"
        },
        {
          "name": "timestamp",
          "value": "01010101"
        }
      ]
    },
    "cred_def_id": "5jnvZf9HuHKnehVtH5QSUd:3:CL:112:faber.agent.degree_schema"
  },
  "credential_offer_dict": {
    "@type": "https://didcomm.org/issue-credential/1.0/offer-credential",
    "@id": "4641a32b-d9f9-4fbd-8e0a-a5298ea8dfdc",
    "~thread": {
      "thid": "4641a32b-d9f9-4fbd-8e0a-a5298ea8dfdc"
    },
    "~trace": {
      "target": "log",
      "full_thread": true,
      "trace_reports": []
    },
    "comment": "test",
    "credential_preview": {
      "@type": "https://didcomm.org/issue-credential/1.0/credential-preview",
      "attributes": [
        {
          "name": "degree",
          "value": "mgr"
        },
        {
          "name": "birthdate_dateint",
          "value": "11"
        },
        {
          "name": "name",
          "value": "user"
        },
        {
          "name": "date",
          "value": "01012024"
        },
        {
          "name": "timestamp",
          "value": "01010101"
        }
      ]
    },
    "offers~attach": [
      {
        "@id": "libindy-cred-offer-0",
        "mime-type": "application/json",
        "data": {
          "base64": "eyJzY2hlbWFfaWQiOiAiNWpudlpmOUh1SEtuZWhWdEg1UVNVZDoyOmRlZ3JlZSBzY2hlbWE6NjUuNDUuNzYiLCAiY3JlZF9kZWZfaWQiOiAiNWpudlpmOUh1SEtuZWhWdEg1UVNVZDozOkNMOjExMjpmYWJlci5hZ2VudC5kZWdyZWVfc2NoZW1hIiwgImtleV9jb3JyZWN0bmVzc19wcm9vZiI6IHsiYyI6ICIxMTA3ODA3NzY4NDE1NjAxNjQ5MzAzODY0NjI1ODA1NjIxODc5Nzk2OTc1ODg0OTEyNDk2MTAzMjkxNjU1OTE5NzQzMTkyMTU4NDQ1MzIiLCAieHpfY2FwIjogIjEwMDY3MDk1MzA2MjEzMjIwNTYwNzkyNTcyNDM1MDYxMzA3NjI0OTY3NDkxNjQ5NzgyOTY1MTQ3OTM1NDQ2NjY5MjQ4MDU2MTY5NzgxNzQ5OTAzODE4ODAzMTIyODE1MzAxNDAzMTIxNzE2MDg0MjM1MTY2MjU5OTcyMDgyNDA3NzYxNTk1MzY2NzQ4ODI0MzUzODk3NjY0MTkwMDI5Nzk2NDM0MjQxNjk5MTMxMzk0NTM2MDU0MDk3Mzc4NzE5MzM0NDU4ODYxNjMxMTY2ODMyNjI4MTExOTgzMjc0NTIxMjc5MzU1OTQzMTkyNzI5MzQxNzE0Njg0MTkxMDE3MTc4NTcyOTgyODU4NjE3ODg5NjQxNDY5Njc0MjgxMzQ3OTc4Nzg4MjYxNjA0NTExMDA4Mjk2NzI2MTQxMDIwNTAwODU3MDIxNzg1NDYwOTA0MDM4NzI1MjEyNDg3NjExMzcyODk4MTA2NjczMTQzMDY2OTM1NTY2MjMwOTI5Nzc4MDk3Mjg1Mzc5NjY1MTg0MzU1NjYwNTkwNTIwMzQ5MDUyNjI0NDgzNzI0OTYyOTg4MDg1NDQ3MjYzMDQ2Mzc5Mzc0MzQyNjY0MTI2NTgzMjkxNjk5Mjg2ODI2OTM5NzU4MTc0NjU0MjM2MjMwNDMwNzA3NTA1MDUwMjI2MzA5ODM1NzA2NTE2NDMzNDQ3NjkxNzkzNTg0MTA4NDQwOTY5NjExMjM2MDA2MTQ5NzYxNjkwNTE2MTY5MDE2MDU2MzMzODczOTQxMzg5ODE1ODQ5OTI0MTEyNjQxOTAxNjc4MTU2Mzg2OTkxNjA4MDg4MTAyMDA1ODc0ODg0MzYzNzM2Mzg2ODM1MzcxODk1NjcxMjMzMDk1MDA3MjU4MDIzMjg4NTQwMDk1NzI0NzM2NzAwMzQwMjE0NzEiLCAieHJfY2FwIjogW1sibWFzdGVyX3NlY3JldCIsICIyMDI5OTQ3MDk5NTk0NDM3MzE5Mzg2OTc3NTI5NjY3NDY5NjU0NDI3OTIzNjI5NDQzNjk0MjgyOTU3OTg2MjE2OTY4NTk4ODI3ODIzNjg5NDQ3ODU0NDkwODIyOTA5NzI4ODEyODQ0MDE3MDUyNDEyODI1NzczOTE0OTM0NTU1MzA3OTY2NDM0Njc2NjI5NzM3NzYyNjM0MjI1MzM1Nzg4NDk0Mzg3MzIzMzgxNjE3ODA1NDQ4MTk4NjYzNjgwMTY1NDI3MDY2MjQ4NTQ1ODkxOTAyMjUzMjE3MjM5MjMwMjg4OTE0MTI2NTYyODczNjg1NDM4OTg2MzYyMjAwNTcxNjc0MzkwMzQzOTAwODQ2ODMzMDI1Nzk5NzEzOTI3ODgxNzk1MjA3NzQ4OTk1NTc0NzA4ODUyODY3MDIwMDI2NDk3ODQ5NTU0OTM3NzQ2ODEzODIyNDg1NTk1NTkzMDY3MDc3NTc5NDEwNzk0NjY4NjM1ODEwODU1MzYzMDE1MDIzOTMzODAyMzU4NzI3MjQzMjE3NTA1OTY4MTgzOTE5MjY3MDgzOTE1ODY3MzY3MDY2NTA3ODk0MzUyOTU4NDY5MTQ0ODk2ODg5ODAwMzk3NTI0NzQ0OTU3MjM0MTI0NjEzNzAxMjc2MjEzMjg0ODUyMDE3MDMzMzk4NjI0MzExNjI4MzcxOTcyMDk3ODQ1NTU5MDU0NTk3Mzk1MzQ3MTk3NjkwNTE1ODYyOTQyMjA4NDYwMzU4OTM0NzA0NzI5MjY1MjU1MDU2OTM0NDUzOTY0NTkzNzU5Njc5MjA2MTgzMzA3NDYyMTk5Njc4ODM0NTk3NzI4MzczNzAzMTA0Mzk3Nzk3ODAzMTU0MjMwODYxOTU1Nzc1MjUwNDc2OTg2OTA1MzM4NTM4ODkzNDc5NDgwMzY0ODkzIl0sIFsiZGF0ZSIsICI4NjQ4NDAzMjQ2MTg1MzgxODUxNjI1MDE1Njg5NjQwMTcyNjU0MzA4NDAxMDAwNzQyNDk0NDU3MTQ5NjgxNjQwNTI3ODAzNzMzMzA3MDI2NDY5NzM2Nzc4MDc1NjU4NDE2MTA2MTQzMTk0NjkxNDQ5NjU5MDYyNDU0MDMwNDc4MTgyMzIyMzI3MzMxMjEyNzEyMTc2NDU4OTgxNDg3MDE4MTMyMDkwNzM1NTk4NTQ2OTEzODU2MDU3MTk2MDA4ODQ5Njg3MDE3NTMyNjIzMjgyMDM5ODUxNTUyNjAwMDk2NDkzNTMzMzQzODgzMjMwNDAxMzg0NzgwNTEyMDc5OTA4Njg0MzE0MjMzMjg4ODQ4MTI4MTA5ODAyOTg5NTExODc4NjY5MjA4MDU4NzUzMDcwNDU2NzAxNzczODY0NzIwNjI3MTI2NzIyNTg2NTg3NTc0NDI4NTgxMTcwNzg5NDkzMjI2NzA3MTU0NjI0MzQ5MDY4MDA1ODk4Njc5MDEwMzI3NDk5NTkzOTgxMjM2NjM2NjkwMjI5OTEwMjc5NDExMzIxMzI1NTEyODkwOTMyMjA5NDM4MzExMjk0OTQ2OTc4MzQ4OTA5Njk2NDk2NjczMjQ5MzU5MjEzMTYzODI3MTIzNjE2MzAxOTUxNzE3OTU4NjYzNzYyNjM4NTgwMjYxNTY5MzA1NzI0NTEzNDYyOTc3MzUwOTI0NTAzMTgzODc0NzQzNjc4NjAwMjQ0OTIyNTE2MjU2NTAwMjc1ODA0MjU4NDEwMDQ1MDk5OTQwNzQ3ODkwMzMxNDY3ODcwODcxMDU2NDUwMTI1MDIyMDYxNTI3NTE4NTYwNzA4MjQzNjM5MjMyODA4MzMyMDg5NjIwMDIwNDkyNDAwNDA4MDg0NTU5Nzc1MTAwNTIyMTcyMjU1ODU1NTYiXSwgWyJiaXJ0aGRhdGVfZGF0ZWludCIsICIyMzg2MTc5NTE0Njk5MTA0MzMwNzA4MzY2ODQ1NTQ3MjY5MDA4MTMzNDY3NDY3NDU3MDUxMTQ1NjkzNjM4NDQ2NjgzODg0OTg3MzE0MzU0MDQzMjg3Njc2NTc1NjcyNjAzNjQzMTk0MzQxMTEwNTI1NTc1NjMyNDM4NzA1ODkxODUxMzA5Nzg5NzYwMjk2NzY5Mjc0NTM0OTI1NzgxMzMyMzY4MTQ4NzE5MzQ2MTkwMTczMTAwNDE2NDQxODg0Mzk1MjUxMDI3MTA1ODIyMjMxOTg2NTY1MjQyOTA4NDEzMDUxMzI5MTQwOTQwNjg4NjgwNDA3ODA2NTIxMzM5NDM1MTE2MDQ2MzMwMzc3MzY5MjIyMDI1MTMxMTk0MzgxODI4NTM5OTM2MTY1MzkwNTM3Nzk1Nzc0NDE4OTIzNTI4OTYzOTMxMDUwNzgzNzMwNzI5NDkzMzI1MDQ1OTYzMTQxMTMxMDUwOTg0NjYwNzA1ODcxNzcxNjkwNjUzMTA1NTYwNDA1MzM2MTYwNzg0NzcwMDA0ODIwMjc0ODMzMTM5NDQ0MzYyNzE1Nzg3NDQ4MDUyNzQ5MzYwNDEwNjQ5MzYzOTIzNjkzMDQ5NDc2MTM5NDQzMTk4NTg3MTU4NTI4MDQ3MzYxMDMwMjkyNDc0OTA4MDYzODQ3NDg3NzgzODQzMDM1ODc3OTEyNDUzOTc2ODY0NDEzODM0MTQzODk4NTQzNDA3ODE4NzU1MDg1ODQ4NTI0NDg5MTAzOTgwMzM3MjUxMTc5NjE2MTEyNDczNjUyMDI2MjA0MTI3NTczMTYyODI3MzczMDgzODc4NTI5MDUxODMxODUxOTY5MTU3NjI5NzM5ODE4NjM2MDIzODkwODU2Mjg2NjQzNjEyNzc2ODg3MjgzNjA1NDE2MTc3NDkxMDA5OTU4Il0sIFsiZGVncmVlIiwgIjIzNzQ3NTI3MTQzNjUyODk1MjE2OTM0OTIwOTQzODAxNzE1MDYzMjQzODQxODAzOTY1NTYyMTE4NTA1NjEzMTk3MTkxMzk1NDgzMTQ2NDU0MzEzMTM3NTQ2ODkyNTc1MDE4NzU4NjUzMDU5MTMzMTM1ODg5NDU2MjM3MzAxOTc0MzY3MjYzMDQxMzUxNDE3MzM4MTUxNzI2MTM5Nzk2MjgzNDQ4OTMwOTMxNDM5NjAxNDMxMTUyNDI1MzA0Njk2MzQ1NDUyOTQxMzQyMDU0OTAyNzYwMjMwNTMyODE5NTMwMDYxNTYxMzE3Njk0MDA4NDAyMTYwNTE3MDk1NTk5Mzc0NDAzMDAwNDIwMTAzNjMyOTc5MDYzODkyMjQzNDQ0NTg1MjQwNDQwMTkwNzgwNzI4MjcxOTg5MzA2MTk3MTYyMDMxNjcwODcwMzAyMjU4OTg1NDMzMDk4NTYxNzIwNzk5Njc3MjQ4NDc5OTkwMzIzNDIyMTkwNjY5OTU0NjkzODI5Nzc5MjM3NDc3ODIyNzM0MTI0NzE5MjQxODcwMjU1MjMzMjY0MzI1MDA5MjAxODY0MzgzNzMxODU2MDEwMzI4MzY2NDYzMDkyODQ4MDg2NzMxMDU4NDM3NzM4MTg3MDIwMzgxMjMxMTA1NjU4NjgzMjUwNTkyOTgwODE1NDk4NjcyNDExNDUyNjMwMTk4NzIyNTYwMzUwMjIyMjc3MjM4NzMxNzA5NjgwNTUyMTQ3NTA4NzA3NTAwMTQzMDc1NTE4ODk4MjkzNDk3MzI1MzM1Mjg0NjUzMzI2NDg5NzU5MjczNzQ3NzUxMTg2NzA4OTgxMDQ5NjY1NTIzNzQ1MDk2NzMzODU3NDM5MjQyNzA0ODU0NDM3ODI1MzM2NjQyNzY1OTkzNzk0NzAyMTM2NTQyNzgxOTgiXSwgWyJuYW1lIiwgIjI3MjgzNjkzNjI3MzM3OTYwNTc2MTQ1NDcyNTY5MDYxMDIwMzc4NzQyMDAwNTAyMjUyNTM5MDY2OTY4MjQzNTQwNzI2NDY4NDIzMzE4ODczMjI2Mjc3ODQ1NzMwMjA0NjM3NTIwNTY4ODgxNTEzMjAwMTIyMDA1OTgwMjg1NTYzMTkwNzU2NzI0NjU0ODUxMTIyMTIyNjEzMzAwMjQ2MDEzNTc0MzkwMDM2MzEzNzMzOTIzMTIzNTYwMDE4MTU4NTE3MjU2NTMxMjU2MDY1MTE1OTk0NzYxMTk3NzE1OTE2OTAyNzUwOTcxNTQ1Nzg0MjAzMTAwODUyNDU2ODQwNzcwMTU1OTgyOTc4Nzc4ODc4ODc2ODc1OTM4NDg0Nzg1MjA2NzgwMjU0OTg5NjUwODUzMzc5Mjk1MDA4ODM3NDMwNzEzMzQyODgzODQ2OTQ5NTU0MzE3MDk5NjU2MTA0NTg4MDEyMTAyNDE0Njk1NDc1MDU3ODA1NTg4ODE2NzUwODMwMzMxMjkwNDg0NDIxMzIzOTI3Mzk5NDQ3OTMwNDg4NTg2NDY3MzQyNzQ2MDE4MTI4MTQxOTI4OTE2MjI0NTAyMjY4NjY3MjM2NzIzMjA5MjQ1MDA2Mjg0NDc4MTI2NTc1MzU5MTQzMzk3NzEyNjUwOTY5NzgzOTI1NDg1Mzc4ODkyMzc5NzUzNzIxMTUwMjIyNzQxMzg0OTkxMzI0MTA1MzAxODAzNTc0MDAzOTYyNTcxOTcyMDc0MjEzNjE0Mzc1Mjk3MjQyODI4NTI4NTMwODQ0MTIyNDkyNzI2NzkwNTg2NDU5MTE4NjAzNDIyMjM3MjQ4MjgxNzQzMTgxNjA4NTcyODk1OTc2NDQzOTg0NDM5MDUwODA3NDMxNDk5MTkxMjU4NzA1MDA1ODc3ODM0OTMzNjgiXSwgWyJ0aW1lc3RhbXAiLCAiMTA3MDIyNDc5MDMzNDI2MDk0MDg2ODkwNDQ3NjYwMzc4NjM5NjIzMTQ0NjUyOTc1ODA0NDIwNTg0ODIzMDI1MjcyMTg4MTkwNDQwMzAyNjg3MzY2NjU3OTY3MTEyMDQwNDI5NDQxMjU2NzYzMzExOTYyNjgxMTg4Mzg5MTMxOTc3MjIzOTc1MTY4Mzk2MjU3Mzc0MTgwNzM3MzQxOTQ3ODY3MDYyOTYzMTE4MTk3MDYxOTg3MzM1MjE3NTE4OTQwNTIxMzU5OTc4MDUzNzg0Mjk4Mzc0NjE5NjYxNTE2MDYxMDA4ODkyOTc2Nzk3ODY4ODg0NzMzMzQ2MzE4NTQxNzY5NjEwMzM0OTMwMDI5NDgyMDI5NDA1OTY2MDM5MzE0MDExMjE2ODExNDU5NzcwNjEwMjMxNTYxMzgzMjI1MzgyOTEyMDcxMTczNTI4OTQzMjM2NTYzNDc0Mjc4NzE2NTExNzkyMzAxMjc0NTY3NzMyODg0MDUxNzQ0NDE0MzAyMzU0ODkzODU1MjE1NjA4NTM5NzU3MTk2NTAyMjM2MjA3MTU2Njg1MjAwMTAxMTE2NjYyMDI5MjU2MjkwMTA3NzE5MDQwOTc2OTQ5NDM2MjUwMDY0MzU2OTI0NTcxMTk3OTU2OTM0MDIwMjk5MTY3NTYzNTY2OTkwMjQ3NzM5MDY5NDA2NzEyODQ0Njk3NTQ5NTM1OTg4NTA4NDU2NzYxNjUxMzYxNDE2MjE4MTk2NTE4OTIzMDIzODEzMDA1NDYzOTY2NDUwNzE1NjkyMTk4MjM0NzQ4NzM2NTUzMjA5NDM3MjUyODQzMjQ5OTE2ODQ5NDUzMTU0MzQ5OTA1NjI5MDE1MTcyMzU1MDIyMTA2Nzk3NjY1MTg5NjAwOTU5ODQ2Mjk4NzI5NjYxODU2OTgzMDMwODA2MSJdXX0sICJub25jZSI6ICIxMTMzOTk2NjMyMDg2NzQ2MTY3ODI5MDUzIn0="
        }
      }
    ]
  },
  "credential_offer": {
    "schema_id": "5jnvZf9HuHKnehVtH5QSUd:2:degree schema:65.45.76",
    "cred_def_id": "5jnvZf9HuHKnehVtH5QSUd:3:CL:112:faber.agent.degree_schema",
    "nonce": "1133996632086746167829053",
    "key_correctness_proof": {
      "c": "110780776841560164930386462580562187979697588491249610329165591974319215844532",
      "xz_cap": "1006709530621322056079257243506130762496749164978296514793544666924805616978174990381880312281530140312171608423516625997208240776159536674882435389766419002979643424169913139453605409737871933445886163116683262811198327452127935594319272934171468419101717857298285861788964146967428134797878826160451100829672614102050085702178546090403872521248761137289810667314306693556623092977809728537966518435566059052034905262448372496298808544726304637937434266412658329169928682693975817465423623043070750505022630983570651643344769179358410844096961123600614976169051616901605633387394138981584992411264190167815638699160808810200587488436373638683537189567123309500725802328854009572473670034021471",
      "xr_cap": [
        [
          "master_secret",
          "2029947099594437319386977529667469654427923629443694282957986216968598827823689447854490822909728812844017052412825773914934555307966434676629737762634225335788494387323381617805448198663680165427066248545891902253217239230288914126562873685438986362200571674390343900846833025799713927881795207748995574708852867020026497849554937746813822485595593067077579410794668635810855363015023933802358727243217505968183919267083915867367066507894352958469144896889800397524744957234124613701276213284852017033398624311628371972097845559054597395347197690515862942208460358934704729265255056934453964593759679206183307462199678834597728373703104397797803154230861955775250476986905338538893479480364893"
        ],
        [
          "date",
          "864840324618538185162501568964017265430840100074249445714968164052780373330702646973677807565841610614319469144965906245403047818232232733121271217645898148701813209073559854691385605719600884968701753262328203985155260009649353334388323040138478051207990868431423328884812810980298951187866920805875307045670177386472062712672258658757442858117078949322670715462434906800589867901032749959398123663669022991027941132132551289093220943831129494697834890969649667324935921316382712361630195171795866376263858026156930572451346297735092450318387474367860024492251625650027580425841004509994074789033146787087105645012502206152751856070824363923280833208962002049240040808455977510052217225585556"
        ],
        [
          "birthdate_dateint",
          "2386179514699104330708366845547269008133467467457051145693638446683884987314354043287676575672603643194341110525575632438705891851309789760296769274534925781332368148719346190173100416441884395251027105822231986565242908413051329140940688680407806521339435116046330377369222025131194381828539936165390537795774418923528963931050783730729493325045963141131050984660705871771690653105560405336160784770004820274833139444362715787448052749360410649363923693049476139443198587158528047361030292474908063847487783843035877912453976864413834143898543407818755085848524489103980337251179616112473652026204127573162827373083878529051831851969157629739818636023890856286643612776887283605416177491009958"
        ],
        [
          "degree",
          "2374752714365289521693492094380171506324384180396556211850561319719139548314645431313754689257501875865305913313588945623730197436726304135141733815172613979628344893093143960143115242530469634545294134205490276023053281953006156131769400840216051709559937440300042010363297906389224344458524044019078072827198930619716203167087030225898543309856172079967724847999032342219066995469382977923747782273412471924187025523326432500920186438373185601032836646309284808673105843773818702038123110565868325059298081549867241145263019872256035022227723873170968055214750870750014307551889829349732533528465332648975927374775118670898104966552374509673385743924270485443782533664276599379470213654278198"
        ],
        [
          "name",
          "2728369362733796057614547256906102037874200050225253906696824354072646842331887322627784573020463752056888151320012200598028556319075672465485112212261330024601357439003631373392312356001815851725653125606511599476119771591690275097154578420310085245684077015598297877887887687593848478520678025498965085337929500883743071334288384694955431709965610458801210241469547505780558881675083033129048442132392739944793048858646734274601812814192891622450226866723672320924500628447812657535914339771265096978392548537889237975372115022274138499132410530180357400396257197207421361437529724282852853084412249272679058645911860342223724828174318160857289597644398443905080743149919125870500587783493368"
        ],
        [
          "timestamp",
          "1070224790334260940868904476603786396231446529758044205848230252721881904403026873666579671120404294412567633119626811883891319772239751683962573741807373419478670629631181970619873352175189405213599780537842983746196615160610088929767978688847333463185417696103349300294820294059660393140112168114597706102315613832253829120711735289432365634742787165117923012745677328840517444143023548938552156085397571965022362071566852001011166620292562901077190409769494362500643569245711979569340202991675635669902477390694067128446975495359885084567616513614162181965189230238130054639664507156921982347487365532094372528432499168494531543499056290151723550221067976651896009598462987296618569830308061"
        ]
      ]
    }
  },
  "auto_offer": false,
  "auto_issue": true,
  "auto_remove": true
}
```




**TODO**  
Keycloak  (M)
- [x] add User, University, Bank, AML  
- [x] authentication to agent via keycloak (user accounts, role, client scope, add role, scope create mapper, add scope to client, add role to user (test token on jwtio))  

Frontend (I)
- [ ] Create schema definition
- [ ] Send credentials
- [ ] Create credential definition
- [ ] Accept credentials
- [ ] keycloak authentication (Faber, Alice fix)
- [ ] Fix Faber logout
- [ ] Fix acme auth
- [ ] Create credential howto for AML agent and University
- [ ] Rename Alice --> User (Green), Faber --> University (Blue), Acme --> Bank (Grey), Faber --> AML (Red)
- [ ] AML agent - spustit noveho agenta aby vedeli Alice - AML vytvorit connection (M)

Agent  (M)
- [x] agent for every user

Usecases   
-
**UC1 - Registrácia používateľa**  
Používateľ (entita) sa digitálne zaregistruje do systému. Počas registrácie vloží požadované údaje do formulára a Identity Provider používateľovi založí účet a umožní mu vytvoriť si meno a heslo. Následne administrátor vytvorí pre nového používateľa agenta a URI, ktorú používa nový agent v Docker sieti, vloží do parametra Audience na Keycloak IDP. Reverzná proxy validuje v každej http požiadavke okrem platnosti tokenu aj Audience a podľa tejto hodnoty prepošle komunikáciu do príslušného Aries agenta v Docker sieti.  

![UC1_RegistraciaPouzivatela_24032024 drawio](https://github.com/Happy-PC/aries/assets/108731656/966c7e94-6783-4d4c-83a8-7b4109cbde55)  

**UC2 - Autentizácia aktérov do aplikácii**  

Používateľ, Univerzita aj Banka používajú na prihlasovanie do aplikácii prihlasovacie údaje vydané Identity Providerom. Počas komunikácie obsahuje každé volanie od aktéra JWT token, ktorý je overený na službe Identity Providera. Pri zaslaní nesprávneho prihlasovacieho údaju je aktérovi zamietnutý prístup k údajom. 

![UC2_KeycloakAuthentication_24032024 drawio](https://github.com/Happy-PC/aries/assets/108731656/c30b3e86-2467-4c97-ab49-b9299042e650)  

**UC3 - Overenie verifikovateľného poverenia**  

Používateľ pomocou prehliadača požiada svoju Univerzitu o potvrdenie platnosti údajov o jeho dosiahnutom vzdelaní: priezvisko, meno, národnosť, dátum narodenia, miesto narodenia, dosiahnutý stupeň vzdelania, status a rok ukončenia štúdia.
 
![UC3_Alice2University_24032024](https://github.com/Happy-PC/aries/assets/108731656/d87fd7e2-9e05-40db-ad5f-896ceb816b96)

Vzor verifikovateľného poverenia.  

```json
{
    "userAttributes": {
      "given_name": "Janko",
      "family_name": "Hraško",
      "birth_date": {
        "day": 1,
        "month": 1,
        "year": 2000
      },
      "birth_city": "Bratislava",
      "birth_country": "Slovakia",
      "personalIdentificationNumber": "010120001234",
      "gender": "Male",
      "nationality": "Slovak",
      "resident_address": {
        "resident_street": "Hrachová",
        "resident_house_number": "1",
        "resident_city": "Bratislava",
        "resident_postal_code": "Bratislava",
        "resident_country": "Slovakia"
      },
      "identityCardIssue": {
        "day": 1,
        "month": 1,
        "year": 2000,
        "place" : "Bratislava"
      },
      "identityCardExpiration": {
        "day": 1,
        "month": 1,
        "year": 2005
      },
      "identityCardNumber": "SK123123"
    },
    "verifiableCredentials": [
      {
        "type": "given_name",
        "value": "Janko",
        "verified": true
      },
      {
        "type": "driverLicense",
        "value": "DL123456",
        "verified": true
      },
      {
        "type": "passport",
        "value": "P123456",
        "verified": false
      }
    ]
  }
  
```


**UC4 - Banka overí poverenia Používateľa vydané Univerzitou**  

Používateľ chce získať pôžičku od banky. Počas KYC procesu chce banka overiť údaje o Používateľovi: dosiahnutý stupeň vzdelania, status, rok, priezvisko, meno. Banka použije na komunikáciu so sieťou blockchain API a na API sa autentizuje pomocou JWT tokenu vydaného Identity Providerom. 

![UC4_BankUniversity_21032024 drawio](https://github.com/Happy-PC/aries/assets/108731656/da7aa60e-ae4d-471b-9f34-8fbedf1e991d)


**UC5 – Screening používateľa v sankčných zoznamoch**

Používateľ potvrdí tzv. screening, t.j. overovanie svojich osobných údajov v sankčných zoznamoch senzitívnych osôb v AML module. Výsledok overenia je uložený do blockchainu. Po odsúhlasení screeningu používateľom je výsledok screeningu oznámený banke v odpovedi na jej požiadavku.

![UC5_AMLCheck_21032024 drawio](https://github.com/Happy-PC/aries/assets/108731656/a78783b3-9105-43ad-9996-c36d6169277b)


https://docs.igrant.io/ssi/ssi-apg/
https://github.com/SmithSamuelM/leopy/blob/master/src/demo/FaberAliceCredential.md


