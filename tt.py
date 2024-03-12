cvr_business = CvrBusiness()
merged_data = cvr_business.merge_tables()

# Specify the analyses you want to perform
analysis_choices = ['low_debt', 'declining', 'profitable']  # You can adjust this list as needed

final_companies = cvr_business.analyze_companies(merged_data, analysis_choices)
print(final_companies)
