import pymysql

if __name__ == '__main__':
    connection = pymysql.connect(user='root', password='123456',
                                 host='localhost',
                                 port=3306)
    cur = connection.cursor()
    # SQL statement
    sql1 = "select * from protein_network.blast"
    sql2 = "select * from protein_network.proteins"
    # select all proteins similar to A0T0J8 with blast scores larger than 500
    sql3 = "select protein2,Score,Organism from protein_network.blast where Score >= 500"
    # show top 5 most similar proteins of A0T0J8 given by blast and fasta
    sql4 = "SELECT Protein2,Score,E_value FROM protein_network.blast WHERE Protein1 = 'A0T0J8' ORDER BY Score DESC LIMIT 5"
    sql5 = "SELECT Protein2,Score,E_value FROM protein_network.fasta WHERE Protein1 = 'A0T0J8' ORDER BY Score DESC LIMIT 5"
    # Execute SQL query
    cur.execute(sql4)
    # retrieve the data using fetchall()
    data = cur.fetchall()
    # iterate and output
    print('blast result:')
    for i in data:
        print(i)
    cur.execute(sql5)
    # retrieve the data using fetchall()
    data = cur.fetchall()
    print('fasta result:')
    for i in data:
        print(i)
        # close the cursor
    cur.close()
    # close the connection
    connection.close()
