import psycopg2
from dotenv import dotenv_values

class DatabaseHelper:
    _instance = None
    _env_vars = dotenv_values(".env")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = psycopg2.connect(
                dbname=cls._get_env('POSTGRES_DB'),
                user=cls._get_env('POSTGRES_USER'),
                password=cls._get_env('POSTGRES_PASSWORD'),
                host=cls._get_env('POSTGRES_HOST'),
                port=cls._get_env('POSTGRES_PORT'),
            )
        return cls._instance

    @staticmethod
    def _get_env(key):
        return DatabaseHelper._env_vars.get(key)

    def execute_query(self, query, data=None):
        with self.connection.cursor() as cursor:
            if data:
                cursor.execute(query, data)
            else:
                cursor.execute(query)
            return cursor.fetchall()

    def close_connection(self):
        self.connection.close()