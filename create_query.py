import mysql.connector
import datetime

now = datetime.datetime.utcnow()

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="password",
  database="facerec"
)

mycursor = mydb.cursor()

sql = "INSERT INTO detected2 (timestamp, name, imagepath) VALUES (%s, %s, %s)"
val = ('2005-01-01', "John2", "Highway 21")
tuuple = sql, val
mycursor.execute(sql, val)

mydb.commit()

print(mycursor.rowcount, "record inserted.")