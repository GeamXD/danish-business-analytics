# Benchmark App

## Overview
The Benchmark App is a Streamlit-based web application designed for analyzing and comparing business metrics. This application leverages a SQLite database for user authentication and integrates with other Python modules to perform complex data analysis.

## Features
- User authentication system (login/signup) using SQLite database.
- Various data analysis functions on company financial data, including:
  - Trend analysis (e.g., comparing companies' profits).
  - Cluster analysis
  - Comparative analysis (e.g., comparing return on assets).
  - Financial health indicators (e.g., current ratio, solvency ratio).
  - Correlation analysis between revenue and profit/loss.
  - Benchmarking analysis (e.g., comparing total employee count).
- Dynamic visualization of analysis results.
- Business overview section based on user selection.

## Installation and Setup
To run the app, you'll need Python installed on your system along with the following dependencies:
- Streamlit
- SQLite3
- Pandas
- Matplotlib (for plotting)
- Additional modules as required (e.g., `ai.py`, `cvr_analysis_1.py`).


### Installing Requirements

```bash
    pip install -r requirements.txt
```

### Downloading Database
```bash
    python to_download_db
```

After cloning/downloading the database, navigate to the app directory and run:
```bash
    streamlit run app.py
```

## Usage
Upon launching the app, users are presented with a login/signup page. After successful authentication, users can access various analytical features:
- Enter CVR numbers for comparison.
- Apply different filters and select metrics for analysis.
- Choose different types of plots for visualizing data.
- Use an Ai tool to clean and summarize business data.

## Contributing
Contributions to the Benchmark App are welcome. Please ensure to follow the project's code style and guidelines.

## License
NA