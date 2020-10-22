import psycopg2
import pandas as pd
import logging

class Client:
    """
    The Client provides methods to perform CRUD operations through an odbc connection
    
    Attributes
    ---------
    cnxnstr : str
        The connection string of the odbc database being read
    
    
    Methods
    ---------
    get_data():
        Retrieves data through the client into a pandas dataframe.
    
    insert_data():
        Inserts data from a pandas dataframe through the client. Handles duplicates.
    """

    
    def __init__(self, host, port, database, user=None, password = None):
        """
        Constructs the connection through a passed connection string

        Parameters           
        ---------
            host : str
                server name or ip address for postgres db
            port : int
                port number for postgres db. default windows is 5432
            database : str
                database name to which to connect
            user : str
                username for postgresql database connection
                default is usually postgres
            password : str
                password for postgresql database connection  
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.conn = self._create_postgres_connection()


    
    def _create_postgres_connection(self):
        try:
            conn = psycopg2.connect(
                host = self.host,
                port = self.port,
                database = self.database,
                user = self.user,
                password = self.password
            )
        except Exception:
            logging.error("Connection failed. Please update your connection credentials.")
            return
        
        return conn
    
    def get_data(self, table, query = None):
        if (self.conn):
            if query is None:
                sql = f'select * from {table}'
            else:
                sql = query
            df = pd.read_sql_query(sql, self.conn)

            return df
        else:
            logging.error("Please ensure a proper connection exists prior to querying your database.")
    