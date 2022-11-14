#pip install mysql.connector
#pip install MYSQL-connector-python
import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Kilburn",
  database="datamarket"
)

mycursor = mydb.cursor()

"""mycursor.execute("CREATE TABLE User (id INT AUTO_INCREMENT PRIMARY KEY, user_name VARCHAR(255),user_email VARCHAR(255),user_type VARCHAR(255), created_at DATETIME,updated_at DATETIME)")
mycursor.execute("CREATE TABLE Domain (id INT AUTO_INCREMENT PRIMARY KEY, domain VARCHAR(255), created_at DATETIME,updated_at DATETIME)")
mycursor.execute("CREATE TABLE Sub_Domain (id INT AUTO_INCREMENT PRIMARY KEY, domain_id INT,sub_domain VARCHAR(255), created_at DATETIME,updated_at DATETIME, FOREIGN KEY (domain_id) REFERENCES Domain(id))")
mycursor.execute("CREATE TABLE Dataset (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, title VARCHAR(255), description VARCHAR(255), domain_id INT, sub_domain_id INT,dataset_file_name VARCHAR(255),host_link VARCHAR(255),price DECIMAL, license VARCHAR(255), published_by VARCHAR(255),last_updated_date  DATETIME,created_at DATETIME,updated_at DATETIME, FOREIGN KEY (user_id) REFERENCES User(id), FOREIGN KEY (domain_id) REFERENCES Domain(id),FOREIGN KEY (sub_domain_id) REFERENCES Sub_Domain(id))")
mycursor.execute("CREATE TABLE Keyword_Inverted_Index (keyword VARCHAR(255), dataset_id INT,FOREIGN KEY (dataset_id) REFERENCES Dataset(id))")
mycursor.execute("CREATE TABLE Quality_information_Metadata (dataset_id INT,total_records INT, total_columns INT,file_size DECIMAL,completeness DECIMAL,summary VARCHAR(255),sample JSON,FOREIGN KEY (dataset_id) REFERENCES Dataset(id))")
"""
mycursor.execute("DESCRIBE User")
#print(mycursor.description)
list = []
for x in mycursor:
  list.append(x)


print(list)