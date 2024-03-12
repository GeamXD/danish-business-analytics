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
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
        
        # Fill missing values for Nans
        merged_data.fillna(0, inplace=True)

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

    def find_low_debt_companies(self, data):
        # Ensure the columns exist and are of the correct type
        if 'debt_obligations' in data.columns and 'equity' in data.columns:
            data['debt_obligations'] = data['debt_obligations'].astype(float)
            data['equity'] = data['equity'].astype(float)
            
            # Calculate the debt-to-equity ratio
            data['debt_to_equity'] = data['debt_obligations'] / data['equity']

            # Identify companies with low debt-to-equity ratio
            low_debt_companies = data[data['debt_to_equity'] < 0.4]['cvr'].unique()
            return low_debt_companies
        else:
            return "Required columns not found in the data"
    
    def analyze_companies(self, data, analysis_choices):
        results = []

        if 'low_debt' in analysis_choices:
            low_debt_companies = self.find_low_debt_companies(data)
            results.append(set(low_debt_companies))

        if 'declining' in analysis_choices:
            decline_companies = self.find_declining_companies(data)
            results.append(set(decline_companies))

        if 'profitable' in analysis_choices:
            profitable_companies = self.find_profitable_companies(data)
            results.append(set(profitable_companies))

        if results:
            final_companies = set.intersection(*results)
        else:
            final_companies = set()

        return final_companies
    
    def compare_companies_profit(self, cvrs, data):
        if len(cvrs) != 2:
            return "Please provide exactly two CVRs for comparison."

        merged_data = data  # Assuming merged_data contains the necessary info

        # Create a subplot with 1 row and 2 columns
        fig = make_subplots(rows=1, cols=2, subplot_titles=[f"CVR: {cvrs[0]}", f"CVR: {cvrs[1]}"])

        for i, cvr in enumerate(cvrs, start=1):
            company_data = merged_data[merged_data['cvr'] == cvr]

            # Create a line plot for each company
            fig.add_trace(
                go.Scatter(x=company_data['publication_date'], y=company_data['profit_loss'], mode='lines', name=f'CVR {cvr}'),
                row=1, col=i
            )

        # Update xaxis and yaxis properties
        fig.update_xaxes(title_text='Year', row=1, col=1)
        fig.update_xaxes(title_text='Year', row=1, col=2)
        fig.update_yaxes(title_text='Profit/Loss', row=1, col=1)
        fig.update_yaxes(title_text='Profit/Loss', row=1, col=2)

        # Update layout properties
        fig.update_layout(height=600, width=1200, title_text="Profit/Loss Trend Comparison")

        return fig
    
    
    def compare_company_metric(self, data, cvrs, metric):
        if len(cvrs) != 2:
            return "Please provide exactly two CVRs for comparison."

        fig = go.Figure()

        for cvr in cvrs:
            company_data = data[data['cvr'] == cvr]
            company_data.fillna(0, inplace=True)

            # Add trace for each company
            fig.add_trace(
                go.Scatter(x=company_data['publication_date'], y=company_data[metric], mode='lines', name=f'CVR {cvr}')
            )

        # Update plot layout
        fig.update_layout(
            title=f"{metric.capitalize()} Trend Comparison",
            xaxis_title='Publication Date',
            yaxis_title=metric.capitalize(),
            height=500,
            width=800
        )

        return fig

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
    
    
    def compare_roa(self, data, cvrs):
        if len(cvrs) != 2:
            return "Please provide exactly two CVRs for comparison."

        # Calculate industry averages for ROA
        industry_roa = data.groupby('industry_code')['return_on_assets'].mean()

        # Create a subplot with 1 row and 2 columns
        fig = make_subplots(rows=1, cols=2, subplot_titles=[f"CVR: {cvrs[0]}", f"CVR: {cvrs[1]}"])

        for i, cvr in enumerate(cvrs, start=1):
            company_data = data[data['cvr'] == cvr]
            if not company_data.empty:
                industry_code = company_data['industry_code'].iloc[0]
                avg_roa = industry_roa[industry_code]

                # Add a bar plot for the company's ROA
                fig.add_trace(
                    go.Bar(x=company_data['year'], y=company_data['return_on_assets'], name=f'CVR {cvr} - ROA'),
                    row=1, col=i
                )

                # Add a line for the industry average ROA
                fig.add_trace(
                    go.Scatter(x=company_data['year'], y=[avg_roa]*len(company_data), mode='lines', name='Industry Average', line=dict(color='red', dash='dash')),
                    row=1, col=i
                )

        # Update layout properties
        fig.update_layout(height=600, width=1200, title_text="Return on Assets Comparison", showlegend=True)
        fig.update_xaxes(title_text='Year')
        fig.update_yaxes(title_text='ROA')

        return fig
    
    def compare_current_ratio_single_plot(self, data, cvrs):
        if len(cvrs) != 2:
            return "Please provide exactly two CVRs for comparison."

        fig = go.Figure()

        for cvr in cvrs:
            company_data = data[data['cvr'] == cvr]

            # Create a line plot for each company's current ratio
            fig.add_trace(
                go.Scatter(x=company_data['publication_date'], y=company_data['current_ratio'], mode='lines', name=f'CVR {cvr}')
            )

        # Update layout properties
        fig.update_layout(
            title="Current Ratio Comparison",
            xaxis_title='Publication Date',
            yaxis_title='Current Ratio',
            height=600,
            width=800
        )

        return fig

    def compare_current_ratio(self, data, cvrs):
        if len(cvrs) != 2:
            return "Please provide exactly two CVRs for comparison."

        # Create a subplot with 1 row and 2 columns
        fig = make_subplots(rows=1, cols=2, subplot_titles=[f"CVR: {cvrs[0]}", f"CVR: {cvrs[1]}"])

        for i, cvr in enumerate(cvrs, start=1):
            company_data = data[data['cvr'] == cvr]

            # Create a line plot for each company's current ratio
            fig.add_trace(
                go.Scatter(x=company_data['publication_date'], y=company_data['current_ratio'], mode='lines', name=f'CVR {cvr}'),
                row=1, col=i
            )

        # Update xaxis and yaxis properties
        fig.update_xaxes(title_text='Publication Date', row=1, col=1)
        fig.update_xaxes(title_text='Publication Date', row=1, col=2)
        fig.update_yaxes(title_text='Current Ratio', row=1, col=1)
        fig.update_yaxes(title_text='Current Ratio', row=1, col=2)

        # Update layout properties
        fig.update_layout(height=600, width=1200, title_text="Current Ratio Comparison")

        return fig
    

    def compare_solvency_ratio_side_by_side(self, data, cvrs):
        if len(cvrs) != 2:
            return "Please provide exactly two CVRs for comparison."

        fig = make_subplots(rows=1, cols=2, subplot_titles=[f"CVR: {cvrs[0]}", f"CVR: {cvrs[1]}"])

        for i, cvr in enumerate(cvrs, start=1):
            company_data = data[data['cvr'] == cvr]

            fig.add_trace(
                go.Scatter(x=company_data['publication_date'], y=company_data['solvency_ratio'], mode='lines', name=f'CVR {cvr}'),
                row=1, col=i
            )

            fig.add_hline(y=1, line_dash="dash", line_color="red", row=1, col=i)

        fig.update_layout(height=600, width=1200, title_text="Solvency Ratio Comparison")
        return fig


    def compare_solvency_ratio_combined(self, data, cvrs):
        if len(cvrs) != 2:
            return "Please provide exactly two CVRs for comparison."

        fig = go.Figure()

        for cvr in cvrs:
            company_data = data[data['cvr'] == cvr]

            fig.add_trace(
                go.Scatter(x=company_data['publication_date'], y=company_data['solvency_ratio'], mode='lines', name=f'CVR {cvr}')
            )

        fig.add_hline(y=1, line_dash="dash", line_color="red")
        fig.update_layout(title="Combined Solvency Ratio Trend", xaxis_title='Publication Date', yaxis_title='Solvency Ratio', height=600, width=800)
        return fig


    def compare_revenue_profit_loss(self, data, cvrs):
        if len(cvrs) != 2:
            return "Please provide exactly two CVRs for comparison."

        fig = make_subplots(rows=1, cols=2, subplot_titles=[f"Revenue vs. Profit/Loss for CVR: {cvrs[0]}", 
                                                            f"Revenue vs. Profit/Loss for CVR: {cvrs[1]}"])


        for i, cvr in enumerate(cvrs, start=1):
            company_data = data[data['cvr'] == cvr]
            company_data.fillna(0, inplace=True)
            # Add Revenue trace
            fig.add_trace(
                go.Scatter(x=company_data['publication_date'], y=company_data['revenue'], mode='lines', name=f'CVR {cvr} - Revenue', line=dict(color='blue')),
                row=1, col=i
            )

            # Add Profit/Loss trace
            fig.add_trace(
                go.Scatter(x=company_data['publication_date'], y=company_data['profit_loss'], mode='lines', name=f'CVR {cvr} - Profit/Loss', line=dict(color='green')),
                row=1, col=i
            )

        fig.update_layout(height=600, width=1200, title_text="Comparison of Revenue vs. Profit/Loss")
        fig.update_xaxes(title_text='Publication Date')
        fig.update_yaxes(title_text='Amount')
        return fig
    
    def compare_total_employee_count(self, data, cvrs, year=None):
        if len(cvrs) != 2:
            return "Please provide exactly two CVRs for comparison."

        # Filter data by the specified year if provided
        if year is not None:
            data = data[data['year'] == year]

        # Calculate total employee counts
        mean_counts = data.groupby('cvr')['employee_count'].sum().reset_index()

        # Filter the data for the specified CVRs
        filtered_data = mean_counts[mean_counts['cvr'].isin(cvrs)]

        # Create the bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=filtered_data['cvr'],
                y=filtered_data['employee_count'],
                marker_color=['blue', 'green']  # Custom colors for each bar
            )
        ])

        # Update layout
        fig.update_layout(
            title='Total Employee Count Comparison' + (f' in {year}' if year is not None else ''),
            xaxis_title='CVR',
            yaxis_title='Average Employee Count',
            height=500,
            width=800
        )

        return fig


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
