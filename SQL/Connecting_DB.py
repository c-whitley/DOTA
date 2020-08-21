import mysql.connector
from mysql.connector import Error


def create_connection(host_name, user_name, user_password, db_name):
    """Create a connection to a an mySQL database

    Args:
        host_name (str)): Host name of database.
        user_name (str): User name for logging in.
        user_password (str): Pass for supplied user name.
        db_name (str): Name of database.

    Returns:
        mySQL.connection: mySQL adapter connection object.
    """
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection


def execute_query(connection, query):
    """[summary]

    Args:
        connection ([type]): [description]
        query ([type]): [description]
    """
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")