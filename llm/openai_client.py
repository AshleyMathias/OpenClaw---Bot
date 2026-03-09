from openai import OpenAI
import monitoring.langsmith_config
from config.settings import MODEL_NAME, TEMPERATURE, OPENAI_API_KEY
from langchain_openai import OpenAIEmbeddings

openai_client = OpenAI(api_key=OPENAI_API_KEY)

embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

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