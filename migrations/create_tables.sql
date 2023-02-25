DROP TABLE IF EXISTS headers;
DROP TABLE IF EXISTS lobbying_activity;
DROP TABLE IF EXISTS pre_2016_lobbying_activity;
DROP TABLE IF EXISTS pre_2010_lobbying_activity;
DROP TABLE IF EXISTS campaign_contributions;
DROP TABLE IF EXISTS client_compensation;
DROP TABLE IF EXISTS salaries;
DROP TABLE IF EXISTS operating_expenses;
DROP TABLE IF EXISTS met_expenses;
DROP TABLE IF EXISTS additional_expenses;

CREATE TABLE IF NOT EXISTS headers (
  header_id INTEGER UNIQUE,
  source_name VARCHAR(255),
  date_range VARCHAR(50),
  source_type VARCHAR(8),
  authorizing_officer_or_lobbyist_name VARCHAR(255),
  agent_type_or_title VARCHAR(255),
  business_name VARCHAR(255),
  address VARCHAR(255),
  city_state_zip_code VARCHAR(255),
  country VARCHAR(255),
  phone VARCHAR(50),
  url VARCHAR(150),
  PRIMARY KEY(url)
);

CREATE TABLE IF NOT EXISTS pre_2016_lobbying_activity (
  header_id INTEGER,
  activity_or_bill_no_and_title TEXT,
  lobbyist_name varchar(255),
  agent_position VARCHAR(255),
  direct_business_association TEXT,
  client_name VARCHAR(255),
  compensation_received VARCHAR(255)

);

CREATE TABLE IF NOT EXISTS pre_2010_lobbying_activity (
  header_id INTEGER,
  date VARCHAR(50),
  activity_or_bill_no_and_title TEXT,
  lobbyist_name VARCHAR(255),
  client_name VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS lobbying_activity (
  header_id INTEGER,
  lobbyist_name varchar(255),
  client_name varchar(255),
  house_or_senate VARCHAR(255),
  bill_number_or_agency_name VARCHAR(255),
  bill_title_or_activity TEXT,
  agent_position VARCHAR(255),
  compensation_received VARCHAR(255),
  direct_business_association TEXT
);

CREATE TABLE IF NOT EXISTS campaign_contributions (
  header_id INTEGER,
  date VARCHAR(50),
  recipient_name VARCHAR(255),
  lobbyist_name VARCHAR(255),
  office_sought VARCHAR(255),
  amount VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS client_compensation (
  header_id INTEGER,
  client_name VARCHAR(255),
  amount VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS salaries (
  header_id INTEGER,
  lobbyist_name VARCHAR(255),
  salary VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS operating_expenses (
  header_id INTEGER,
  date varchar(50),
  recipient VARCHAR(255),
  type_of_expense VARCHAR(255),
  amount varchar(20)
);

CREATE TABLE IF NOT EXISTS met_expenses (
  header_id INTEGER,
  date VARCHAR(50),
  lobbyist_name VARCHAR(255),
  event_type VARCHAR(255),
  payee VARCHAR(255),
  attendees VARCHAR(255),
  amount VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS additional_expenses (
  header_id INTEGER,
  date_from VARCHAR(20),
  date_to VARCHAR(20),
  lobbyist_name VARCHAR(255),
  recipient_name VARCHAR(255),
  expense VARCHAR(255),
  amount VARCHAR(20)
);
