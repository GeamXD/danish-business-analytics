# Import dotenv
import os
import json
from dotenv import load_dotenv
import together

# load dotenv from environment
load_dotenv()

# loads the api key
together.api_key = os.getenv('TOGETHER_AI_API_KEY')




# Load the JSON data from a file
def load_json():
    filename = 'businessscrapper/business-data/ten_business.json'
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

# Function to get company description by name
def get_company_description(data, company_name):
    for company in data:
        if company['company_name'] == company_name:
            return ' '.join(company['company_desc'])
    return "Company not found"


# write a function that passes description to together ai and returns the result
def get_markdown_description(description):
    # Prompt
    prompt_1 = f"""
        Summarize the text below, into a markdown format.
        Outline the business in this format.
        Business Name in Bold at the top.
        what they offer or what they do with a heading called Services or,
        who they are.
        text: {description}
    """

    #generate response
    output = together.Complete.create(
        prompt=prompt_1,
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        max_tokens = 500,
        temperature = 0.8,
    )
    
    # parse the completion then print the whole output
    generatedText = output['output']['choices'][0]['text']

    return generatedText
