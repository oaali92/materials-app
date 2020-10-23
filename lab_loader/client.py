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

    def __init__(self, host, port, database, user=None, password=None):
        """
        Constructs the client through a passed connection string

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
        """
        Returns a connection to postgres
        """
        try:
            connstr = f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
            conn = create_engine(connstr)

        except Exception:
            logging.error(
                "Connection failed. Please update your connection credentials."
            )
            return

        return conn

    def _db_table_exists(self, table):
        """
        Checks existence of a table in a postgres database
        
        Parameters
        ---------
            table : str
                table name for which to search
        """
        sql = f"select * from information_schema.tables where table_name = '{table}'"
        if self.conn:
            results = pd.read_sql_query(sql, self.conn)
        else:
            logging.error(
                "Please ensure a proper connection exists prior to querying your database"
            )
            return
        return bool(len(results))

    def get_data(self, table, query=None):
        """
        Retrieves data from client
        
        Parameters           
        ---------
            table : str
                table name for which to search
            query : str
                sql query to execute against client connection. if query is passed, the table parameter is ignored
        """
        if self.conn:
            if query is None:
                sql = f"select * from {table}"
            else:
                sql = query
            df = pd.read_sql_query(sql, self.conn)

            return df
        else:
            logging.error(
                "Please ensure a proper connection exists prior to querying your database."
            )

    def insert_data(self, df, table, index_column):
        """
        Inserts dataframe into postgres table. If the table does not exist, it will be created. If it does exist, it will be appended to.
        
        Parameters           
        ---------
            df : DataFrame
                dataframe to be inserted into table. dataframe must have matching columns to schema. ensure dataframe index matches the index_column in sql.
            table : str
                table name in sql database that will be inserted to
            index_column : str
                index column name in sql database. this is what prevents duplicates from being loaded
        """
        if self.conn:
            if self._db_table_exists(table):
                loaded_data = self.get_data(table)
                if len(loaded_data) > 0:
                    materials_in_db = list(loaded_data[index_column])
                    df = df.loc[~df.index.isin(materials_in_db)]
            if len(df) > 0:
                err = df.to_sql(table, self.conn, if_exists="append", index=True)
                if err is None:
                    logging.info("Data was successfully loaded.")
            else:
                logging.info("No new Hall or ICP measurements found.")
        else:
            logging.error(
                "Please ensure a proper connection exists prior to inserting into your database"
            )

