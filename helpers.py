import os
import time
import logging
import pymysql
import datetime
import pandas as pd
import configparser
import warnings

# Define constants
CONFIG_FILE = 'config.ini'

# Read config-file
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

# Access telegram settings from config file
bot_token = config['telegram']['bot_token']
channel = int(config['telegram']['channel'])
user = int(config['telegram']['user'])

# Establish db connection
def establish_db_connection() -> pymysql.Connection:
    while True:
        try:
            db_connection = pymysql.connect(host   = config['database']['host'],
                                            db     = config['database']['name'],
                                            port   = int(config['database']['port']),
                                            user   = config['database']['user'],
                                            passwd = config['database']['password']
                                            )
            logging.info('Database connection established.')
            return db_connection
        except Exception as e:
            logging.error('Database connection failed. Reconnection... Error: {e}')
            time.sleep(60*3)

# Get specified table from database
def get_table(table_name:str, connection) -> pd.DataFrame:
    query = f"SELECT * FROM {table_name}"
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UserWarning)
        df = pd.read_sql_query(query, con=connection)
    return df

# Get a list of accounts from the 'dbt_stats_report' table from database
def get_accounts(connection) -> list[str] :
    query = f"SELECT id_key FROM dbt_stats_report"
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UserWarning)    
        df = pd.read_sql_query(query, con=connection)
    return df['id_key'].tolist()

# Calculate the last trading date based on the current day of the week for correct .xlsx-file name
def get_last_trading_date(offset:int=1) -> str:
    today = datetime.date.today()

    if today.isoweekday() == 1:
        # Adjust offset for Monday to select Friday's date
        offset = 3
    elif today.isoweekday() == 7:
        # Adjust offset for Sunday to select Friday's date
        offset = 2

    last_trading_date = today - datetime.timedelta(days=offset)
    return last_trading_date.strftime("%Y-%m-%d")

# Set columns width based on maximum length of cell value
def set_column_width(writer:pd.ExcelWriter, sheet_name:str, df:pd.DataFrame):
    worksheet = writer.sheets[sheet_name]
    for i, col in enumerate(df.columns):
        column_width = max(df[col].astype(str).str.len().max(), len(col)) + 1
        worksheet.set_column(i, i, column_width)

# Split table with timeseries to the required format
def split_equities(df:pd.DataFrame) -> pd.DataFrame:
    df = df[~((df['trade_account'] == 'all') & (df['strategy'] != 'all'))]
    df = pd.pivot_table(df, values='equity', index='date', columns='trade_account')
    df.reset_index(drop=False, inplace=True)
    return df

# Generate .xlsx report file
def create_report():
    db_connection = establish_db_connection()

    while True:
        try:
            # Create result folder if it doesn't exist
            result_folder = config['folders']['result_folder']
            if not os.path.exists(result_folder): os.makedirs(result_folder)

             # Generate report file name based on the last trading date and create Excel writer object
            report_file = f"{result_folder}{get_last_trading_date()}_report.xlsx"
            writer = pd.ExcelWriter(report_file, engine='xlsxwriter')

            # Iterate over each trade account and create separate worksheet for each
            for account in get_accounts(db_connection):
                df = get_table(f'report_{account.lower()}', db_connection)
                sheet_name = account.upper()
                df.to_excel(writer, sheet_name=sheet_name, index=False)

                # Set column width
                set_column_width(writer, sheet_name, df)
            
            # Iterate over each required table and create separate worksheet for each
            for table in ['total_report', 'stats', 'tickers', 'equity']:
                df = get_table(table, db_connection)

                # Set sheet name based on table name
                if table == 'total_report':
                    sheet_name = 'SI'
                else:
                    sheet_name = table.upper()

                # If table name is 'equity', split it to required format before writing to Excel
                if table == 'equity':
                    df = split_equities(df)

                df.to_excel(writer, sheet_name=sheet_name, index=False)

                # Set column width
                set_column_width(writer, sheet_name, df)

            writer.close()
            report = open(report_file, 'rb')
            db_connection.close()
            logging.info('Database connection closed.')

            # Return the report file as a binary object
            return report
        
        except Exception as e:
            logging.error(f"Error generating report: {type(e).__name__}: {e}. Retrying...")
            time.sleep(60)