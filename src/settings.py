import os


# database = "maple_lobbying"
test_database = "lobbying_test"

host = os.getenv("DB_HOST", "localhost")
port = os.getenv("DB_PORT", "5432")
user = os.getenv("DB_USER", "geekc")
password = os.getenv("DB_PASSWORD", "asdf")
dbname = os.getenv("DB_NAME", test_database)

urls_dict_file = "data/urls_dict.pkl"

psql_params_dict = {
    "host": host,
    "port": port,
    "database": dbname,
    "user": user,
    "password": password,
}


psql_test_params_dict = psql_params_dict.copy()
psql_test_params_dict["database"] = test_database
