# Create new agent manually
## Clone folder for new Keycloak UID 90afb701-fae5-40b4-8895-e387ba34902jh
1. copy folder AliceTemplate2
2. change in file docker/docker-compose.yaml
    - services name (f.e. agent-template2 - will be the username)
    - command port (f.e. --port 8130 )
    - ports (f.e. 8130-8137:8130-8137)

## Run docker container for new user
```shell
./run_demo webstart -l
```