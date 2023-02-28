from types import SimpleNamespace
from bs4 import BeautifulSoup as bs
import psycopg2.extras as extras
import src.settings as settings

import psycopg2, requests, logging

#####
# PageFactory:
#   Takes a url. Verifies that it points to a data page. If not, returns a BlankPage. If so, returns a DataPage
######

class PageFactory:
    def __new__(cls, url):

        if not url:
            logging.exception("PageFactory requires a url")
            return BlankPage()
        logging.debug(f'Pulling data from URL: {url}')
        html = PageFactory.pull_html(url)
        soup = bs(html, 'html.parser')

        if PageFactory.check_validity(soup, url):
            return DataPage(soup, url)
        else:
            return BlankPage()

    def pull_html(url):
        headers={"User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"}
        result = requests.get(url, headers=headers)
        result.raise_for_status()
        return result.content

    def check_validity(soup, url):
        if soup.h1 and soup.h1.text == 'An Error Occurred':
            logging.warning("Disclosure Report Not Found")
            if url:
                logging.warning(f"URL: {url}")
            return False
        return True

#####
# BlankPage:
#   Just an empty placeholder class, here so I have something to return from PageFactory that implements save()
#####

class BlankPage:
    def save(self):
        return

#####
# DataPage:
#   Represents the data from one disclosure page.
#   Automatically extracts relevant tables
#   Can save tables to postgres
######

class DataPage:
    columns_dict =  {'campaign_contributions':
                        ['Date','lobbyist_name','Recipient name','Office Sought','Amount'],
                    'client_compensation':
                        ['Client name','Amount'],
                    'lobbying_activity':
                        ['Lobbyist name','Client name','House / Senate','Bill Number or Agency Name','Bill title or activity','Agent position','Compensation received','Direct business association'],
                    'pre_2016_lobbying_activity':
                        ['Activity or Bill No and Title','Lobbyist name','Agent position','Direct business association','Client name','Compensation received'],
                    'pre_2010_lobbying_activity':
                        ['Date','Activity or bill No and Title','Lobbyist name','Client name'],
                    'headers':
                        ['source_name','source_type','date_range','authorizing_officer_or_lobbyist_name','agent_type_or_title','business_name','address','city_state_zip_code','country', 'phone', 'url'],
                    'salaries':
                        ['lobbyist_name','salary'],
                    'operating_expenses':
                        ['date','recipient','type_of_expense','amount'],
                    'met_expenses':
                        ['date','lobbyist_name','event_type','payee','attendees','amount'],
                    'pre_2016_met_expenses':
                        ['date','lobbyist_name','event_type','payee','attendees','addresses','amount'],
                    'additional_expenses':
                        ['date_from','date_to','lobbyist_name','recipient_name','expense','amount'],
                    'all':
                        ['header_id']}

    def __init__(self, soup, url = None):
        self.soup = soup
        self.url = url
        self.type = 'Entity' if 'Lobbyist Entity' in soup.text else 'Lobbyist'
        self.date_range = soup.find('span', id = lambda tag: tag and tag.startswith("ContentPlaceHolder1_lblYear")).text
        self.year = int(self.date_range[-4:])
        self.header = self.get_header_table() # Header table has info that we will need later for other tables
        self.tables = self.get_all_tables()
        self.verify_row_lengths()
        logging.info(f"Pulled tables {', '.join([table for table in self.tables.__dict__.keys() if self.tables.__dict__[table]])} from {self.source_name} {self.date_range}")


    ####################
    # Table Extraction #
    ####################

    def get_all_tables(self):
        tables = SimpleNamespace()

        # For activity tables, we have to figure out which kind we are dealing with
        if 'DateActivity or Bill No and Title' in self.soup.text:
            tables.pre_2010_lobbying_activity = self.get_generic_table('grdvActivities', drop_last_row = False)
            tables.pre_2010_lobbying_activity = self.add_lobbyist_name(tables.pre_2010_lobbying_activity, -1)
        if "Agent's positionDirect business association with public officialClient representedCompensation received" in self.soup.text:
            tables.pre_2016_lobbying_activity = self.get_generic_table('grdvActivities', drop_last_row = False)
            tables.pre_2016_lobbying_activity = self.add_lobbyist_name(tables.pre_2016_lobbying_activity, 1)
        elif "House / SenateBill Number or Agency Name" in self.soup.text:
            tables.lobbying_activity = self.get_lobbying_activity()

        # MOSTLY a consistent table, except that the individual lobbyist verison doesn't include the lobbyist name
        tables.campaign_contributions = self.get_generic_table("CampaignContribution")
        tables.campaign_contributions = self.add_lobbyist_name(tables.campaign_contributions, 1)
        if "Event typeEvent locationNames of all event participantsAddresses of all event participantsAmount" in self.soup.text:
            tables.pre_2016_met_expenses = self.get_generic_table("METExpenses")
            tables.pre_2016_met_expenses = self.add_lobbyist_name(tables.pre_2016_met_expenses, 1)
        else:
            tables.met_expenses = self.get_generic_table("METExpenses")
            tables.met_expenses = self.add_lobbyist_name(tables.met_expenses, 1)

        # Very consistent tables
        tables.client_compensation = self.get_generic_table("ClientPaidToEntity")
        tables.salaries = self.get_generic_table('SalaryPaid')
        tables.operating_expenses = self.get_generic_table("OperatingExpenses")
        tables.additional_expenses = self.get_generic_table("AdditionalExpenses")
        tables.additional_expenses = self.add_lobbyist_name(tables.additional_expenses, 2)
        return tables

    def add_lobbyist_name(self, table, index):
        if self.type == 'Lobbyist':
            for row in table:
                row.insert(index, self.source_name)
        return table

    def get_header_table(self):
        header_table = self.soup.find('div',id=lambda tag: tag and tag.startswith("ContentPlaceHolder1_pnl"))
        rows = header_table.findAll('tr')
        row_list = []
        for row in rows[:-1]: #last row is always blank
            cell = " ".join([result.text for result in row.findAll('span', id=lambda tag: tag and "RegistrationInfoReview1_lbl" in tag)])
            row_list.append(cell)
        if self.type == 'Lobbyist':
            row_list.insert(1, row_list.pop(5)) # Move the 'Agent Type' table to match up with the 'Position' index for entites
            self.source_name = row_list[0]
        else:
            self.source_name = row_list[2]
        row_list = [self.source_name, self.type, self.date_range] + row_list
        row_list.append(self.url)
        return row_list

    # pulls a table with an id tag like %table_tag_includes%
    def get_generic_table(self, table_tag_includes, drop_last_row = True):
        table_list = []
        tables = self.soup.findAll('table', id = lambda tag: tag and table_tag_includes in tag)
        for table in tables:
            rows = table.findAll('tr', class_=lambda tag: tag and 'Grid' in tag and 'Header' not in tag)
            if drop_last_row: rows = rows[:-1]
            for row in rows: #last row is total
                table_list.append(self.process_row(row))
        return table_list

    # extracts and cleans a row from a table
    def process_row(self, row, starting_list = None):
        row_list = starting_list if starting_list else []
        cells = row.findAll('td')
        if cells:
            for cell in cells:
                row_list.append(cell.text.strip().replace('\n', '; '))
        return row_list

    # There are currently 3 breeds of activity table in the zoo:
    def get_lobbying_activity(self):
        table_text = "lblLobbyistName" if self.type == 'Entity' else "lblClientName"
        full_tables = self.soup.findAll('span',id = lambda tag: tag and table_text in tag)
        table_list = []
        for full_table in full_tables:
            lobbyist_name, client_name = self.assign_lobbyist_and_client_names(full_table)
            table = full_table.findNext('table').findNext('table')
            rows = table.findAll('tr', class_=lambda tag: tag and 'Grid' in tag and 'Header' not in tag)
            if 'No activities were disclosed for this reporting period.' not in rows:
                for row in rows:
                    table_list.append(self.process_row(row, [lobbyist_name, client_name]))
        return table_list

    # Helper function for modern lobbying activity tables
    def assign_lobbyist_and_client_names(self, full_table):
        if self.type == 'Entity':
            return (full_table.text.replace('Lobbyist: ',""), full_table.findNext('span').text)
        else:
            return (self.header[0], full_table.text)

    def verify_row_lengths(self):
        for table in self.tables.__dict__:
            if self.tables.__dict__[table]:
                for i, row in enumerate(self.tables.__dict__[table]):
                    if len(row) != len(self.columns_dict[table]):
                        logging.warning(f"Invalid row length in table {table}. Removing row.")
                        del self.tables.__dict__[table][i]

    ################
    # Save Methods #
    ################

    def save(self, params_dict = settings.psql_params_dict):
        with  psycopg2.connect(**params_dict) as conn:
            header_id = self.get_header_id(conn)
            if self.write_header_to_psql(conn, header_id):
                for table_name in self.tables.__dict__.keys():
                    self.write_table_to_psql(table_name, conn, header_id)

    def write_header_to_psql(self, conn, header_id):
        table = [tuple(row) for row in [[str(header_id)]+self.header]]
        return self.execute_insert_table_query('headers', table, conn)

    def write_table_to_psql(self, table_name, conn, header_id):
        table_list = self.tables.__dict__[table_name].copy()

        if not table_list: return True #If the table is empty let's not waste any time

        table = [tuple([str(header_id)]+row) for row in table_list]
        return self.execute_insert_table_query(table_name, table, conn)

    def get_header_id(self, conn):
        with conn.cursor() as cursor:
            query = 'select MAX(header_id) from headers;'
            cursor.execute(query)
            response = cursor.fetchone()[0]
            header_id = response + 1 if response else 1
        return header_id

    #returns true if all rows of the table are uploaded to the database or if table is empty
    #returns false if any errors occur
    def execute_insert_table_query(self, table_name, table, conn):
        columns = DataPage.columns_dict['all'] + DataPage.columns_dict[table_name]
        cols = ','.join([col.lower().replace(",","").replace(" ","_").replace('/','or') for col in columns])
        query = "INSERT INTO %s(%s) VALUES %%s" % (table_name, cols)

        with conn.cursor() as cursor:
            try:
                extras.execute_values(cursor, query, table)
                conn.commit()
                logging.debug(f"Data successfully inserted into table '{table_name}'")
                return True

            except (Exception, psycopg2.DatabaseError) as error:
                logging.warning(f"Error: {error} On table {table_name}")
                conn.rollback()
                cursor.close()
                return False
