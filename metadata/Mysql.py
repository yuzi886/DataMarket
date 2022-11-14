import mysql.connector


#get the column value from a row
def Select_column(column_name,table_name, condition):
  mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Kilburn",
    database="datamarket"
  )
  mycursor = mydb.cursor()
  mycursor.execute("SELECT %s FROM %s WHERE %s"%(column_name,table_name,condition))
  myresult = mycursor.fetchall()
  mycursor.close()
  mydb.close()
  return myresult

#get the specific row
def Select_One(table_name, condition):
  mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Kilburn",
    database="datamarket"
  )
  mycursor = mydb.cursor()
  mycursor.execute("SELECT * FROM %s WHERE %s"%(table_name,condition))
  myresult = mycursor.fetchall()
  mycursor.close()
  mydb.close()
  return myresult


"""column_name_list should be ["user_id","host_link"]
   value_list should be ["1","'/home/csimage/git/DataMarket/csv/industry.csv'"]"""
def Insert_Row(table_name, column_name,value_list):
  mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Kilburn",
    database="datamarket"
  )
  mycursor = mydb.cursor()
  value = ""
  for x in value_list:
    if type(x).__name__ == "str" :
      value = value+"'"+x+"'"+","
    else:
      value = value+str(x)+","
  value = value[:-1]
  flag = True
  try:
    query = "INSERT INTO %s(%s) VALUES (%s)"%(table_name,column_name,value)
    print(query)
    mycursor.execute(query)
  except Exception as e:
    flag = False
    print(e)
  finally:
    mydb.close()
    mycursor.close()
    return flag
  

