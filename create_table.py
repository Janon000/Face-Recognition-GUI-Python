import sql_handler as sql
import datetime
import mysql.connector

pw = 'password'
db = 'facerec'

# create connection to server
#connection = sql.create_server_connection("localhost", "root", pw)

# create database facerec
#create_database_query = 'CREATE DATABASE facerec'
#sql.create_database(connection, create_database_query)

#create table in facerec called detected
create_face_table = """
CREATE TABLE detected3 (
  timestamp TIMESTAMP PRIMARY KEY,
  name VARCHAR(40) NOT NULL,
  imagepath VARCHAR(255) NOT NULL
  );
 """
db_connection = sql.create_db_connection1()

now = datetime.datetime.utcnow()
date_time = '1992-01-01'
name = 'test2'
filename = 'oogabooga'
#test = """
#INSERT INTO detected VALUES
#('1985-04-20', 'test', 'testpath.jpg')
#"""

#attempt = "INSERT INTO detected (timestamp, name, imagepath) VALUES (%s, %s, %s)", (now.strftime('%Y-%m-%d %H:%M:%S'),"name", "path")
#sql.execute_query(db_connection,attempt)
#val = ("2012-01-01", "John", "Highway 21")
#headshot_sql = "INSERT INTO detected (timestamp, name, imagepath) VALUES (%s, %s, %s)"


#connection1 = sql.create_db_connection1() # Connect to the Database
sql.execute_query(db_connection, create_face_table) # Execute our defined query


#mydb = mysql.connector.connect(
 # host="localhost",
 # user="root",
 # password="password",
 # database="facerec"
#)

#mycursor = mydb.cursor()

#sql = "INSERT INTO detected (timestamp, name, imagepath) VALUES (%s, %s, %s)"
#val = ("1992-01-01", "John", "Highway 21")
#mycursor.execute(sql, val)

#mydb.commit()

#print(mycursor.rowcount, "record inserted.")