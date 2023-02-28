import logging, argparse, datetime, pickle

import src.settings as settings
import src.lobbyingDataPage as ldp
import src.lobbyingScraper as ls
import src.utils as utils



########################
# COMMAND LINE METHODS #
########################
# -a --all
def do_initial_setup():
    params_dict = settings.psql_params_dict
    utils.generate_database_if_not_exists(params_dict)
    scrape_current_urls_to_dict()
    process_saved_urls()

# -r --recent
def scrape_recent_urls():
    new_urls = ls.get_recent_disclosures()
    unique_new_urls = load_and_update_saved_urls(new_urls, return_all=False)
    process_urls(unique_new_urls)

# -t --test
# Grab records_per_year for each year between start_year and end_year
def generate_test_data(records_per_year = 10):
    params_dict = settings.psql_test_params_dict
    utils.re_create_test_database()

    with open(settings.urls_dict_file, 'rb') as f:
        urls_dict = pickle.load(f)

    for year in urls_dict.keys():
        if urls_dict[year]:
            logging.info(f"Fetching {records_per_year} disclosure reports for {year}")
            url_iter = iter(urls_dict[year])
            records_found = 0
            while records_found < records_per_year:
                page = ldp.PageFactory(next(url_iter))
                if len([key for key in page.tables.__dict__.keys() if page.tables.__dict__[key]]) > 1:
                    page.save(params_dict=params_dict)
                    records_found = records_found + 1

# -p --process
def process_saved_urls(offset = 0):
    all_urls = load_and_update_saved_urls()
    process_urls(all_urls, offset=offset)


###############################
# Command line Helper Methods #
###############################

# Probably an overloaded function imo. If passed no arguments, simply loads the url dictionary as a list and returns it
# If given a new dictionary of urls, it will add the new values to url_dict
# if return_all = true returns a list of all urls
# if return_all = false returns only new urls not originally present in url_dict
def load_and_update_saved_urls(new_url_dict = None, return_all = True):
    with open(settings.urls_dict_file, 'rb') as f:
        urls_dict = pickle.load(f)
    returned_urls = []
    for year in new_url_dict.keys():
        if new_url_dict:
            urls_dict[year] = utils.unique_values(urls_dict[year] + new_url_dict[year])
            if not return_all:
                returned_urls = returned_urls + utils.new_values(new_url_dict[year], urls_dict[year])
        else:
            returned_urls = returned_urls + urls_dict[year]
    if new_url_dict:
        with open(settings.current_urls_file, 'wb') as f: pickle.dump(urls_dict, f)
    return returned_urls

def process_urls(urls, offset = 0):
    for url in urls[offset:]:
        ldp.PageFactory(url).save()

def scrape_current_urls_to_dict():
    with open(settings.urls_dict_file, 'rb') as f:
        urls_dict = pickle.load(f)
    start_year = 2005
    end_year = datetime.date.today().year
    print(f"Pickling all disclosure URLs between {start_year} and {end_year}")
    print(urls_dict.keys())
    for year in range(start_year, end_year+1):
        if year not in urls_dict.keys():
            print(f"Pulling disclosures for year {year}")
            results = ls.get_disclosures_by_year(year)
            print(f'{len(results)} disclosures found for year {year}')
            urls_dict[year] = results
            with open('urls_dict.pkl', 'wb+') as f:
                pickle.dump(urls_dict, f)
    print("Job finished")

###################
# Argument Parser #
###################

def parse_arguments():
    verbosity_levels = [logging.ERROR, logging.INFO, logging.DEBUG]

    all_help = """Scrape, process, and save all disclosure reports from sec.state.ma.us"""
    recent_help = """Scrape, process and save disclosure reports from the last 2 years. Default action"""
    test_help = """Create test data from saved urls and upload them to the database"""
    process_help = """Process saved urls. Can optionally include a specific year"""
    verbose_help = "set logging level. Default = 0, max = 2"

    help_msg = f"""Maple Lobbying Scraper"""

    parser = argparse.ArgumentParser(description = help_msg)
    parser.add_argument('-a', '--all', help = all_help, action = 'store_true')
    parser.add_argument('-r', '--recent', help = recent_help, action='store_true')
    parser.add_argument('-t', '--test', help = test_help, action = 'store_true')
    parser.add_argument('-p', '--process', help = process_help, nargs = '?', metavar = 'YEAR')
    parser.add_argument('-v', '--verbose', help=verbose_help, action='count', default=0)

    args = parser.parse_args()
    logging.basicConfig(level=verbosity_levels[args.verbose])

    if args.all:
        do_initial_setup()
    elif args.test:
        generate_test_data()
    elif args.process is not None:
        logging.info(f'Processing saved urls starting at index {args.process}')
        process_saved_urls(args.process)
    else:
        ls.get_recent_disclosures()




# Main
if __name__ == "__main__":
    parse_arguments()

