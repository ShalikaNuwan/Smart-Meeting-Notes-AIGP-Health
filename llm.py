# this file containes the LLM for the inference 
# add your credentials to use the LLM 
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AzureOpenAI(
    api_version=os.getenv('API_VERSION'),
    azure_endpoint=os.getenv('AZURE_ENDPOINT'),
    api_key=os.getenv('API_KEY'),
)

if __name__ == "__main__":
    response = client.chat.completions.create(
    messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant.",
            },
            {
                "role": "user",
                "content": "I am going to Paris, what should I see?",
            }
        ],
        max_tokens=4096,
        temperature=1.0,
        top_p=1.0,
        model=os.getenv('DEPLOYMENT'),
    )
    
    print(response.choices[0].message.content)
    