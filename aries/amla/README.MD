**Run API**  
```shell
docker-compose build # After changes
docker/compose run -d
```

**DEBUG API Locally in Python terminal (database is not working, API only)**
```shell
cd flask-api
flask --app app.py --debug run
curl -X POST http://127.0.0.1:5000/name -H "Content-Type: application/json" -d '{"name": "Kean"}'
# database error is valid response
```

**Edit DB using phpMyAdmin**  
```html 
http://localhost:8080/index.php
```
root/root  


