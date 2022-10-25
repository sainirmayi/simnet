import pymysql

if __name__ == '__main__':
    connection = pymysql.connect(user='root', password='123456',
                                 host='localhost',
                                 port=3306)

    cur = connection.cursor()
    # SQL statement
    sql1 = "select * from protein_network.blast"
    sql2 = "select * from protein_network.proteins"
    # Execute SQL query
    cur.execute(sql2)
    # retrieve the data using fetchall()
    data = cur.fetchall()
    # iterate and output
    for i in data:
        print(i)
        # close the cursor
    cur.close()
    # close the connection
    connection.close()
