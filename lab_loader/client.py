import pandas as pd
import logging
from sqlalchemy import create_engine

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
        Inserts data from a pandas dataframe through the client. Handles duplicates
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
            connstr=f'postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}'
            conn = create_engine(connstr)

        except Exception:
            logging.error("Connection failed. Please update your connection credentials.")
            return
        
        return conn
    
    def _db_table_exists(self, table):
        sql = f"select * from information_schema.tables where table_name = '{table}'"
        if (self.conn):
            results = pd.read_sql_query(sql, self.conn)
        else:
            logging.error("Please ensure a proper connection exists prior to querying your database")
            return
        return bool(len(results))

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
    
    def insert_data(self, df, table):       
        if (self.conn):
            if (self._db_table_exists(table)):
                loaded_data = self.get_data(table)         
                if len(loaded_data) > 0:
                    materials_in_db = list(loaded_data['material_uid'])
                    print(materials_in_db)
                    df = df.loc[~df.index.isin(materials_in_db)]
            if len(df) > 0:
                df.to_sql(table, self.conn, if_exists='append', index=True)
        else:
            logging.error("Please ensure a proper connection exists prior to inserting into your database")