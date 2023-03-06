host = 'prod-sharedstack-postgresinstance19cdd68a-tcd37grhqqcj.ci5mri6omzhg.us-east-1.rds.amazonaws.com'
port = '5432'
user = 'kaylacrush'
password = 'DJhW4lmNwvP1Xp5nlMymYS'

database = 'maple_lobbying'
test_database = 'lobbying_test'

urls_dict_file = 'data/urls_dict.pkl'

psql_params_dict = {
    'host'      : host,
    'port'      : port,
    'database'  : 'maple_lobbying',
    'user'      : user,
    'password'  : password
}


psql_test_params_dict = psql_params_dict.copy()
psql_test_params_dict['database'] = test_database
