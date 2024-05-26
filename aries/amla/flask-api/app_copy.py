from flask import Flask, jsonify
import mysql.connector
from mysql.connector import connect
import requests

app = Flask(__name__)

# MySQL connection parameters
config = {
  'user': 'user',
  'password': 'user',
  'host': 'host.docker.internal',
  'port': 3306,
  'database': 'amla',
#   'ssl_ca': 'path_to_ca_certificate.pem',  # Path to CA certificate file
}

try:
    # Establish a secure connection to the MySQL server
    conn = connect(**config)
    
    if conn.is_connected():
        print('Connected to MySQL database')
        
        # Perform database operations here
        # # API endpoint for searching strings
        @app.route('/<string_to_search>', methods=['POST'])
        def search_string(string_to_search):
            # Query to search for the string in the database
            query = "SELECT * FROM amla WHERE name %s"
            print(query)
            conn.execute(query, ('%' + string_to_search + '%',))
            result = conn.fetchall()
            print(result)

            # Check if any rows were returned
            if result:
                response = {'status': 'Found'}
            else:
                response = {'status': 'Not Found'}

            return jsonify(response)
        
except mysql.connector.Error as e:
    print(f"Error connecting to MySQL: {e}")

finally:
    # Close the connection
    if 'conn' in locals() and conn.is_connected():
        conn.close()
        print('MySQL connection closed')


if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
