# Import necessary libraries
import gdown
import sqlite3
import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")  # Ignore warnings for cleaner output

class CvrBusiness:
    """
    A class to handle various business analytics operations for CVR (Central Business Register) data.
    """
    
    def __init__(self, filepath='cvr.db'):
        """
        Initializes the CvrBusiness class with a specified SQLite database file path.
        :param filepath: str, path to the SQLite database file (default is 'cvr.db')
        """
        self.filepath = filepath

    def check_file_exists(self):
        """
        Checks if the database file exists locally. If not, downloads it from Google Drive.
        """
        # File ID from Google Drive
        id = "1ViJNZGAqN4DmFIN5f_HtRAYrA0jeMuSw"
        output = self.filepath

        if os.path.exists(self.filepath):
            return f"{output} exists"
        else:
            # Download the database from Google Drive if not present
            gdown.download(id=id, output=output, quiet=True)
            return f"{output} Downloaded"

    def db_to_pandas(self):
        """
        Downloads the SQLite database file if not present and loads its tables into Pandas DataFrames.
        :return: dict of DataFrames, keys are table names and values are the corresponding DataFrames
        """
        self.check_file_exists()

        # Connect to the SQLite database
        conn = sqlite3.connect(self.filepath)
        
        # List of table names in the database
        table_names = ['financials', 'observations', 'company']
        
        # Dictionary to store DataFrames
        df_collection = {}
        
        # Loop through each table and load its data into a DataFrame
        for table in table_names:
            df = pd.read_sql_query(f'SELECT * FROM {table}', conn)
            df_collection[table] = df

        # Close the database connection
        conn.close()
        return df_collection

    def merge_tables(self):
        """
        Merges different tables (financials, observations, company) into a single DataFrame.
        :return: DataFrame, merged data from the financials, observations, and company tables
        """
        data = self.db_to_pandas()
        # Extract data for each table
        df_financials = data['financials']
        df_observations = data['observations']
        df_company = data['company']
        
        # Data cleaning and type conversion
        df_financials['cvr'] = df_financials['cvr'].astype(str)
        df_company['cvr_number'] = df_company['cvr_number'].astype(str)
        df_financials['publication_date'] = pd.to_datetime(df_financials['publication_date'], errors='coerce')

        # Merge the DataFrames on the 'cvr' column
        merged_data = df_financials.merge(df_observations, on='cvr').merge(df_company, left_on='cvr', right_on='cvr_number')
        
        # Fill missing values with zeros
        merged_data.fillna(0, inplace=True)

        return merged_data

    def find_profitable_companies(self, merged_data):
        """
        Identifies companies with a specified number of profitable years.
        :param merged_data: DataFrame, data merged from financials, observations, and company tables
        :return: list, companies with five or more profitable years
        """
        # Ensure data types are correct
        merged_data['cvr'] = merged_data['cvr'].astype(str)
        merged_data['year'] = merged_data['year'].astype(int)
        merged_data['profit_loss'] = merged_data['profit_loss'].astype(float)

        # Compute profitable years per company
        profit_years = merged_data.groupby(['cvr', 'year'])['profit_loss'].apply(lambda x: (x > 0).sum()).reset_index()

        # Summarize and sort profitable years by company
        profit_years = profit_years.groupby('cvr')['profit_loss'].apply(lambda x: (x > 0).sum()).sort_values(ascending=False)

        # Identify companies with five or more profitable years
        five_yr_or_more_profit_companies = profit_years[profit_years >= 5].index.tolist()

        return five_yr_or_more_profit_companies

    def find_declining_companies(self, merged_data, start_year=8, end_year=2):
        """
        Identifies companies showing a decline in profit/loss over a specified period.

        :param merged_data: DataFrame, data merged from financials, observations, and company tables
        :param start_year: int, the start year index for the declining period (default 8)
        :param end_year: int, the end year index for the declining period (default 2)
        :return: list, companies that show a decline in profit/loss in the specified period
        """
        filtered_data = merged_data.sort_values(by='publication_date')
        decline_companies = []

        # Iterate through each company's data
        for cvr, group in filtered_data.groupby('cvr'):
            # Check for sufficient data length
            if len(group) >= abs(start_year):
                # Calculate profit/loss for specified period
                period_profit = group.iloc[start_year:end_year]['profit_loss'].sum()
                year_before_period_profit = group.iloc[start_year-1:start_year]['profit_loss'].sum()
                
                # Check for decline
                if period_profit < 0 and year_before_period_profit > 0:
                    decline_companies.append(cvr)

        return decline_companies

    def find_low_debt_companies(self, data):
        """
        Identifies companies with a low debt-to-equity ratio.
        :param data: DataFrame, data containing financial information of companies
        :return: list, CVRs of companies with a debt-to-equity ratio less than 0.4
        """
        # Check if necessary columns are present
        if 'debt_obligations' in data.columns and 'equity' in data.columns:
            # Ensure data types are correct
            data['debt_obligations'] = data['debt_obligations'].astype(float)
            data['equity'] = data['equity'].astype(float)
            
            # Calculate the debt-to-equity ratio
            data['debt_to_equity'] = data['debt_obligations'] / data['equity']

            # Filter and identify companies with a low debt-to-equity ratio
            low_debt_companies = data[data['debt_to_equity'] < 0.4]['cvr'].unique()
            return low_debt_companies
        else:
            return "Required columns not found in the data"
