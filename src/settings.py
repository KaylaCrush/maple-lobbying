host = 'localhost'
port = '5432'
user = 'geekc'
password = 'asdf'
database = 'maple_lobbying'
test_database = 'lobbying_test'
urls_dict_file = 'urls_dict.pkl'
current_urls_file = 'all_current_urls.pkl'


psql_params_dict = {
    'host'      : host,
    'port'      : port,
    'database'  : 'maple_lobbying',
    'user'      : user,
    'password'  : password
}


psql_test_params_dict = psql_params_dict
psql_test_params_dict['database'] = test_database
