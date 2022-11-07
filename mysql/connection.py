import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Kilburn"
)

mycursor = mydb.cursor()

mycursor.execute("CREATE DATABASE datamarket")