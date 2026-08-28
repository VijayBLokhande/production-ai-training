import os
from dotenv import load_dotenv

# load environment variables from a .env file
load_dotenv()

# Read the API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")

# Validate that the API key exists
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables."
                    " Please set it in the .env file.")

# Create OPENAI client using the API key
from openai import OpenAI
client = OpenAI(api_key=api_key)

# Send a request to the OpenAI model
response = client.responses.create(
    model="gpt-5-mini",
    input="Explain what is generative ai in two simple sentences."
)

# Print the response from the model
print(response.output_text)