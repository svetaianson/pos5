from dotenv import load_dotenv
from os import getenv
from typing  import Union

import pymysql


class Database:
        
    # Возврашает подключение к БД
    def connection(self):
        load_dotenv()
        return pymysql.connect(
            host = getenv("DB_HOST"),
            user = getenv("DB_USER"),
            password = getenv("DB_PASSWORD"),
            database = getenv("DB_NAME"),
            port = int(getenv("DB_PORT"))
        )
        
    # Выбор из БД
    def select(self, table: str, columns: Union[str, list[str]], identifier: str = None):
        data: Union[bool, tuple] = False
        sql = f"SELECT {columns if type(columns) == str else ','.join(columns)} FROM {table}" + ("" if identifier is None else f" WHERE {identifier}")
        connection = self.connection()
        cursor = connection.cursor()
        try:
            cursor.execute(sql)
            data = cursor.fetchone()
        except:
            data = False
        finally:
            connection.close()
            return data
        
        
        


