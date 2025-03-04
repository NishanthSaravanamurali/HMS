import psycopg2

def init_db():
    conn = psycopg2.connect(
        host="db",
        database="cloud_test1",
        user="postgres",
        password="Database"
    )
    return conn

#def init_db():
#    conn = psycopg2.connect(
#        host="localhost",
#        database="Assignment3",
#        user="postgres",
#        password="Database"
#    )
#    return conn
