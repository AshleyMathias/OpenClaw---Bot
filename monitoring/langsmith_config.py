import os
from langsmith import Client
from config.settings import LANGCHAIN_API_KEY

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "openclaw bot"
# Make sure LANGCHAIN_API_KEY is available in the environment for Client()
if LANGCHAIN_API_KEY:
    os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY

client = Client()