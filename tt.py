cvr_business = CvrBusiness()
merged_data = cvr_business.merge_tables()

# Specify the analyses you want to perform
analysis_choices = ['low_debt', 'declining', 'profitable']  # You can adjust this list as needed

final_companies = cvr_business.analyze_companies(merged_data, analysis_choices)
print(final_companies)

['compare companies profit' # trend
, 'compare company metric' # trend
, 'compare roa' # comparison analysis
, 'compare current ratio (single plot)' # financial health indicators
, 'compare current ratio'  # financial health indicators
, 'compare solvency ratio side_by_side'  # financial health indicators
, 'compare solvency ratio combined'  # financial health indicators
,'compare revenue profit_loss' # Correlation analysis
,'compare total employee count'] # Benchmarking Analysis

['compare current ratio (single plot)', 'compare current ratio', 'compare solvency ratio side_by_side', 'compare solvency ratio combined']