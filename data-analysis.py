# IMPORT LIBRARIES
import gdown
import sqlite3
import pandas as pd
import plotly.express as px
import numpy as np
import os


def check_file_exits(filepath):
    # File ID from google drive
    id = "1ViJNZGAqN4DmFIN5f_HtRAYrA0jeMuSw"
    output = 'cvr.db'

    # Check if the file exists
    if os.path.exists(filepath):
        return f"{output} exists"
    else:
        # downloads database from google drive
        gdown.download(id=id, output=output, quiet=True)
        return f"{output} Downloaded"


def db_to_pandas(filepath):
    # Connects to DB
    conn = sqlite3.connect(filepath)

    # Table names present in database
    table_names = ['financials', 'observations', 'company']

    # Empty dictionary
    df_collection = {}

    # Iterate through tables in db
    for table in table_names:
        # Creates dictionary with table name as key and data as value
        df = pd.read_sql_query(f'SELECT * FROM {table}', conn)
        df_collection[table] = df
    # returns collection
    return df_collection


check_file_exits('./cvr.db')

data = db_to_pandas('./cvr.db')
df_financials = data['financials']
df_observations = data['observations']
df_company = data['company']
del data
df_financials.info()

def missing_data(data):
    total = data.isnull().sum()
    percent = (data.isnull().sum()/ data.isnull().count()*100)
    tt = pd.concat([total, percent], axis=1, keys=['Total', 'Percent'])
    types = []
    for col in data.columns:
        dtype = str(data[col].dtype)
        types.append(dtype)
    tt['types'] = types
    return(np.transpose(tt))

missing_data(df_financials)
