# Import dotenv
import os
import json
from dotenv import load_dotenv
import together
import streamlit as st

# load dotenv from environment
load_dotenv()

# loads the api key
together.api_key = os.getenv('TOGETHER_AI_API_KEY')



with open('businessscrapper/business-data/ten_business.json', 'r') as file:
    data = json.load(file)

# Prompt

prompt_1 = f"""
    Summarize the text below, into a markdown format.
    Outline the business in this format.
    Business Name in Bold at the top.
    what they offer or what they do,
    who they are.
    text: {data[0]['company_desc']}
"""


#generate response
output = together.Complete.create(
  prompt=prompt_1,
  model="mistralai/Mixtral-8x7B-Instruct-v0.1",
  max_tokens = 250,
  temperature = 0.8,
)
# parse the completion then print the whole output
generatedText = output['output']['choices'][0]['text']

st.markdown(generatedText)
