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
        Write a business overview in this format for the text below.
        
        Name of Business
        ----------------------
        
        
        Services/What they Offer
        -------------------------
        
        
        Other Essential Details
        -----------------------
        
        Note: You must maintain consistent structure. Return output as a markdown.
        text: {description}
    """

    # generate response
    output = together.Complete.create(
        prompt=prompt_1,
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        max_tokens=512,
        temperature=0.5,
    )

    # parse the completion then print the whole output
    generatedText = output['output']['choices'][0]['text']

    return generatedText
