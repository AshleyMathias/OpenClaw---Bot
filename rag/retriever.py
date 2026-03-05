from langchain_community.vectorstores import Chroma
from llm.openai_client import embeddings
import os


def get_retriever():
    # Check if vector store exists
    if not os.path.exists("vector_store"):
        return None
    
    try:
        vectorstore = Chroma(
            persist_directory="vector_store",
            embedding_function=embeddings
        )
        return vectorstore.as_retriever(search_kwargs={"k":3})
    except Exception as e:
        # If there's an error loading, return None
        print(f"Error loading vector store: {e}")
        return None