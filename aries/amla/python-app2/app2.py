import mysql.connector
from mysql.connector import connect


def main():
    
    mydb = mysql.connector.connect(
    host="host.docker.internal",
    user="user",
    password="user",
    database="amla",
    port="3306"
    )

    mycursor = mydb.cursor()
    
    # Search string
    string_to_search = "Kean"
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
    else:
        print ("Not Found")


if __name__ == "__main__":
    main()