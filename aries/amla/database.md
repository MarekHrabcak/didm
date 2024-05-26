# Database

## Run docker
```shell
cd amla
docker-compose up -d
```
## Manage database using phpmyadmin

http://localhost:8080/index.php 

root/root


# Bulk dataset info

## Download dataset
https://www.opensanctions.org/datasets/peps/
### PEP dataset
```shell
curl -o pep.txt https://data.opensanctions.org/datasets/20240202/peps/names.txt
```
## Prepare dataset for import
```CSV
1;Axmadova Aminat Ramzanovna
2;Ахмадова Аминат Рамзановна
3;Аминат Рамзановна Ахмадова
```
## Import dataset using phpMyAdmin console
![image](https://github.com/Happy-PC/aries/assets/108731656/1ea99584-19cd-4312-99de-007202320b98)
