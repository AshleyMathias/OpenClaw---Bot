from pathlib import Path

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

# Paths relative to this file: rag/vector_store.py -> project root = parent.parent
_RAG_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _RAG_DIR.parent
POLICY_PATH = _RAG_DIR / "knoweldge" / "company_policy.txt"  # folder name has typo "knoweldge"
VECTOR_DB_PATH = str(_PROJECT_ROOT / "vector_db")


def create_vector_store():
    loader = TextLoader(str(POLICY_PATH))
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings()
    vector_store = Chroma.from_documents(docs, embeddings, persist_directory=VECTOR_DB_PATH)
    return vector_store

