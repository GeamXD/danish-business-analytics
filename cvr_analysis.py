# IMPORT LIBRARIES
import gdown
import sqlite3
import pandas as pd
import plotly.express as px
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from matplotlib import style
style.use('ggplot')
sns.set_style("whitegrid")
sns.set_palette('colorblind')

# Suppress all warnings
# warnings.filterwarnings("ignore")

class CvrBusiness:
    
    def __init__(self, filepath='cvr.db'):
        self.filepath = filepath

    def check_file_exists(self):
        # File ID from google drive
        id = "1ViJNZGAqN4DmFIN5f_HtRAYrA0jeMuSw"
        output = self.filepath

        # Check if the file exists
        if os.path.exists(self.filepath):
            return f"{output} exists"
        else:
            # downloads database from google drive
            gdown.download(id=id, output=output, quiet=True)
            return f"{output} Downloaded"

    def db_to_pandas(self):
        # Downloads the data
        self.check_file_exists()

        # Connects to DB
        conn = sqlite3.connect(self.filepath)
        
        # Table names present in database
        table_names = ['financials', 'observations', 'company']
        
        # Empty dictionary
        df_collection = {}
        
        # Iterate through tables in db
        for table in table_names:
            # Creates dictionary with table name as key and data as value
            df = pd.read_sql_query(f'SELECT * FROM {table}', conn)
            df_collection[table] = df

        conn.close()
        # returns collection
        return df_collection

    def merge_tables(self):
        data = self.db_to_pandas()
        df_financials = data['financials']
        df_observations = data['observations']
        df_company = data['company']
        
        # Data Cleaning and Type conversion
        df_financials['cvr'] = df_financials['cvr'].astype(str)
        df_company['cvr_number'] = df_company['cvr_number'].astype(str)
        df_financials['publication_date'] = pd.to_datetime(df_financials['publication_date'], errors='coerce')

        # Merge DataFrames
        merged_data = df_financials.merge(df_observations, on='cvr').merge(df_company, left_on='cvr', right_on='cvr_number')
        
        return merged_data
    
    def find_profitable_companies(self, merged_data):
        # Ensure correct data types
        merged_data['cvr'] = merged_data['cvr'].astype(str)
        merged_data['year'] = merged_data['year'].astype(int)
        merged_data['profit_loss'] = merged_data['profit_loss'].astype(float)

        # Calculate the number of profitable years for each company
        profit_years = merged_data.groupby(['cvr', 'year'])['profit_loss'].apply(lambda x: (x > 0).sum()).reset_index()

        # Summarize the total number of profitable years by company
        profit_years = profit_years.groupby('cvr')['profit_loss'].apply(lambda x: (x > 0).sum()).sort_values(ascending=False)

        # Identify companies with five or more years of profit
        five_yr_or_more_profit_companies = profit_years[profit_years >= 5].index.tolist()

        return five_yr_or_more_profit_companies

    def find_declining_companies(self, merged_data, start_year=8, end_year=2):
        filtered_data = merged_data.sort_values(by='publication_date')
        decline_companies = []

        # Iterate through each group
        for cvr, group in filtered_data.groupby('cvr'):
            if len(group) >= abs(start_year):
                period_profit = group.iloc[start_year:end_year]['profit_loss'].sum()
                year_before_period_profit = group.iloc[start_year-1:start_year]['profit_loss'].sum()
                if period_profit < 0 and year_before_period_profit > 0:
                    decline_companies.append(cvr)

        return decline_companies
        
    def use_case_filter_for_multiple(self):
        pass


    @staticmethod
    def missing_data(data):
        total = data.isnull().sum()
        percent = (data.isnull().sum() / data.isnull().count() * 100)
        tt = pd.concat([total, percent], axis=1, keys=['Total', 'Percent'])
        types = []
        for col in data.columns:
            dtype = str(data[col].dtype)
            types.append(dtype)
        tt['types'] = types
        return np.transpose(tt)

    @staticmethod
    def unique_values(data):
        total = data.count()
        tt = pd.DataFrame(total)
        tt.columns = ['Total']
        uniques = []
        for col in data.columns:
            unique = data[col].nunique()
            uniques.append(unique) 
        tt['Uniques'] = uniques
        return np.transpose(tt)



#usage
cvr_business = CvrBusiness()
merged_data = cvr_business.merge_tables()
print(merged_data.head())

# To check for missing data
missing = CvrBusiness.missing_data(merged_data)
print(missing)

# To check for unique values
unique_vals = CvrBusiness.unique_values(merged_data)
print(unique_vals)
