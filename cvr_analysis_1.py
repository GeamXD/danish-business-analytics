# IMPORT LIBRARIES
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import gdown
import sqlite3
import pandas as pd
import numpy as np
import os
# from pandas.api.types import is_datetime64_any_dtype as is_datetime
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from matplotlib import style
sns.set_style("whitegrid")
sns.set_palette('colorblind')
warnings.filterwarnings("ignore")


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
        df_financials['publication_date'] = pd.to_datetime(
            df_financials['publication_date'], format='mixed')

        # Merge DataFrames
        merged_data = df_financials.merge(df_observations, on='cvr').merge(
            df_company, left_on='cvr', right_on='cvr_number')

        # Fill missing values for Nans
        merged_data.fillna(0, inplace=True)

        return merged_data

    def find_profitable_companies(self, merged_data):
        # Ensure correct data types
        merged_data['cvr'] = merged_data['cvr'].astype(str)
        merged_data['year'] = merged_data['year'].astype(int)
        merged_data['profit_loss'] = merged_data['profit_loss'].astype(float)

        # Calculate the number of profitable years for each company
        profit_years = merged_data.groupby(['cvr', 'year'])['profit_loss'].apply(
            lambda x: (x > 0).sum()).reset_index()

        # Summarize the total number of profitable years by company
        profit_years = profit_years.groupby('cvr')['profit_loss'].apply(
            lambda x: (x > 0).sum()).sort_values(ascending=False)

        # Identify companies with five or more years of profit
        five_yr_or_more_profit_companies = profit_years[profit_years >= 5].index.tolist(
        )

        return five_yr_or_more_profit_companies

    def find_declining_companies(self, merged_data, start_year=-10, end_year=-2):

        # # Ensure 'publication_date' is in datetime format
        # if not is_datetime(merged_data['publication_date']):
        #     merged_data['publication_date'] = pd.to_datetime(merged_data['publication_date'], errors='coerce')

        filtered_data = merged_data.sort_values(by='publication_date')
        decline_companies = []

        # Iterate through each group
        for cvr, group in filtered_data.groupby('cvr'):
            if len(group) >= abs(start_year):
                period_profit = group.iloc[start_year:end_year]['profit_loss'].sum(
                )
                year_before_period_profit = group.iloc[start_year -
                                                       1:start_year]['profit_loss'].sum()
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
            low_debt_companies = data[data['debt_to_equity']
                                      < 0.4]['cvr'].unique()
            return low_debt_companies
        else:
            return "Required columns not found in the data"

    def analyze_companies(self, data, analysis_choices):

        if 'low_debt' in analysis_choices and len(analysis_choices) == 1:
            low_debt_companies = self.find_low_debt_companies(data)
            return low_debt_companies
        elif 'declining' in analysis_choices and len(analysis_choices) == 1:
            decline_companies = self.find_declining_companies(data)
            return decline_companies
        elif 'profitable' in analysis_choices and len(analysis_choices) == 1:
            profitable_companies = self.find_profitable_companies(data)
            return profitable_companies
        elif 'low_debt' in analysis_choices and 'declining' in analysis_choices and len(analysis_choices) == 2:
            low_debt_companies = self.find_low_debt_companies(data)
            fil_low = data[data['cvr'].isin(low_debt_companies)]
            decline_companies = self.find_declining_companies(fil_low)
            return set(low_debt_companies) and set(decline_companies)

        elif 'low_debt' in analysis_choices and 'profitable' in analysis_choices and len(analysis_choices) == 2:
            low_debt_companies = self.find_low_debt_companies(data)
            fil_low = data[data['cvr'].isin(low_debt_companies)]
            profitable_companies = self.find_profitable_companies(fil_low)
            return set(low_debt_companies) and set(profitable_companies)

        elif 'profitable' in analysis_choices and 'declining' in analysis_choices and len(analysis_choices) == 2:
            profitable_companies = self.find_profitable_companies(data)
            fil_prof = data[data['cvr'].isin(profitable_companies)]
            decline_companies = self.find_declining_companies(fil_prof)
            return set(profitable_companies) and set(decline_companies)

        elif 'profitable' in analysis_choices and 'declining' in analysis_choices and 'low_debt' in analysis_choices and len(analysis_choices) == 3:
            profitable_companies = self.find_profitable_companies(data)
            filer_prof = data[data['cvr'].isin(profitable_companies)]
            decline_companies = self.find_declining_companies(filer_prof)
            low_debt_companies = self.find_low_debt_companies(filer_prof)
            return set(profitable_companies) & set(decline_companies) & set(low_debt_companies)
        else:
            return 'No choice was made'

    def apply_filter(self, filters_cvrs, data):
        filtered_data = data[data['cvr'].isin(filters_cvrs)]
        return filtered_data

    def compare_companies_profit(self, cvrs, data):
        if len(cvrs) != 2:
            return "Please provide exactly two CVRs for comparison."

        # Filter data for the provided CVRs
        filtered_data = data[data['cvr'].isin(cvrs)]

        # Create a matplotlib figure and axis
        fig, ax = plt.subplots(figsize=(12, 6))

        # Setting the color palette to colorblind
        sns.set_palette('colorblind')

        # Plotting the data using Seaborn on the created axis
        sns.lineplot(ax=ax, data=filtered_data, x='year',
                     y='profit_loss', hue='cvr')

        # Setting plot titles and labels
        ax.set_title('Profit/Loss Trend Comparison')
        ax.set_xlabel('Year')
        ax.set_ylabel('Profit/Loss')

        # Return the figure object
        return fig

    def compare_company_metric(self, data, cvrs, metric='profit_loss'):
        if len(cvrs) != 2:
            return "Please provide exactly two CVRs for comparison."

        # Filter data for the provided CVRs
        filtered_data = data[data['cvr'].isin(cvrs)].fillna(0)

        # Create a matplotlib figure and axis
        fig, ax = plt.subplots(figsize=(8, 5))

        # Plotting the data using Seaborn
        sns.lineplot(ax=ax, data=filtered_data, x='year', y=metric, hue='cvr')

        # Setting plot titles and labels
        ax.set_title(f"{metric.capitalize()} Trend Comparison")
        ax.set_xlabel('Year')
        ax.set_ylabel(metric.capitalize())

        # Return the figure object
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

        # Create a matplotlib figure with subplots
        fig, axes = plt.subplots(1, 2, figsize=(12, 6))

        for i, cvr in enumerate(cvrs):
            company_data = data[data['cvr'] == cvr]
            if not company_data.empty:
                industry_code = company_data['industry_code'].iloc[0]
                avg_roa = industry_roa[industry_code]

                # Plotting the company's ROA
                sns.barplot(ax=axes[i], x='year', y='return_on_assets',
                            data=company_data, label=f'CVR {cvr} - ROA')

                # Plotting the industry average ROA
                axes[i].plot(company_data['year'], [avg_roa]*len(company_data),
                             label='Industry Average', color='red', linestyle='--')

                axes[i].set_title(f"CVR: {cvr}")
                axes[i].set_xlabel('Year')
                axes[i].set_ylabel('ROA')
                axes[i].legend()

        fig.suptitle("Return on Assets Comparison")
        plt.tight_layout()

        return fig

    def compare_current_ratio_single_plot(self, data, cvrs):
        if len(cvrs) != 2:
            return "Please provide exactly two CVRs for comparison."

        # Filter data for the provided CVRs
        filtered_data = data[data['cvr'].isin(cvrs)]

        # Create a matplotlib figure and axis
        fig, ax = plt.subplots(figsize=(8, 6))

        # Plotting the data using Seaborn
        sns.lineplot(ax=ax, data=filtered_data, x='publication_date',
                     y='current_ratio', hue='cvr', style='cvr')

        # Setting plot titles and labels
        ax.set_title('Current Ratio Comparison')
        ax.set_xlabel('Publication Date')
        ax.set_ylabel('Current Ratio')

        # Return the figure object
        return fig

    def compare_current_ratio(self, data, cvrs):
        if len(cvrs) != 2:
            return "Please provide exactly two CVRs for comparison."

        # Create a subplot with 1 row and 2 columns
        fig, axes = plt.subplots(1, 2, figsize=(10, 5))

        for i, cvr in enumerate(cvrs):
            company_data = data[data['cvr'] == cvr]

            # Create a line plot for each company's current ratio
            sns.lineplot(ax=axes[i], x='publication_date',
                         y='current_ratio', data=company_data, label=f'CVR {cvr}')
            axes[i].set_title(f"CVR: {cvr}")
            axes[i].set_xlabel('Publication Date')
            axes[i].set_ylabel('Current Ratio')

        plt.suptitle("Current Ratio Comparison")
        plt.tight_layout()

        return fig

    def compare_solvency_ratio_side_by_side(self, data, cvrs):
        if len(cvrs) != 2:
            return "Please provide exactly two CVRs for comparison."

        # Create a subplot with 1 row and 2 columns
        fig, axes = plt.subplots(1, 2, figsize=(12, 6))

        for i, cvr in enumerate(cvrs):
            company_data = data[data['cvr'] == cvr]

            sns.lineplot(ax=axes[i], x='publication_date',
                         y='solvency_ratio', data=company_data, label=f'CVR {cvr}')
            axes[i].axhline(y=1, linestyle='--', color='red')
            axes[i].set_title(f"CVR: {cvr}")
            axes[i].set_xlabel('Publication Date')
            axes[i].set_ylabel('Solvency Ratio')

        plt.suptitle("Solvency Ratio Comparison")
        plt.tight_layout()

        return fig

    def compare_solvency_ratio_combined(self, data, cvrs):
        if len(cvrs) != 2:
            return "Please provide exactly two CVRs for comparison."

        fig, ax = plt.subplots(figsize=(8, 6))

        for cvr in cvrs:
            company_data = data[data['cvr'] == cvr]

            sns.lineplot(ax=ax, x='publication_date', y='solvency_ratio',
                         data=company_data, label=f'CVR {cvr}')

        ax.axhline(y=1, linestyle='--', color='red')
        ax.set_title('Combined Solvency Ratio Trend')
        ax.set_xlabel('Publication Date')
        ax.set_ylabel('Solvency Ratio')

        plt.tight_layout()
        return fig

    def compare_revenue_profit_loss(self, data, cvrs):
        if len(cvrs) != 2:
            return "Please provide exactly two CVRs for comparison."

        # Create a subplot with 1 row and 2 columns
        fig, axes = plt.subplots(1, 2, figsize=(12, 6))

        for i, cvr in enumerate(cvrs):
            company_data = data[data['cvr'] == cvr]
            company_data.fillna(0, inplace=True)

            # Create first y-axis for Revenue
            sns.lineplot(ax=axes[i], x='publication_date', y='revenue',
                         data=company_data, color='blue', label='Revenue')

            # Create second y-axis for Profit/Loss
            ax2 = axes[i].twinx()
            sns.lineplot(ax=ax2, x='publication_date', y='profit_loss',
                         data=company_data, color='green', label='Profit/Loss')

            axes[i].set_title(f"Revenue vs. Profit/Loss for CVR: {cvr}")
            axes[i].set_xlabel('Publication Date')
            axes[i].set_ylabel('Revenue', color='blue')
            ax2.set_ylabel('Profit/Loss', color='green')

        plt.suptitle("Comparison of Revenue vs. Profit/Loss")
        plt.tight_layout()

        return fig

    def compare_total_employee_count(self, data, cvrs):
        if len(cvrs) != 2:
            return "Please provide exactly two CVRs for comparison."

        # Calculate total employee counts
        mean_counts = data.groupby('cvr')['employee_count'].sum().reset_index()

        # Filter the data for the specified CVRs
        filtered_data = mean_counts[mean_counts['cvr'].isin(cvrs)]

        # Create a figure and axis object
        fig, ax = plt.subplots(figsize=(15, 10))

        # Create the bar chart on the created axis
        sns.barplot(x='cvr', y='employee_count', data=filtered_data, ax=ax)
        # Update layout
        ax.set_title('Total Employee Count Comparison')
        ax.set_xlabel('CVR')
        ax.set_ylabel('Total Employee Count')

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

    @staticmethod
    def check_cvr(cvrs):
        if len(cvrs) != 2:
            return "Please provide exactly two CVRs for comparison."
        else:
            return cvrs


cols_to_drop = ['pdf_url', 'secondary_industry', 'short_description', 'long_description', 'capital_partly', 'establishment_date', 'first_financial_year_start', 'last_loaded', 'email', 'reporting_period_end_date', 'website_url', 'status_valid_to', 'date_of_approval_of_annual_report', 'status_valid_from', 'description', 'name',
                'capital_currency', 'auditor_reprimand', 'responsible_data_providers', 'industry_text', 'purpose', 'effective_date', 'industry_sector', 'company_binding', 'effective_actor', 'financial_year_start', 'last_updated', 'first_financial_year_end', 'title', 'current_revision', 'alt_names', 'unit_type', 'phone_number', 'financial_year_end', 'reporting_period_start_date']
