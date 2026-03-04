from pathlib import Path

from langchain_openai import OpenAIEmbeddings

try:
    from langchain_chroma import Chroma
except ModuleNotFoundError:
    from langchain_community.vectorstores import Chroma  # fallback if langchain-chroma not installed

# Same vector_db path as vector_store.py (project root / vector_db)
_VECTOR_DB_PATH = str(Path(__file__).resolve().parent.parent / "vector_db")


def get_retriever():
    embeddings = OpenAIEmbeddings()
    vector_store = Chroma(persist_directory=_VECTOR_DB_PATH, embedding_function=embeddings)
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    return retriever