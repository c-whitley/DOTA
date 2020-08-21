import mysql.connector
from mysql.connector import Error

import numpy as np
import pandas as pd

import glob
import pickle


def pickle_read(file_name):
    """[summary]

    Args:
        file_name ([type]): [description]

    Returns:
        [type]: [description]
    """
    with open(file_name, "rb") as file:

        dict_ = pickle.load(file)
    return dict_

def pickle_write(obj, filename):
    """[summary]

    Args:
        obj ([type]): [description]
        filename ([type]): [description]
    """
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)


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


def execute_query(connection, query, verbose=False):
    """[summary]

    Args:
        connection ([type]): [description]
        query ([type]): [description]
    """
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()

        if verbose:
            print("Query executed successfully")
    except Error as e:
        if verbose:
            print(f"The error '{e}' occurred")