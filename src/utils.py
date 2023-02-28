import requests, psycopg2, logging
import src.settings as settings
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
########################
# Misc Utility Methods #
########################

def pull_html(url):
    headers={"User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"}
    result = requests.get(url, headers=headers)
    result.raise_for_status()
    return result.content

# Equivalent to converting to a set and back, but it preserves list order
def unique_values(sequence):
    seen = set()
    return [x for x in sequence if x not in seen and not seen.add(x)]

# Returns values of new_sequence that don't appear in old_sequence.
# This is so I only process new urls when I scrape recent reports
def new_values(new_sequence, old_sequence):
    return [x for x in new_sequence if x not in old_sequence]

def fetch_conn_and_cursor(params_dict):
    conn = psycopg2.connect(**params_dict)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT) # <-- ADD THIS LINE
    cursor = conn.cursor()
    return conn, cursor

def execute_query(sql_query, query_vars = None, params_dict = settings.psql_params_dict):
    conn, cursor = fetch_conn_and_cursor(params_dict)
    cursor.execute(sql_query, query_vars)
    response = cursor.fetchall()
    conn.close()
    return response

def does_table_exist(table_name, params_dict = None):
    response = execute_query("select exists(select * from information_schema.tables where table_name=%s)", (table_name,), params_dict=params_dict)
    response = response[0][0]
    return response

def does_database_exist(database_name, params_dict = None):
    params_dict = settings.psql_test_params_dict.copy()
    database_name = params_dict['database']
    params_dict['database'] = 'postgres'

    list_database = execute_query("select datname from pg_database;", params_dict=params_dict)
    return (database_name,) in list_database


def execute_sql_file(filename, params_dict = settings.psql_params_dict):
    with open(filename, 'r') as f:
        sql_file = f.read().splitlines()
    sql_commands = " ".join(sql_file).split(";")
    conn, cursor = fetch_conn_and_cursor(params_dict)
    for command in sql_commands:
        if command:
            logging.debug(f'Executing sql query {command}')
            cursor.execute(command)
    conn.commit()
    conn.close()

def generate_database_if_not_exists(params_dict):
    database = params_dict['database']
    if not does_database_exist(database):
        logging.info(f"Creating database {database}")
        conn, cursor = fetch_conn_and_cursor(params_dict)
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database)))
        conn.close()

    if not does_table_exist('headers', params_dict = params_dict):
        logging.info(f"Running migrations against {database}")
        execute_sql_file('migrations/create_tables.sql', params_dict = params_dict)


def re_create_test_database():
    params_dict = settings.psql_test_params_dict.copy()
    database_name = params_dict['database']
    params_dict['database'] = 'postgres'

    conn, cursor = fetch_conn_and_cursor(params_dict)

    if does_database_exist(database_name):
        cursor.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(database_name)))
    print(database_name)
    cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name)))
    conn.close()
    execute_sql_file('migrations/create_tables.sql', params_dict = settings.psql_test_params_dict)
