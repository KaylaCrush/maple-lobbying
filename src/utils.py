import requests, psycopg2, logging, datetime
import src.settings as settings
from psycopg2 import sql
import psycopg2.extras as extras
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from bs4 import BeautifulSoup as bs

########################
# Misc Utility Methods #
########################

# import src.lobbyingScraper as ls
def pull_html(url):
    headers={"User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"}
    result = requests.get(str(url), headers=headers)
    result.raise_for_status()
    return result.content

def create_conn(params_dict = settings.psql_params_dict):
    conn = psycopg2.connect(**params_dict)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT) # <-- ADD THIS LINE
    return conn

def execute_query(sql_query, query_vars = None, params_dict = settings.psql_params_dict):
    with create_conn(params_dict) as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql_query, query_vars)
            response = cursor.fetchall()
    return response

def execute_sql_file(filename, params_dict = settings.psql_params_dict):
    with open(filename, 'r') as f:
        sql_file = f.read().splitlines()

    sql_commands = " ".join(sql_file).split(";")
    with create_conn(params_dict) as conn:
        with conn.cursor() as cursor:

            for command in sql_commands:
                if command:
                    logging.debug(f'Executing sql query {command}')
                    cursor.execute(command)
    return

def insert_table(table_name, columns, rows, params_dict=settings.psql_params_dict):
    cols = ','.join([col.lower().replace(",","").replace(" ","_").replace('/','or') for col in columns])
    query = "INSERT INTO %s(%s) VALUES %%s" % (table_name, cols)
    response = False
    with create_conn(params_dict) as conn:
        with conn.cursor() as cursor:
            try:
                extras.execute_values(cursor, query, rows)
                conn.commit()
                logging.debug(f"Data successfully inserted into table '{table_name}'")
                response = True

            except (Exception, psycopg2.DatabaseError) as error:
                logging.warning(f"Error: {error} On table {table_name}")
                conn.rollback()
                cursor.close()
                response = False
    return response


