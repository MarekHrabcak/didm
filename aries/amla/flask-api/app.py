from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import connect
import requests

app = Flask(__name__)

@app.route('/aml', methods=['POST'])
def get_name():
    # Check if request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request body must be in JSON format"}), 400
    
    # Get the JSON data from the request
    json_data = request.json
    
    # Check if 'name' key exists in the JSON data
    if 'name' not in json_data:
        return jsonify({"error": "Name not found in JSON data"}), 400
    
    # Get the name from JSON data
    string_to_search = json_data['name']


    # Dabase connection
    mydb = mysql.connector.connect(
    host="host.docker.internal",
    user="user",
    password="user",
    database="amla",
    port="3306"
    )

    mycursor = mydb.cursor()

    # Search string
    # string_to_search = "Kean"
    # print(string_to_search)

    # SQL Select
    mycursor.execute("SELECT * FROM `amla` WHERE amla.name LIKE '" + string_to_search + "';")
        
    # Run sql query
    myresult = mycursor.fetchall()

    # Print result 
    # print(myresult)

    count = len(myresult)
    # print("Total rows are:  ", count)

    # Filter output
    if count > 0:
        print ("Found ", count)
        return jsonify({"message": f"Name '{string_to_search}' FOUND"}), 200

    else:
        print ("Not Found")
        return jsonify({"message": f"Name '{string_to_search}' NOT FOUND"}), 200


if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
