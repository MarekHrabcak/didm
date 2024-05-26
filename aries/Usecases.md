# Usecases

KYC scenarios running in Hyperledger Aries

- projects running in docker compose
    - von-network: A portable development level Indy Node network, including a Ledger Browser. (https://github.com/bcgov/von-network/ )
    - ARIES Cloud Agent Python (or any other web based agent for building SSI services) and wallets stored in server https://github.com/hyperledger/aries-cloudagent-python/ 

There are 5 agents (Actors) in usecases:
- Alice (WEB browser), 
- University (WEB browser), 
- Bank (API),
- a service that does AML sensitivity verification.

## UC1 
Alice is using browser for requesting validity of her education data on University: Surname, Given Name, Nationality, Date of Birth, Place of birth, Degree of education achieved, Status, Year of graduation. 
Presentation of similar usecases is here: https://www.youtube.com/watch?v=9WZxlrGMA3s

![Employee](https://github.com/Happy-PC/aries/assets/108731656/779c6833-ac11-4b06-a261-b63b383a419e)


- [ ] Ready in ACA-PY here: https://github.com/hyperledger/aries-cloudagent-python/blob/main/demo/AcmeDemoWorkshop.md  
- [ ] Ready in swagger here: https://github.com/hyperledger/aries-cloudagent-python/blob/main/demo/AriesOpenAPIDemo.md 

## UC2
Alice wants to get a loan from the bank. During the KYC process, the bank wants to verify data about Alice:  Degree of education achieved, Status, Year, Surname, Given Name. Bank is using API’s for communication with blockchain.

![UC2_BankUniversity_21012024 drawio](https://github.com/Happy-PC/aries/assets/108731656/b57fa396-949e-427a-af88-f484bce6a1a0)

￼
- [ ] Ready in ACA-PY here: https://github.com/hyperledger/aries-cloudagent-python/blob/main/demo/AcmeDemoWorkshop.md 
- [ ] Ready in swagger here: https://github.com/hyperledger/aries-cloudagent-python/blob/main/demo/AriesOpenAPIDemo.md 

## UC3
Alice will confirm the regular verification of her data in the list of AML sensitive persons stored in database. During data verification, the bank will also request information on Alice's AML sensitivity.

![UC4_AMLCheck_21012024 copy drawio](https://github.com/Happy-PC/aries/assets/108731656/929b8269-1554-4140-a7cf-5b9c453e5d97)￼

## UC4
Alice, University and bank are using Keycloak Identity provider to login into her web application or API’s.

![UC1_21012024 drawio](https://github.com/Happy-PC/aries/assets/108731656/393c2156-3140-4f90-a1b2-4dee9209e2ac)

￼
