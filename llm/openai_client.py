import os
from openai import OpenAI
from llm.prompts import System_Prompt
from dotenv import load_dotenv
import monitoring.langsmith_config
from config.settings import MODEL_NAME, TEMPERATURE

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_response(message):
    response = openai_client.chat.completions.create(
        model=MODEL_NAME,
        messages=message,
        temperature=TEMPERATURE,
        stream=True
    )
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content